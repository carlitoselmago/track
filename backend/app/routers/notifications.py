from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, and_, select

from app.db.session import get_session
from app.deps import get_current_user
from app.models import Notification, User
from app.services.notifications import serialize_notification


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_notifications(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    rows = session.exec(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc(), Notification.id.desc()),
    ).all()
    unread_count = sum(1 for row in rows if not row.is_read)
    return {
        "items": [serialize_notification(session, row) for row in rows],
        "unread_count": unread_count,
    }


@router.post("/read-all")
def mark_all_read(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    rows = session.exec(
        select(Notification).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read.is_(False),
            ),
        ),
    ).all()
    now = datetime.utcnow()
    for row in rows:
        row.is_read = True
        row.read_at = now
        session.add(row)
    session.commit()
    return {"success": True}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    row = session.get(Notification, notification_id)
    if not row or row.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    session.delete(row)
    session.commit()
    return {"success": True}


@router.delete("")
def clear_notifications(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    rows = session.exec(
        select(Notification).where(Notification.user_id == current_user.id),
    ).all()
    for row in rows:
        session.delete(row)
    session.commit()
    return {"success": True}

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, and_, select

from app.db.session import get_session
from app.deps import ensure_board_access, get_current_user
from app.models import Card, TimeSession, User


router = APIRouter(tags=["time-tracking"])


def _active_session_for_user(session: Session, user_id: int) -> TimeSession | None:
    return session.exec(
        select(TimeSession).where(
            and_(TimeSession.user_id == user_id, TimeSession.ended_at.is_(None)),
        ),
    ).first()


def _session_payload(row: TimeSession) -> dict:
    return {
        "id": row.id,
        "card_id": row.card_id,
        "user_id": row.user_id,
        "started_at": row.started_at,
        "ended_at": row.ended_at,
        "duration_seconds": row.duration_seconds,
    }


@router.post("/cards/{card_id}/timer/start")
def start_timer(
    card_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)

    active = _active_session_for_user(session, current_user.id)
    if active:
        if active.card_id == card_id:
            return {
                "session": _session_payload(active),
                "summary": {"total_seconds": card.total_tracked_seconds},
            }
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Another timer is already running",
        )

    row = TimeSession(
        card_id=card_id,
        user_id=current_user.id,
        started_at=datetime.utcnow(),
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return {
        "session": _session_payload(row),
        "summary": {"total_seconds": card.total_tracked_seconds},
    }


@router.post("/cards/{card_id}/timer/stop")
def stop_timer(
    card_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    active = _active_session_for_user(session, current_user.id)
    if not active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active timer")
    if active.card_id != card_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active timer belongs to another card",
        )

    now = datetime.utcnow()
    elapsed = int((now - active.started_at).total_seconds())
    active.ended_at = now
    active.duration_seconds = max(0, elapsed)
    card.total_tracked_seconds += active.duration_seconds
    card.updated_at = now
    session.add(active)
    session.add(card)
    session.commit()
    session.refresh(active)
    session.refresh(card)
    return {
        "session": _session_payload(active),
        "summary": {"total_seconds": card.total_tracked_seconds},
    }


@router.get("/cards/{card_id}/time")
def get_card_time(
    card_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    active = _active_session_for_user(session, current_user.id)
    if active and active.card_id != card_id:
        active = None
    return {
        "total_seconds": card.total_tracked_seconds,
        "active_session": _session_payload(active) if active else None,
    }


@router.get("/users/me/active-timer")
def get_active_timer(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    active = _active_session_for_user(session, current_user.id)
    return {"active_session": _session_payload(active) if active else None}


@router.get("/cards/{card_id}/time-sessions")
def get_time_sessions(
    card_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    rows = session.exec(
        select(TimeSession)
        .where(TimeSession.card_id == card_id)
        .order_by(TimeSession.started_at.desc(), TimeSession.id.desc()),
    ).all()
    return [_session_payload(row) for row in rows]

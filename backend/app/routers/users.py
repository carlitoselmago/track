from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, and_, select

from app.core.security import get_password_hash
from app.db.session import get_session
from app.deps import get_current_user, require_system_admin
from app.models import Board, BoardMembership, User
from app.schemas import (
    UserCreateRequest,
    UserEmailPreferenceUpdateRequest,
    UserPasswordChangeRequest,
)
from app.serializers import user_public
from app.services.email import send_email
from app.services.notifications import (
    create_notification,
    get_email_notifications_enabled,
    set_email_notifications_enabled,
)


router = APIRouter(prefix="/users", tags=["users"])


@router.post("", dependencies=[Depends(require_system_admin)])
def create_user(
    payload: UserCreateRequest,
    session: Session = Depends(get_session),
):
    email = payload.email.strip().lower()
    exists = session.exec(
        select(User).where(and_(User.email == email, User.deleted_at.is_(None))),
    ).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    full_name = payload.full_name.strip()
    if not full_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Full name is required")

    user = User(
        email=email,
        name=full_name,
        password_hash=get_password_hash(payload.password),
        is_system_admin=payload.is_system_admin,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    for board_id in payload.board_ids:
        board = session.get(Board, board_id)
        if not board or board.deleted_at is not None:
            continue
        existing_membership = session.exec(
            select(BoardMembership).where(
                and_(
                    BoardMembership.board_id == board_id,
                    BoardMembership.user_id == user.id,
                ),
            ),
        ).first()
        if not existing_membership:
            session.add(
                BoardMembership(
                    board_id=board_id,
                    user_id=user.id,
                    role="member",
                ),
            )
    session.commit()

    create_notification(
        session,
        user_id=user.id,
        type="user_created",
        title="Welcome to Track",
        message="Your user account has been created. You can now sign in.",
        send_email_copy=True,
    )
    return user_public(user)


@router.get("", dependencies=[Depends(require_system_admin)])
def list_users(session: Session = Depends(get_session)):
    users = session.exec(select(User).where(User.deleted_at.is_(None)).order_by(User.id)).all()
    return [user_public(user) for user in users]


@router.post("/{user_id}/deactivate", dependencies=[Depends(require_system_admin)])
def deactivate_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    user = session.get(User, user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = False
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    return {"success": True}


@router.get("/me/preferences/email-notifications")
def get_my_email_notifications_preference(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return {
        "email_notifications_enabled": get_email_notifications_enabled(session, current_user.id),
    }


@router.patch("/me/preferences/email-notifications")
def update_my_email_notifications_preference(
    payload: UserEmailPreferenceUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    pref = set_email_notifications_enabled(
        session,
        user_id=current_user.id,
        enabled=payload.email_notifications_enabled,
    )
    return {"email_notifications_enabled": pref.email_notifications_enabled}


@router.post("/me/password")
def change_my_password(
    payload: UserPasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    current_user.password_hash = get_password_hash(payload.new_password)
    current_user.updated_at = datetime.utcnow()
    session.add(current_user)
    session.commit()

    send_email(
        to_email=current_user.email,
        subject="Track: Password changed",
        body="Your Track account password was changed.",
    )
    return {"success": True}

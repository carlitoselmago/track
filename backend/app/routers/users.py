from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, and_, select

from app.core.security import get_password_hash
from app.db.session import get_session
from app.deps import require_system_admin
from app.models import User
from app.schemas import UserCreateRequest
from app.serializers import user_public


router = APIRouter(prefix="/users", tags=["users"])


@router.post("", dependencies=[Depends(require_system_admin)])
def create_user(
    payload: UserCreateRequest,
    session: Session = Depends(get_session),
):
    exists = session.exec(
        select(User).where(and_(User.email == payload.email, User.deleted_at.is_(None))),
    ).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=get_password_hash(payload.password),
        is_system_admin=payload.is_system_admin,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
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

from datetime import datetime

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, and_, select

from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_session
from app.models import Board, BoardMembership, RefreshToken, User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        ) from exc

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token type",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token payload",
        )

    user = session.get(User, int(user_id))
    if not user or not user.is_active or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not available",
        )
    return user


def require_system_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_system_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return user


def get_current_user_flexible(
    request: Request,
    token: str | None = Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)),
    session: Session = Depends(get_session),
) -> User:
    if token:
        try:
            payload = decode_token(token)
            if payload.get("type") == "access" and payload.get("sub"):
                user = session.get(User, int(payload["sub"]))
                if user and user.is_active and user.deleted_at is None:
                    return user
        except (ValueError, KeyError):
            pass

    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    if refresh_token:
        try:
            payload = decode_token(refresh_token)
        except ValueError:
            payload = {}
        if payload.get("type") == "refresh" and payload.get("jti") and payload.get("sub"):
            db_token = session.exec(
                select(RefreshToken).where(
                    and_(
                        RefreshToken.jti == payload["jti"],
                        RefreshToken.revoked_at.is_(None),
                    ),
                ),
            ).first()
            if db_token and db_token.expires_at >= datetime.utcnow():
                user = session.get(User, int(payload["sub"]))
                if user and user.is_active and user.deleted_at is None:
                    return user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


def ensure_board_access(
    board_id: int,
    user: User,
    session: Session,
    require_board_admin: bool = False,
) -> Board:
    board = session.get(Board, board_id)
    if not board or board.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")

    if user.is_system_admin:
        return board

    membership = session.exec(
        select(BoardMembership).where(
            and_(BoardMembership.board_id == board_id, BoardMembership.user_id == user.id),
        ),
    ).first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Board access denied")
    if require_board_admin and membership.role != "board_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Board admin required")
    return board

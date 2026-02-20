from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlmodel import Session, and_, select

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.db.session import get_session
from app.models import RefreshToken, User
from app.schemas import LoginRequest, TokenResponse
from app.serializers import user_public


router = APIRouter(prefix="/auth", tags=["auth"])


def _set_refresh_cookie(response: Response, token: str) -> None:
    max_age = settings.refresh_token_expire_days * 24 * 60 * 60
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=max_age,
        path="/",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=settings.refresh_cookie_name, path="/")


def _get_user_by_refresh_token(session: Session, refresh_token: str | None) -> User | None:
    if not refresh_token:
        return None
    try:
        payload = decode_token(refresh_token)
    except ValueError:
        return None

    if payload.get("type") != "refresh":
        return None

    jti = payload.get("jti")
    user_id = payload.get("sub")
    if not jti or not user_id:
        return None

    db_token = session.exec(
        select(RefreshToken).where(
            and_(
                RefreshToken.jti == jti,
                RefreshToken.revoked_at.is_(None),
            ),
        ),
    ).first()
    if not db_token or db_token.expires_at < datetime.utcnow():
        return None

    user = session.get(User, int(user_id))
    if not user or not user.is_active or user.deleted_at is not None:
        return None
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    response: Response,
    session: Session = Depends(get_session),
):
    login_email = payload.email.strip().lower()
    user = session.exec(
        select(User).where(and_(User.email == login_email, User.deleted_at.is_(None))),
    ).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    access_token = create_access_token(str(user.id))
    refresh_token, jti, expires_at = create_refresh_token(str(user.id))
    session.add(RefreshToken(user_id=user.id, jti=jti, expires_at=expires_at))
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()

    _set_refresh_cookie(response, refresh_token)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_public(user),
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
):
    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")
    try:
        payload = decode_token(refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from exc

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    jti = payload.get("jti")
    sub = payload.get("sub")
    if not jti or not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh payload")

    db_token = session.exec(
        select(RefreshToken).where(
            and_(
                RefreshToken.jti == jti,
                RefreshToken.revoked_at.is_(None),
            ),
        ),
    ).first()
    if not db_token or db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    user = session.get(User, int(sub))
    if not user or not user.is_active or user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User unavailable")

    db_token.revoked_at = datetime.utcnow()
    session.add(db_token)

    new_refresh_token, new_jti, new_expires_at = create_refresh_token(str(user.id))
    session.add(RefreshToken(user_id=user.id, jti=new_jti, expires_at=new_expires_at))
    access_token = create_access_token(str(user.id))
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()

    _set_refresh_cookie(response, new_refresh_token)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_public(user),
    }


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
):
    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            jti = payload.get("jti")
            if jti:
                db_token = session.exec(
                    select(RefreshToken).where(
                        and_(
                            RefreshToken.jti == jti,
                            RefreshToken.revoked_at.is_(None),
                        ),
                    ),
                ).first()
                if db_token:
                    db_token.revoked_at = datetime.utcnow()
                    session.add(db_token)
                    session.commit()
        except ValueError:
            pass

    _clear_refresh_cookie(response)
    return {"success": True}


@router.get("/me")
def me(
    request: Request,
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
):
    user: User | None = None

    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
        try:
            payload = decode_token(token)
            if payload.get("type") == "access":
                user = session.get(User, int(payload["sub"]))
        except (ValueError, KeyError):
            user = None

    if not user:
        user = _get_user_by_refresh_token(
            session,
            request.cookies.get(settings.refresh_cookie_name),
        )

    if not user or not user.is_active or user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return user_public(user)

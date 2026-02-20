from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _build_payload(
    *,
    subject: str,
    expires_delta: timedelta,
    token_type: str,
    jti: str | None = None,
) -> dict[str, Any]:
    now = datetime.utcnow()
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "type": token_type,
    }
    if jti:
        payload["jti"] = jti
    return payload


def create_access_token(subject: str) -> str:
    payload = _build_payload(
        subject=subject,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        token_type="access",
    )
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str) -> tuple[str, str, datetime]:
    expires_delta = timedelta(days=settings.refresh_token_expire_days)
    expires_at = datetime.utcnow() + expires_delta
    jti = str(uuid4())
    payload = _build_payload(
        subject=subject,
        expires_delta=expires_delta,
        token_type="refresh",
        jti=jti,
    )
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token, jti, expires_at


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

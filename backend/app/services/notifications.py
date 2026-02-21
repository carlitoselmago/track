from __future__ import annotations

from datetime import datetime
import json

from sqlmodel import Session, and_, select

from app.models import Notification, User, UserNotificationPreference
from app.serializers import user_public
from app.services.email import send_email


def get_email_notifications_enabled(session: Session, user_id: int) -> bool:
    pref = session.exec(
        select(UserNotificationPreference).where(UserNotificationPreference.user_id == user_id),
    ).first()
    if not pref:
        return True
    return bool(pref.email_notifications_enabled)


def set_email_notifications_enabled(
    session: Session,
    *,
    user_id: int,
    enabled: bool,
) -> UserNotificationPreference:
    pref = session.exec(
        select(UserNotificationPreference).where(UserNotificationPreference.user_id == user_id),
    ).first()
    now = datetime.utcnow()
    if pref:
        pref.email_notifications_enabled = enabled
        pref.updated_at = now
    else:
        pref = UserNotificationPreference(
            user_id=user_id,
            email_notifications_enabled=enabled,
            created_at=now,
            updated_at=now,
        )
    session.add(pref)
    session.commit()
    session.refresh(pref)
    return pref


def create_notification(
    session: Session,
    *,
    user_id: int,
    type: str,
    title: str,
    message: str,
    actor_user_id: int | None = None,
    data: dict | None = None,
    send_email_copy: bool = True,
) -> Notification:
    row = Notification(
        user_id=user_id,
        actor_user_id=actor_user_id,
        type=type,
        title=title,
        message=message,
        data_json=json.dumps(data) if data else None,
        is_read=False,
    )
    session.add(row)
    session.commit()
    session.refresh(row)

    if send_email_copy and get_email_notifications_enabled(session, user_id):
        user = session.get(User, user_id)
        if user and user.deleted_at is None and user.is_active:
            send_email(
                to_email=user.email,
                subject=f"Track: {title}",
                body=message,
            )

    return row


def serialize_notification(session: Session, row: Notification) -> dict:
    actor_payload = None
    if row.actor_user_id:
        actor = session.exec(
            select(User).where(and_(User.id == row.actor_user_id, User.deleted_at.is_(None))),
        ).first()
        if actor:
            actor_payload = user_public(actor)

    data_payload = None
    if row.data_json:
        try:
            data_payload = json.loads(row.data_json)
        except json.JSONDecodeError:
            data_payload = None

    return {
        "id": row.id,
        "type": row.type,
        "title": row.title,
        "message": row.message,
        "is_read": row.is_read,
        "created_at": row.created_at,
        "actor_user": actor_payload,
        "data": data_payload,
    }

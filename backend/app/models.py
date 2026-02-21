from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Index, UniqueConstraint, text
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.utcnow()


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    name: str = Field(max_length=120)
    password_hash: str = Field(max_length=255)
    is_system_admin: bool = Field(default=False, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"
    __table_args__ = (UniqueConstraint("jti", name="uq_refresh_tokens_jti"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    jti: str = Field(max_length=120, index=True)
    expires_at: datetime = Field(nullable=False)
    revoked_at: Optional[datetime] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class Board(SQLModel, table=True):
    __tablename__ = "boards"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=120)
    description: Optional[str] = Field(default=None)
    color_hex: str = Field(default="#16A34A", max_length=7)
    created_by_user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


class BoardMembership(SQLModel, table=True):
    __tablename__ = "board_memberships"
    __table_args__ = (
        UniqueConstraint("board_id", "user_id", name="uq_board_memberships_board_user"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="boards.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    role: str = Field(default="member", max_length=20)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class BoardList(SQLModel, table=True):
    __tablename__ = "lists"

    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="boards.id", index=True)
    title: str = Field(max_length=120)
    position: float = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


class CardLabel(SQLModel, table=True):
    __tablename__ = "card_labels"
    __table_args__ = (UniqueConstraint("card_id", "label_id", name="uq_card_label"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    card_id: int = Field(foreign_key="cards.id", index=True)
    label_id: int = Field(foreign_key="labels.id", index=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class CardAssignee(SQLModel, table=True):
    __tablename__ = "card_assignees"
    __table_args__ = (UniqueConstraint("card_id", "user_id", name="uq_card_assignee"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    card_id: int = Field(foreign_key="cards.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    assigned_by_user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class Card(SQLModel, table=True):
    __tablename__ = "cards"

    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="boards.id", index=True)
    list_id: int = Field(foreign_key="lists.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None)
    position: float = Field(default=0, nullable=False)
    cover_image_id: Optional[int] = Field(default=None, foreign_key="card_images.id")
    total_tracked_seconds: int = Field(default=0, nullable=False)
    created_by_user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


class Label(SQLModel, table=True):
    __tablename__ = "labels"
    __table_args__ = (
        UniqueConstraint("board_id", "name", name="uq_labels_board_name"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="boards.id", index=True)
    name: str = Field(max_length=80)
    color_hex: str = Field(default="#16A34A", max_length=7)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


class Checklist(SQLModel, table=True):
    __tablename__ = "checklists"

    id: Optional[int] = Field(default=None, primary_key=True)
    card_id: int = Field(foreign_key="cards.id", index=True)
    title: str = Field(max_length=120)
    position: float = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


class ChecklistItem(SQLModel, table=True):
    __tablename__ = "checklist_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    checklist_id: int = Field(foreign_key="checklists.id", index=True)
    content: str = Field(max_length=500)
    is_done: bool = Field(default=False, nullable=False)
    position: float = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


class CardImage(SQLModel, table=True):
    __tablename__ = "card_images"

    id: Optional[int] = Field(default=None, primary_key=True)
    card_id: int = Field(foreign_key="cards.id", index=True)
    storage_path: str = Field(max_length=500)
    original_filename: str = Field(max_length=255)
    mime_type: str = Field(max_length=120)
    size_bytes: int = Field(default=0, nullable=False)
    uploaded_by_user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


class TimeSession(SQLModel, table=True):
    __tablename__ = "time_sessions"
    __table_args__ = (
        Index(
            "uq_time_sessions_user_active",
            "user_id",
            unique=True,
            sqlite_where=text("ended_at IS NULL"),
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    card_id: int = Field(foreign_key="cards.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    started_at: datetime = Field(default_factory=utcnow, nullable=False)
    ended_at: Optional[datetime] = Field(default=None, nullable=True)
    duration_seconds: Optional[int] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    actor_user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    type: str = Field(max_length=80)
    title: str = Field(max_length=200)
    message: str = Field(max_length=1000)
    data_json: Optional[str] = Field(default=None)
    is_read: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    read_at: Optional[datetime] = Field(default=None, nullable=True)


class UserNotificationPreference(SQLModel, table=True):
    __tablename__ = "user_notification_preferences"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_notification_pref_user"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    email_notifications_enabled: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)

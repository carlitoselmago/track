from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


BoardRole = Literal["board_admin", "member"]


class UserPublic(BaseModel):
    id: int
    email: str
    name: str
    is_system_admin: bool
    is_active: bool


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class UserCreateRequest(BaseModel):
    email: str
    name: str
    password: str = Field(min_length=8)
    is_system_admin: bool = False


class BoardCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    color_hex: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class BoardUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color_hex: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class BoardMemberCreateRequest(BaseModel):
    user_id: int
    role: BoardRole = "member"


class BoardMemberUpdateRequest(BaseModel):
    role: BoardRole


class ListCreateRequest(BaseModel):
    title: str


class ListUpdateRequest(BaseModel):
    title: Optional[str] = None
    position: Optional[float] = None


class ReorderItem(BaseModel):
    id: int
    position: float


class ReorderListsRequest(BaseModel):
    lists: list[ReorderItem]


class CardCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None


class CardUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    position: Optional[float] = None
    list_id: Optional[int] = None


class MoveCardRequest(BaseModel):
    list_id: int
    position: float = 0


class ReorderCardsRequest(BaseModel):
    cards: list[ReorderItem]


class ChecklistCreateRequest(BaseModel):
    title: str


class ChecklistUpdateRequest(BaseModel):
    title: Optional[str] = None
    position: Optional[float] = None


class ChecklistItemCreateRequest(BaseModel):
    content: str


class ChecklistItemUpdateRequest(BaseModel):
    content: Optional[str] = None
    is_done: Optional[bool] = None
    position: Optional[float] = None


class LabelCreateRequest(BaseModel):
    name: str
    color_hex: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")


class LabelUpdateRequest(BaseModel):
    name: Optional[str] = None
    color_hex: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class ChecklistItemResponse(BaseModel):
    id: int
    checklist_id: int
    content: str
    is_done: bool
    position: float


class ChecklistResponse(BaseModel):
    id: int
    card_id: int
    title: str
    position: float
    items: list[ChecklistItemResponse]


class LabelResponse(BaseModel):
    id: int
    board_id: int
    name: str
    color_hex: str


class CardImageResponse(BaseModel):
    id: int
    card_id: int
    original_filename: str
    mime_type: str
    size_bytes: int
    created_at: datetime


class CardResponse(BaseModel):
    id: int
    board_id: int
    list_id: int
    title: str
    description: Optional[str]
    position: float
    cover_image_id: Optional[int]
    total_tracked_seconds: int
    labels: list[LabelResponse]
    checklists: list[ChecklistResponse]
    images: list[CardImageResponse]


class ListResponse(BaseModel):
    id: int
    board_id: int
    title: str
    position: float
    cards: list[CardResponse]


class BoardResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color_hex: str
    labels: list[LabelResponse]
    lists: list[ListResponse]


class BoardSummaryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color_hex: str


class TimeSessionResponse(BaseModel):
    id: int
    card_id: int
    user_id: int
    started_at: datetime
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]


class CardTimeSummaryResponse(BaseModel):
    total_seconds: int
    active_session: Optional[TimeSessionResponse] = None

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session, and_, select

from app.core.config import settings
from app.db.session import get_session
from app.deps import ensure_board_access, get_current_user, get_current_user_flexible
from app.models import Card, CardImage, User
from app.serializers import card_image_payload


router = APIRouter(tags=["images"])


def _ensure_card(card_id: int, user: User, session: Session) -> Card:
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=user, session=session)
    return card


def _fallback_cover_id(session: Session, card_id: int) -> int | None:
    latest = session.exec(
        select(CardImage)
        .where(and_(CardImage.card_id == card_id, CardImage.deleted_at.is_(None)))
        .order_by(CardImage.created_at.desc(), CardImage.id.desc()),
    ).first()
    return latest.id if latest else None


@router.post("/cards/{card_id}/images")
async def upload_card_image(
    card_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = _ensure_card(card_id, current_user, session)
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only image files are allowed")

    card_dir = settings.upload_dir / str(card.id)
    card_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "").suffix or ".bin"
    filename = f"{uuid4().hex}{suffix}"
    file_path = card_dir / filename

    content = await file.read()
    file_path.write_bytes(content)

    image = CardImage(
        card_id=card.id,
        storage_path=str(file_path.resolve()),
        original_filename=file.filename or filename,
        mime_type=file.content_type,
        size_bytes=len(content),
        uploaded_by_user_id=current_user.id,
    )
    session.add(image)
    session.commit()
    session.refresh(image)

    card.cover_image_id = image.id
    card.updated_at = datetime.utcnow()
    session.add(card)
    session.commit()
    return card_image_payload(image)


@router.get("/cards/{card_id}/images")
def list_card_images(
    card_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _ensure_card(card_id, current_user, session)
    images = session.exec(
        select(CardImage)
        .where(and_(CardImage.card_id == card_id, CardImage.deleted_at.is_(None)))
        .order_by(CardImage.created_at, CardImage.id),
    ).all()
    return [card_image_payload(image) for image in images]


@router.get("/images/{image_id}/content")
def get_image_content(
    image_id: int,
    current_user: User = Depends(get_current_user_flexible),
    session: Session = Depends(get_session),
):
    image = session.get(CardImage, image_id)
    if not image or image.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    card = _ensure_card(image.card_id, current_user, session)
    file_path = Path(image.storage_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image file is missing")
    return FileResponse(path=file_path, media_type=image.mime_type, filename=image.original_filename)


@router.delete("/images/{image_id}")
def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    image = session.get(CardImage, image_id)
    if not image or image.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    card = _ensure_card(image.card_id, current_user, session)

    file_path = Path(image.storage_path)
    if file_path.exists():
        file_path.unlink(missing_ok=True)

    image.deleted_at = datetime.utcnow()
    session.add(image)

    if card.cover_image_id == image_id:
        card.cover_image_id = _fallback_cover_id(session, card.id)
        card.updated_at = datetime.utcnow()
        session.add(card)

    session.commit()
    return {"success": True}


@router.post("/cards/{card_id}/cover/{image_id}")
def set_card_cover(
    card_id: int,
    image_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = _ensure_card(card_id, current_user, session)
    image = session.get(CardImage, image_id)
    if not image or image.deleted_at is not None or image.card_id != card.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    card.cover_image_id = image.id
    card.updated_at = datetime.utcnow()
    session.add(card)
    session.commit()
    return {"success": True}

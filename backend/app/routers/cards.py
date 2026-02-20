from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, and_, select

from app.db.session import get_session
from app.deps import ensure_board_access, get_current_user
from app.models import BoardList, Card, CardImage, User
from app.schemas import CardCreateRequest, CardUpdateRequest, MoveCardRequest, ReorderCardsRequest
from app.serializers import card_payload


router = APIRouter(tags=["cards"])


def _delete_card_image_files(images: list[CardImage]) -> None:
    for image in images:
        path = Path(image.storage_path)
        if path.exists():
            path.unlink(missing_ok=True)


@router.post("/lists/{list_id}/cards")
def create_card(
    list_id: int,
    payload: CardCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    board_list = session.get(BoardList, list_id)
    if not board_list or board_list.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    ensure_board_access(board_id=board_list.board_id, user=current_user, session=session)

    max_pos = session.exec(
        select(Card.position)
        .where(and_(Card.list_id == list_id, Card.deleted_at.is_(None)))
        .order_by(Card.position.desc()),
    ).first()
    next_position = float(max_pos + 1) if max_pos is not None else 0.0

    card = Card(
        board_id=board_list.board_id,
        list_id=list_id,
        title=payload.title,
        description=payload.description,
        position=next_position,
        created_by_user_id=current_user.id,
    )
    session.add(card)
    session.commit()
    session.refresh(card)
    return card_payload(session, card)


@router.get("/cards/{card_id}")
def get_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    return card_payload(session, card)


@router.patch("/cards/{card_id}")
def update_card(
    card_id: int,
    payload: CardUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    if payload.title is not None:
        card.title = payload.title
    if payload.description is not None:
        card.description = payload.description
    if payload.position is not None:
        card.position = payload.position
    if payload.list_id is not None:
        target_list = session.get(BoardList, payload.list_id)
        if not target_list or target_list.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target list not found")
        if target_list.board_id != card.board_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot move to another board")
        card.list_id = payload.list_id
    card.updated_at = datetime.utcnow()
    session.add(card)
    session.commit()
    session.refresh(card)
    return card_payload(session, card)


@router.delete("/cards/{card_id}")
def delete_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)

    now = datetime.utcnow()
    card.deleted_at = now
    card.updated_at = now
    session.add(card)

    images = session.exec(
        select(CardImage).where(and_(CardImage.card_id == card.id, CardImage.deleted_at.is_(None))),
    ).all()
    _delete_card_image_files(images)
    for image in images:
        image.deleted_at = now
        session.add(image)

    session.commit()
    return {"success": True}


@router.post("/cards/{card_id}/move")
def move_card(
    card_id: int,
    payload: MoveCardRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)

    board_list = session.get(BoardList, payload.list_id)
    if not board_list or board_list.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    if board_list.board_id != card.board_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid target list")

    card.list_id = payload.list_id
    card.position = payload.position
    card.updated_at = datetime.utcnow()
    session.add(card)
    session.commit()
    session.refresh(card)
    return card_payload(session, card)


@router.post("/lists/{list_id}/cards/reorder")
def reorder_cards(
    list_id: int,
    payload: ReorderCardsRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    board_list = session.get(BoardList, list_id)
    if not board_list or board_list.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    ensure_board_access(board_id=board_list.board_id, user=current_user, session=session)
    for item in payload.cards:
        card = session.get(Card, item.id)
        if not card or card.deleted_at is not None or card.list_id != list_id:
            continue
        card.position = item.position
        card.updated_at = datetime.utcnow()
        session.add(card)
    session.commit()
    return {"success": True}

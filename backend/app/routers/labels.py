from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, and_, select

from app.db.session import get_session
from app.deps import ensure_board_access, get_current_user
from app.models import Board, Card, CardLabel, Label, User
from app.schemas import LabelCreateRequest, LabelUpdateRequest
from app.serializers import label_payload


router = APIRouter(tags=["labels"])


@router.post("/boards/{board_id}/labels")
def create_label(
    board_id: int,
    payload: LabelCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    ensure_board_access(board_id=board_id, user=current_user, session=session)
    existing = session.exec(
        select(Label).where(
            and_(
                Label.board_id == board_id,
                Label.name == payload.name,
                Label.deleted_at.is_(None),
            ),
        ),
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Label name already exists")
    label = Label(board_id=board_id, name=payload.name, color_hex=payload.color_hex)
    session.add(label)
    session.commit()
    session.refresh(label)
    return label_payload(label)


@router.get("/boards/{board_id}/labels")
def list_board_labels(
    board_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    ensure_board_access(board_id=board_id, user=current_user, session=session)
    labels = session.exec(
        select(Label)
        .where(and_(Label.board_id == board_id, Label.deleted_at.is_(None)))
        .order_by(Label.id),
    ).all()
    return [label_payload(label) for label in labels]


@router.patch("/labels/{label_id}")
def update_label(
    label_id: int,
    payload: LabelUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    label = session.get(Label, label_id)
    if not label or label.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")
    ensure_board_access(board_id=label.board_id, user=current_user, session=session)
    if payload.name is not None:
        label.name = payload.name
    if payload.color_hex is not None:
        label.color_hex = payload.color_hex
    label.updated_at = datetime.utcnow()
    session.add(label)
    session.commit()
    session.refresh(label)
    return label_payload(label)


@router.delete("/labels/{label_id}")
def delete_label(
    label_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    label = session.get(Label, label_id)
    if not label or label.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")
    ensure_board_access(board_id=label.board_id, user=current_user, session=session)
    label.deleted_at = datetime.utcnow()
    label.updated_at = datetime.utcnow()
    session.add(label)
    session.commit()
    return {"success": True}


@router.post("/cards/{card_id}/labels/{label_id}")
def assign_label(
    card_id: int,
    label_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    label = session.get(Label, label_id)
    if not label or label.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    if label.board_id != card.board_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Label belongs to another board")
    existing = session.exec(
        select(CardLabel).where(
            and_(CardLabel.card_id == card_id, CardLabel.label_id == label_id),
        ),
    ).first()
    if not existing:
        session.add(CardLabel(card_id=card_id, label_id=label_id))
        session.commit()
    return {"success": True}


@router.delete("/cards/{card_id}/labels/{label_id}")
def unassign_label(
    card_id: int,
    label_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    existing = session.exec(
        select(CardLabel).where(
            and_(CardLabel.card_id == card_id, CardLabel.label_id == label_id),
        ),
    ).first()
    if existing:
        session.delete(existing)
        session.commit()
    return {"success": True}

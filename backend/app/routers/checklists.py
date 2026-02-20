from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, and_, select

from app.db.session import get_session
from app.deps import ensure_board_access, get_current_user
from app.models import Card, Checklist, ChecklistItem, User
from app.schemas import (
    ChecklistCreateRequest,
    ChecklistItemCreateRequest,
    ChecklistItemUpdateRequest,
    ChecklistUpdateRequest,
)
from app.serializers import checklist_item_payload, checklist_payload


router = APIRouter(tags=["checklists"])


@router.post("/cards/{card_id}/checklists")
def create_checklist(
    card_id: int,
    payload: ChecklistCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    max_pos = session.exec(
        select(Checklist.position)
        .where(and_(Checklist.card_id == card_id, Checklist.deleted_at.is_(None)))
        .order_by(Checklist.position.desc()),
    ).first()
    checklist = Checklist(
        card_id=card_id,
        title=payload.title,
        position=float(max_pos + 1) if max_pos is not None else 0.0,
    )
    session.add(checklist)
    session.commit()
    session.refresh(checklist)
    return checklist_payload(session, checklist)


@router.patch("/checklists/{checklist_id}")
def update_checklist(
    checklist_id: int,
    payload: ChecklistUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    checklist = session.get(Checklist, checklist_id)
    if not checklist or checklist.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")
    card = session.get(Card, checklist.card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    if payload.title is not None:
        checklist.title = payload.title
    if payload.position is not None:
        checklist.position = payload.position
    checklist.updated_at = datetime.utcnow()
    session.add(checklist)
    session.commit()
    session.refresh(checklist)
    return checklist_payload(session, checklist)


@router.delete("/checklists/{checklist_id}")
def delete_checklist(
    checklist_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    checklist = session.get(Checklist, checklist_id)
    if not checklist or checklist.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")
    card = session.get(Card, checklist.card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    now = datetime.utcnow()
    checklist.deleted_at = now
    checklist.updated_at = now
    session.add(checklist)
    items = session.exec(
        select(ChecklistItem).where(
            and_(ChecklistItem.checklist_id == checklist.id, ChecklistItem.deleted_at.is_(None)),
        ),
    ).all()
    for item in items:
        item.deleted_at = now
        item.updated_at = now
        session.add(item)
    session.commit()
    return {"success": True}


@router.post("/checklists/{checklist_id}/items")
def create_checklist_item(
    checklist_id: int,
    payload: ChecklistItemCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    checklist = session.get(Checklist, checklist_id)
    if not checklist or checklist.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")
    card = session.get(Card, checklist.card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    max_pos = session.exec(
        select(ChecklistItem.position)
        .where(
            and_(
                ChecklistItem.checklist_id == checklist_id,
                ChecklistItem.deleted_at.is_(None),
            ),
        )
        .order_by(ChecklistItem.position.desc()),
    ).first()
    item = ChecklistItem(
        checklist_id=checklist_id,
        content=payload.content,
        position=float(max_pos + 1) if max_pos is not None else 0.0,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return checklist_item_payload(item)


@router.patch("/checklist-items/{item_id}")
def update_checklist_item(
    item_id: int,
    payload: ChecklistItemUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    item = session.get(ChecklistItem, item_id)
    if not item or item.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist item not found")
    checklist = session.get(Checklist, item.checklist_id)
    if not checklist or checklist.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")
    card = session.get(Card, checklist.card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    if payload.content is not None:
        item.content = payload.content
    if payload.is_done is not None:
        item.is_done = payload.is_done
    if payload.position is not None:
        item.position = payload.position
    item.updated_at = datetime.utcnow()
    session.add(item)
    session.commit()
    session.refresh(item)
    return checklist_item_payload(item)


@router.delete("/checklist-items/{item_id}")
def delete_checklist_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    item = session.get(ChecklistItem, item_id)
    if not item or item.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist item not found")
    checklist = session.get(Checklist, item.checklist_id)
    if not checklist or checklist.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")
    card = session.get(Card, checklist.card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    item.deleted_at = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    session.add(item)
    session.commit()
    return {"success": True}

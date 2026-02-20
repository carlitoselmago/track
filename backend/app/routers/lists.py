from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, and_, select

from app.db.session import get_session
from app.deps import ensure_board_access, get_current_user
from app.models import BoardList, Card, User
from app.schemas import ListCreateRequest, ListUpdateRequest, ReorderListsRequest
from app.serializers import list_payload


router = APIRouter(tags=["lists"])


@router.post("/boards/{board_id}/lists")
def create_list(
    board_id: int,
    payload: ListCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    ensure_board_access(board_id=board_id, user=current_user, session=session)
    max_pos = session.exec(
        select(BoardList.position)
        .where(and_(BoardList.board_id == board_id, BoardList.deleted_at.is_(None)))
        .order_by(BoardList.position.desc()),
    ).first()
    next_position = float(max_pos + 1) if max_pos is not None else 0.0

    board_list = BoardList(board_id=board_id, title=payload.title, position=next_position)
    session.add(board_list)
    session.commit()
    session.refresh(board_list)
    return list_payload(session, board_list)


@router.patch("/lists/{list_id}")
def update_list(
    list_id: int,
    payload: ListUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    board_list = session.get(BoardList, list_id)
    if not board_list or board_list.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    ensure_board_access(board_id=board_list.board_id, user=current_user, session=session)
    if payload.title is not None:
        board_list.title = payload.title
    if payload.position is not None:
        board_list.position = payload.position
    board_list.updated_at = datetime.utcnow()
    session.add(board_list)
    session.commit()
    session.refresh(board_list)
    return list_payload(session, board_list)


@router.delete("/lists/{list_id}")
def delete_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    board_list = session.get(BoardList, list_id)
    if not board_list or board_list.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    ensure_board_access(board_id=board_list.board_id, user=current_user, session=session)

    now = datetime.utcnow()
    board_list.deleted_at = now
    board_list.updated_at = now
    session.add(board_list)

    cards = session.exec(
        select(Card).where(and_(Card.list_id == list_id, Card.deleted_at.is_(None))),
    ).all()
    for card in cards:
        card.deleted_at = now
        card.updated_at = now
        session.add(card)

    session.commit()
    return {"success": True}


@router.post("/boards/{board_id}/lists/reorder")
def reorder_lists(
    board_id: int,
    payload: ReorderListsRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    ensure_board_access(board_id=board_id, user=current_user, session=session)
    for item in payload.lists:
        board_list = session.get(BoardList, item.id)
        if not board_list or board_list.deleted_at is not None or board_list.board_id != board_id:
            continue
        board_list.position = item.position
        board_list.updated_at = datetime.utcnow()
        session.add(board_list)
    session.commit()
    return {"success": True}

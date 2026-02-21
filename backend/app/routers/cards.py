from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, and_, select

from app.db.session import get_session
from app.deps import ensure_board_access, get_current_user
from app.models import BoardList, BoardMembership, Card, CardAssignee, CardImage, User
from app.schemas import (
    CardAssigneeAssignRequest,
    CardCreateRequest,
    CardUpdateRequest,
    MoveCardRequest,
    ReorderCardsRequest,
)
from app.serializers import card_payload, user_public
from app.services.notifications import create_notification


router = APIRouter(tags=["cards"])


def _delete_card_image_files(images: list[CardImage]) -> None:
    for image in images:
        path = Path(image.storage_path)
        if path.exists():
            path.unlink(missing_ok=True)


def _get_assignee_user_ids(session: Session, card_id: int) -> list[int]:
    rows = session.exec(
        select(CardAssignee).where(CardAssignee.card_id == card_id),
    ).all()
    return [row.user_id for row in rows]


def _notify_card_assignment(
    *,
    session: Session,
    card: Card,
    assigned_user_id: int,
    actor_user: User,
) -> None:
    if assigned_user_id == actor_user.id:
        return
    create_notification(
        session,
        user_id=assigned_user_id,
        actor_user_id=actor_user.id,
        type="card_assigned",
        title="You were assigned to a card",
        message=f'{actor_user.name} assigned you to "{card.title}".',
        data={"card_id": card.id, "board_id": card.board_id},
    )


def _notify_card_moved(
    *,
    session: Session,
    card: Card,
    from_list: BoardList,
    to_list: BoardList,
    actor_user: User,
) -> None:
    assignee_user_ids = _get_assignee_user_ids(session, card.id)
    for user_id in assignee_user_ids:
        create_notification(
            session,
            user_id=user_id,
            actor_user_id=actor_user.id,
            type="card_moved",
            title="Card moved",
            message=(
                f'"{card.title}" was moved from "{from_list.title}" '
                f'to "{to_list.title}" by {actor_user.name}.'
            ),
            data={
                "card_id": card.id,
                "board_id": card.board_id,
                "from_list_id": from_list.id,
                "to_list_id": to_list.id,
            },
        )


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


@router.get("/cards/{card_id}/assignees")
def list_card_assignees(
    card_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    users = session.exec(
        select(User)
        .join(CardAssignee, CardAssignee.user_id == User.id)
        .where(
            and_(
                CardAssignee.card_id == card_id,
                User.deleted_at.is_(None),
            ),
        )
        .order_by(User.name, User.id),
    ).all()
    return [user_public(user) for user in users]


@router.post("/cards/{card_id}/assignees")
def assign_card_user(
    card_id: int,
    payload: CardAssigneeAssignRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)

    target_user = session.get(User, payload.user_id)
    if not target_user or target_user.deleted_at is not None or not target_user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    membership = session.exec(
        select(BoardMembership).where(
            and_(
                BoardMembership.board_id == card.board_id,
                BoardMembership.user_id == payload.user_id,
            ),
        ),
    ).first()
    if not membership and not target_user.is_system_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be a board member before card assignment",
        )

    existing = session.exec(
        select(CardAssignee).where(
            and_(CardAssignee.card_id == card_id, CardAssignee.user_id == payload.user_id),
        ),
    ).first()
    created = False
    if not existing:
        existing = CardAssignee(
            card_id=card_id,
            user_id=payload.user_id,
            assigned_by_user_id=current_user.id,
        )
        session.add(existing)
        session.commit()
        created = True
    if created:
        _notify_card_assignment(
            session=session,
            card=card,
            assigned_user_id=payload.user_id,
            actor_user=current_user,
        )
    return {"success": True}


@router.delete("/cards/{card_id}/assignees/{user_id}")
def unassign_card_user(
    card_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)

    existing = session.exec(
        select(CardAssignee).where(and_(CardAssignee.card_id == card_id, CardAssignee.user_id == user_id)),
    ).first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee not found")
    session.delete(existing)
    session.commit()
    return {"success": True}


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
    source_list = session.get(BoardList, card.list_id)
    list_changed = False
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
        list_changed = card.list_id != payload.list_id
        card.list_id = payload.list_id
    card.updated_at = datetime.utcnow()
    session.add(card)
    session.commit()
    session.refresh(card)
    if list_changed and source_list:
        target_list = session.get(BoardList, card.list_id)
        if target_list:
            _notify_card_moved(
                session=session,
                card=card,
                from_list=source_list,
                to_list=target_list,
                actor_user=current_user,
            )
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

    source_list = session.get(BoardList, card.list_id)
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
    if source_list and source_list.id != board_list.id:
        _notify_card_moved(
            session=session,
            card=card,
            from_list=source_list,
            to_list=board_list,
            actor_user=current_user,
        )
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

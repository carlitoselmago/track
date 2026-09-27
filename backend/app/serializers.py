from sqlalchemy import func
from sqlmodel import Session, and_, select

from app.models import (
    Board,
    BoardList,
    CardAssignee,
    Card,
    CardImage,
    CardLabel,
    Checklist,
    ChecklistItem,
    Label,
    User,
)


def user_public(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.name,
        "name": user.name,
        "is_system_admin": user.is_system_admin,
        "is_active": user.is_active,
    }


def label_payload(label: Label) -> dict:
    return {
        "id": label.id,
        "board_id": label.board_id,
        "name": label.name,
        "color_hex": label.color_hex,
    }


def checklist_item_payload(item: ChecklistItem) -> dict:
    return {
        "id": item.id,
        "checklist_id": item.checklist_id,
        "content": item.content,
        "is_done": item.is_done,
        "position": item.position,
    }


def checklist_payload(session: Session, checklist: Checklist) -> dict:
    items = session.exec(
        select(ChecklistItem)
        .where(
            and_(
                ChecklistItem.checklist_id == checklist.id,
                ChecklistItem.deleted_at.is_(None),
            ),
        )
        .order_by(ChecklistItem.position, ChecklistItem.id),
    ).all()
    return {
        "id": checklist.id,
        "card_id": checklist.card_id,
        "title": checklist.title,
        "position": checklist.position,
        "items": [checklist_item_payload(item) for item in items],
    }


def card_image_payload(image: CardImage) -> dict:
    return {
        "id": image.id,
        "card_id": image.card_id,
        "original_filename": image.original_filename,
        "mime_type": image.mime_type,
        "size_bytes": image.size_bytes,
        "created_at": image.created_at,
    }


def card_payload(session: Session, card: Card) -> dict:
    labels = session.exec(
        select(Label)
        .join(CardLabel, CardLabel.label_id == Label.id)
        .where(
            and_(
                CardLabel.card_id == card.id,
                Label.deleted_at.is_(None),
            ),
        )
        .order_by(Label.id),
    ).all()
    checklists = session.exec(
        select(Checklist)
        .where(and_(Checklist.card_id == card.id, Checklist.deleted_at.is_(None)))
        .order_by(Checklist.position, Checklist.id),
    ).all()
    images = session.exec(
        select(CardImage)
        .where(and_(CardImage.card_id == card.id, CardImage.deleted_at.is_(None)))
        .order_by(CardImage.created_at, CardImage.id),
    ).all()
    assignee_users = session.exec(
        select(User)
        .join(CardAssignee, CardAssignee.user_id == User.id)
        .where(
            and_(
                CardAssignee.card_id == card.id,
                User.deleted_at.is_(None),
                User.is_active.is_(True),
            ),
        )
        .order_by(User.name, User.id),
    ).all()
    return {
        "id": card.id,
        "board_id": card.board_id,
        "list_id": card.list_id,
        "title": card.title,
        "description": card.description,
        "position": card.position,
        "cover_image_id": card.cover_image_id,
        "total_tracked_seconds": card.total_tracked_seconds,
        "labels": [label_payload(label) for label in labels],
        "checklists": [checklist_payload(session, checklist) for checklist in checklists],
        "images": [card_image_payload(image) for image in images],
        "assignees": [user_public(user) for user in assignee_users],
    }


def _batch_card_summaries(session: Session, card_ids: list[int]) -> dict[int, dict]:
    """Fetch labels/checklist-counts/image-counts/assignees for many cards at once.

    Board and list views only need to show counts (checklist progress, image
    count) on the card face, not the full nested detail (which is fetched
    lazily via GET /cards/{id} when a card is opened). Batching these lookups
    avoids an O(cards) fan-out of queries per board load.
    """
    empty = {"labels": [], "checklist_total": 0, "checklist_done": 0, "image_count": 0, "assignees": []}
    if not card_ids:
        return {}

    summaries = {card_id: dict(empty, labels=[], assignees=[]) for card_id in card_ids}

    label_rows = session.exec(
        select(CardLabel.card_id, Label)
        .join(Label, Label.id == CardLabel.label_id)
        .where(and_(CardLabel.card_id.in_(card_ids), Label.deleted_at.is_(None)))
        .order_by(Label.id),
    ).all()
    for card_id, label in label_rows:
        summaries[card_id]["labels"].append(label_payload(label))

    checklist_rows = session.exec(
        select(Checklist.id, Checklist.card_id)
        .where(and_(Checklist.card_id.in_(card_ids), Checklist.deleted_at.is_(None))),
    ).all()
    card_id_by_checklist_id = {checklist_id: card_id for checklist_id, card_id in checklist_rows}

    if card_id_by_checklist_id:
        item_rows = session.exec(
            select(ChecklistItem.checklist_id, ChecklistItem.is_done)
            .where(
                and_(
                    ChecklistItem.checklist_id.in_(card_id_by_checklist_id.keys()),
                    ChecklistItem.deleted_at.is_(None),
                ),
            ),
        ).all()
        for checklist_id, is_done in item_rows:
            card_id = card_id_by_checklist_id.get(checklist_id)
            if card_id is None:
                continue
            summaries[card_id]["checklist_total"] += 1
            if is_done:
                summaries[card_id]["checklist_done"] += 1

    image_rows = session.exec(
        select(CardImage.card_id, func.count(CardImage.id))
        .where(and_(CardImage.card_id.in_(card_ids), CardImage.deleted_at.is_(None)))
        .group_by(CardImage.card_id),
    ).all()
    for card_id, count in image_rows:
        summaries[card_id]["image_count"] = int(count)

    assignee_rows = session.exec(
        select(CardAssignee.card_id, User)
        .join(User, User.id == CardAssignee.user_id)
        .where(
            and_(
                CardAssignee.card_id.in_(card_ids),
                User.deleted_at.is_(None),
                User.is_active.is_(True),
            ),
        )
        .order_by(User.name, User.id),
    ).all()
    for card_id, user in assignee_rows:
        summaries[card_id]["assignees"].append(user_public(user))

    return summaries


def _card_summary_payload(card: Card, summary: dict) -> dict:
    return {
        "id": card.id,
        "board_id": card.board_id,
        "list_id": card.list_id,
        "title": card.title,
        "description": card.description,
        "position": card.position,
        "cover_image_id": card.cover_image_id,
        "total_tracked_seconds": card.total_tracked_seconds,
        "labels": summary["labels"],
        "checklist_total": summary["checklist_total"],
        "checklist_done": summary["checklist_done"],
        "image_count": summary["image_count"],
        "assignees": summary["assignees"],
    }


def list_payload(session: Session, board_list: BoardList) -> dict:
    cards = session.exec(
        select(Card)
        .where(and_(Card.list_id == board_list.id, Card.deleted_at.is_(None)))
        .order_by(Card.position, Card.id),
    ).all()
    summaries = _batch_card_summaries(session, [card.id for card in cards])
    return {
        "id": board_list.id,
        "board_id": board_list.board_id,
        "title": board_list.title,
        "position": board_list.position,
        "cards": [_card_summary_payload(card, summaries[card.id]) for card in cards],
    }


def board_payload(session: Session, board: Board) -> dict:
    labels = session.exec(
        select(Label)
        .where(and_(Label.board_id == board.id, Label.deleted_at.is_(None)))
        .order_by(Label.id),
    ).all()
    lists = session.exec(
        select(BoardList)
        .where(and_(BoardList.board_id == board.id, BoardList.deleted_at.is_(None)))
        .order_by(BoardList.position, BoardList.id),
    ).all()

    list_ids = [board_list.id for board_list in lists]
    cards = (
        session.exec(
            select(Card)
            .where(and_(Card.list_id.in_(list_ids), Card.deleted_at.is_(None)))
            .order_by(Card.position, Card.id),
        ).all()
        if list_ids
        else []
    )
    summaries = _batch_card_summaries(session, [card.id for card in cards])
    cards_by_list: dict[int, list[Card]] = {}
    for card in cards:
        cards_by_list.setdefault(card.list_id, []).append(card)

    return {
        "id": board.id,
        "name": board.name,
        "description": board.description,
        "color_hex": board.color_hex,
        "labels": [label_payload(label) for label in labels],
        "lists": [
            {
                "id": board_list.id,
                "board_id": board_list.board_id,
                "title": board_list.title,
                "position": board_list.position,
                "cards": [
                    _card_summary_payload(card, summaries[card.id])
                    for card in cards_by_list.get(board_list.id, [])
                ],
            }
            for board_list in lists
        ],
    }

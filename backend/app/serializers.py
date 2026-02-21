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


def list_payload(session: Session, board_list: BoardList) -> dict:
    cards = session.exec(
        select(Card)
        .where(and_(Card.list_id == board_list.id, Card.deleted_at.is_(None)))
        .order_by(Card.position, Card.id),
    ).all()
    return {
        "id": board_list.id,
        "board_id": board_list.board_id,
        "title": board_list.title,
        "position": board_list.position,
        "cards": [card_payload(session, card) for card in cards],
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
    return {
        "id": board.id,
        "name": board.name,
        "description": board.description,
        "color_hex": board.color_hex,
        "labels": [label_payload(label) for label in labels],
        "lists": [list_payload(session, board_list) for board_list in lists],
    }

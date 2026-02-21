from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, and_, select

from app.core.config import settings
from app.db.session import get_session
from app.deps import ensure_board_access, get_current_user, require_system_admin
from app.models import Board, BoardMembership, User
from app.schemas import (
    BoardCreateRequest,
    BoardMemberCreateRequest,
    BoardMemberUpdateRequest,
    BoardUpdateRequest,
)
from app.serializers import board_payload, user_public


router = APIRouter(prefix="/boards", tags=["boards"])


@router.post("")
def create_board(
    payload: BoardCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    board = Board(
        name=payload.name,
        description=payload.description,
        color_hex=payload.color_hex or settings.default_board_color,
        created_by_user_id=current_user.id,
    )
    session.add(board)
    session.commit()
    session.refresh(board)

    session.add(
        BoardMembership(board_id=board.id, user_id=current_user.id, role="board_admin"),
    )
    session.commit()
    return board_payload(session, board)


@router.get("")
def list_boards(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.is_system_admin:
        boards = session.exec(
            select(Board).where(Board.deleted_at.is_(None)).order_by(Board.id),
        ).all()
    else:
        boards = session.exec(
            select(Board)
            .join(BoardMembership, BoardMembership.board_id == Board.id)
            .where(
                and_(
                    BoardMembership.user_id == current_user.id,
                    Board.deleted_at.is_(None),
                ),
            )
            .order_by(Board.id),
        ).all()

    return [
        {
            "id": board.id,
            "name": board.name,
            "description": board.description,
            "color_hex": board.color_hex,
        }
        for board in boards
    ]


@router.get("/{board_id}")
def get_board(
    board_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    board = ensure_board_access(board_id=board_id, user=current_user, session=session)
    return board_payload(session, board)


@router.patch("/{board_id}")
def update_board(
    board_id: int,
    payload: BoardUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    board = ensure_board_access(
        board_id=board_id,
        user=current_user,
        session=session,
        require_board_admin=True,
    )
    if payload.name is not None:
        board.name = payload.name
    if payload.description is not None:
        board.description = payload.description
    if payload.color_hex is not None:
        board.color_hex = payload.color_hex
    board.updated_at = datetime.utcnow()
    session.add(board)
    session.commit()
    session.refresh(board)
    return board_payload(session, board)


@router.delete("/{board_id}")
def delete_board(
    board_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    board = ensure_board_access(
        board_id=board_id,
        user=current_user,
        session=session,
        require_board_admin=True,
    )
    now = datetime.utcnow()
    board.deleted_at = now
    board.updated_at = now
    session.add(board)
    session.commit()
    return {"success": True}


@router.get("/{board_id}/members")
def list_members(
    board_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    ensure_board_access(board_id=board_id, user=current_user, session=session)
    memberships = session.exec(
        select(BoardMembership)
        .where(BoardMembership.board_id == board_id)
        .order_by(BoardMembership.id),
    ).all()
    user_ids = [membership.user_id for membership in memberships]
    users = session.exec(
        select(User).where(and_(User.id.in_(user_ids), User.deleted_at.is_(None))),
    ).all()
    user_map = {user.id: user for user in users}
    return [
        {
            "user": user_public(user_map[membership.user_id]),
            "role": membership.role,
        }
        for membership in memberships
        if membership.user_id in user_map
    ]


@router.post("/{board_id}/members")
def add_member(
    board_id: int,
    payload: BoardMemberCreateRequest,
    _: User = Depends(require_system_admin),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    ensure_board_access(board_id=board_id, user=current_user, session=session)
    user = session.get(User, payload.user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    membership = session.exec(
        select(BoardMembership).where(
            and_(
                BoardMembership.board_id == board_id,
                BoardMembership.user_id == payload.user_id,
            ),
        ),
    ).first()
    if membership:
        membership.role = payload.role
    else:
        membership = BoardMembership(
            board_id=board_id,
            user_id=payload.user_id,
            role=payload.role,
        )
    session.add(membership)
    session.commit()
    return {"success": True}


@router.patch("/{board_id}/members/{user_id}")
def update_member(
    board_id: int,
    user_id: int,
    payload: BoardMemberUpdateRequest,
    _: User = Depends(require_system_admin),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    ensure_board_access(board_id=board_id, user=current_user, session=session)
    membership = session.exec(
        select(BoardMembership).where(
            and_(BoardMembership.board_id == board_id, BoardMembership.user_id == user_id),
        ),
    ).first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
    membership.role = payload.role
    session.add(membership)
    session.commit()
    return {"success": True}


@router.delete("/{board_id}/members/{user_id}")
def remove_member(
    board_id: int,
    user_id: int,
    _: User = Depends(require_system_admin),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    ensure_board_access(board_id=board_id, user=current_user, session=session)
    membership = session.exec(
        select(BoardMembership).where(
            and_(BoardMembership.board_id == board_id, BoardMembership.user_id == user_id),
        ),
    ).first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
    session.delete(membership)
    session.commit()
    return {"success": True}

from datetime import datetime, timedelta
import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, and_, select

from app.db.session import get_session
from app.deps import ensure_board_access, get_current_user
from app.models import Card, TimeSession, User
from app.schemas import TimeSessionUpdateRequest


router = APIRouter(tags=["time-tracking"])
MONTH_PATTERN = re.compile(r"^\d{4}-\d{2}$")


def _active_session_for_user(session: Session, user_id: int) -> TimeSession | None:
    return session.exec(
        select(TimeSession).where(
            and_(TimeSession.user_id == user_id, TimeSession.ended_at.is_(None)),
        ),
    ).first()


def _session_payload(row: TimeSession) -> dict:
    return {
        "id": row.id,
        "card_id": row.card_id,
        "user_id": row.user_id,
        "started_at": row.started_at,
        "ended_at": row.ended_at,
        "duration_seconds": row.duration_seconds,
    }


def _resolved_duration_seconds(row: TimeSession) -> int:
    if row.duration_seconds is not None:
        return int(row.duration_seconds)
    if row.ended_at is None:
        return 0
    return max(0, int((row.ended_at - row.started_at).total_seconds()))


def _month_bounds(month: str | None) -> tuple[str, datetime, datetime]:
    now = datetime.utcnow()
    if month and MONTH_PATTERN.match(month):
        year, month_number = month.split("-")
        year_i = int(year)
        month_i = int(month_number)
        if month_i < 1 or month_i > 12:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid month")
    else:
        year_i = now.year
        month_i = now.month

    month_start = datetime(year_i, month_i, 1)
    if month_i == 12:
        next_month_start = datetime(year_i + 1, 1, 1)
    else:
        next_month_start = datetime(year_i, month_i + 1, 1)
    month_key = f"{year_i:04d}-{month_i:02d}"
    return month_key, month_start, next_month_start


def _format_day_key(value: datetime) -> str:
    return value.strftime("%Y-%m-%d")


def _split_session_by_day(
    *,
    start_at: datetime,
    end_at: datetime,
) -> list[tuple[str, int]]:
    if end_at <= start_at:
        return []

    chunks: list[tuple[str, int]] = []
    cursor = start_at
    while cursor.date() < end_at.date():
        day_end = datetime(cursor.year, cursor.month, cursor.day) + timedelta(days=1)
        seconds = int((day_end - cursor).total_seconds())
        if seconds > 0:
            chunks.append((_format_day_key(cursor), seconds))
        cursor = day_end

    tail_seconds = int((end_at - cursor).total_seconds())
    if tail_seconds > 0:
        chunks.append((_format_day_key(cursor), tail_seconds))
    return chunks


@router.post("/cards/{card_id}/timer/start")
def start_timer(
    card_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)

    active = _active_session_for_user(session, current_user.id)
    if active:
        if active.card_id == card_id:
            return {
                "session": _session_payload(active),
                "summary": {"total_seconds": card.total_tracked_seconds},
            }
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Another timer is already running",
        )

    row = TimeSession(
        card_id=card_id,
        user_id=current_user.id,
        started_at=datetime.utcnow(),
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return {
        "session": _session_payload(row),
        "summary": {"total_seconds": card.total_tracked_seconds},
    }


@router.post("/cards/{card_id}/timer/stop")
def stop_timer(
    card_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    active = _active_session_for_user(session, current_user.id)
    if not active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active timer")
    if active.card_id != card_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active timer belongs to another card",
        )

    now = datetime.utcnow()
    elapsed = int((now - active.started_at).total_seconds())
    active.ended_at = now
    active.duration_seconds = max(0, elapsed)
    card.total_tracked_seconds += active.duration_seconds
    card.updated_at = now
    session.add(active)
    session.add(card)
    session.commit()
    session.refresh(active)
    session.refresh(card)
    return {
        "session": _session_payload(active),
        "summary": {"total_seconds": card.total_tracked_seconds},
    }


@router.get("/cards/{card_id}/time")
def get_card_time(
    card_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    active = _active_session_for_user(session, current_user.id)
    if active and active.card_id != card_id:
        active = None
    return {
        "total_seconds": card.total_tracked_seconds,
        "active_session": _session_payload(active) if active else None,
    }


@router.get("/users/me/active-timer")
def get_active_timer(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    active = _active_session_for_user(session, current_user.id)
    return {"active_session": _session_payload(active) if active else None}


@router.get("/cards/{card_id}/time-sessions")
def get_time_sessions(
    card_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    card = session.get(Card, card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)
    rows = session.exec(
        select(TimeSession)
        .where(
            and_(
                TimeSession.card_id == card_id,
                TimeSession.user_id == current_user.id,
            ),
        )
        .order_by(TimeSession.started_at.desc(), TimeSession.id.desc()),
    ).all()
    return [_session_payload(row) for row in rows]


@router.patch("/time-sessions/{session_id}")
def update_time_session(
    session_id: int,
    payload: TimeSessionUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    row = session.get(TimeSession, session_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time session not found")
    if row.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    if row.ended_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stop the running timer before editing this time chunk",
        )

    card = session.get(Card, row.card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)

    previous = _resolved_duration_seconds(row)
    next_duration = max(0, int(payload.duration_seconds))
    delta = next_duration - previous

    row.duration_seconds = next_duration
    row.ended_at = row.started_at + timedelta(seconds=next_duration)
    card.total_tracked_seconds = max(0, card.total_tracked_seconds + delta)
    card.updated_at = datetime.utcnow()

    session.add(row)
    session.add(card)
    session.commit()
    session.refresh(row)
    session.refresh(card)
    return {
        "session": _session_payload(row),
        "summary": {"total_seconds": card.total_tracked_seconds},
    }


@router.delete("/time-sessions/{session_id}")
def delete_time_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    row = session.get(TimeSession, session_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time session not found")
    if row.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    if row.ended_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stop the running timer before deleting this time chunk",
        )

    card = session.get(Card, row.card_id)
    if not card or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    ensure_board_access(board_id=card.board_id, user=current_user, session=session)

    duration = _resolved_duration_seconds(row)
    card.total_tracked_seconds = max(0, card.total_tracked_seconds - duration)
    card.updated_at = datetime.utcnow()

    card_id = row.card_id
    session.delete(row)
    session.add(card)
    session.commit()
    session.refresh(card)
    return {
        "deleted": True,
        "card_id": card_id,
        "summary": {"total_seconds": card.total_tracked_seconds},
    }


@router.get("/boards/{board_id}/calendar")
def get_board_month_calendar(
    board_id: int,
    month: str | None = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    ensure_board_access(board_id=board_id, user=current_user, session=session)
    month_key, month_start, next_month_start = _month_bounds(month)

    cards = session.exec(
        select(Card).where(and_(Card.board_id == board_id, Card.deleted_at.is_(None))),
    ).all()
    card_map = {card.id: card for card in cards}

    sessions = session.exec(
        select(TimeSession)
        .join(Card, Card.id == TimeSession.card_id)
        .where(
            and_(
                Card.board_id == board_id,
                Card.deleted_at.is_(None),
                TimeSession.started_at < next_month_start,
                (TimeSession.ended_at.is_(None) | (TimeSession.ended_at > month_start)),
            ),
        )
        .order_by(TimeSession.started_at, TimeSession.id),
    ).all()

    day_totals: dict[str, dict[int, int]] = {}
    card_totals: dict[int, int] = {}

    now = datetime.utcnow()
    for row in sessions:
        if row.card_id not in card_map:
            continue
        raw_end = row.ended_at or now
        bounded_start = max(row.started_at, month_start)
        bounded_end = min(raw_end, next_month_start)
        for day_key, seconds in _split_session_by_day(
            start_at=bounded_start,
            end_at=bounded_end,
        ):
            day_entry = day_totals.setdefault(day_key, {})
            day_entry[row.card_id] = day_entry.get(row.card_id, 0) + seconds
            card_totals[row.card_id] = card_totals.get(row.card_id, 0) + seconds

    cards_payload = [
        {
            "id": card_id,
            "title": card_map[card_id].title,
            "total_seconds": total_seconds,
        }
        for card_id, total_seconds in card_totals.items()
    ]
    cards_payload.sort(key=lambda item: item["title"].lower())

    days_payload: dict[str, dict] = {}
    for day_key in sorted(day_totals.keys()):
        per_card = day_totals[day_key]
        card_rows = [
            {
                "card_id": card_id,
                "card_title": card_map[card_id].title,
                "seconds": per_card[card_id],
            }
            for card_id in per_card.keys()
        ]
        card_rows.sort(key=lambda item: item["card_title"].lower())
        days_payload[day_key] = {
            "total_seconds": sum(per_card.values()),
            "cards": card_rows,
        }

    return {
        "month": month_key,
        "month_start": month_start.date().isoformat(),
        "month_end": (next_month_start - timedelta(days=1)).date().isoformat(),
        "timezone": "UTC",
        "cards": cards_payload,
        "days": days_payload,
    }

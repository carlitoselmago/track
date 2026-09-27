from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from sqlmodel import Session

from app.core.security import decode_token
from app.db.session import engine
from app.deps import ensure_board_access
from app.models import User
from app.services.realtime import hub

router = APIRouter(tags=["realtime"])


def _authenticate_ws(token: str | None) -> User | None:
    if not token:
        return None
    try:
        payload = decode_token(token)
    except ValueError:
        return None
    if payload.get("type") != "access" or not payload.get("sub"):
        return None
    with Session(engine) as session:
        user = session.get(User, int(payload["sub"]))
        if user and user.is_active and user.deleted_at is None:
            return user
    return None


@router.websocket("/ws/boards/{board_id}")
async def board_updates(websocket: WebSocket, board_id: int, token: str | None = None):
    user = _authenticate_ws(token)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    with Session(engine) as session:
        try:
            ensure_board_access(board_id=board_id, user=user, session=session)
        except Exception:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    await websocket.accept()
    await hub.connect(board_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await hub.disconnect(board_id, websocket)

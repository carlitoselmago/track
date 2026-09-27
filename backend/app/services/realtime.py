import asyncio
import logging

from fastapi import WebSocket

logger = logging.getLogger("track.realtime")


class BoardHub:
    """In-process pub/sub for board-scoped WebSocket connections.

    Publishing happens from sync request-handler code (running in FastAPI's
    threadpool), so `publish` hops onto the event loop captured at startup
    via `run_coroutine_threadsafe` instead of awaiting directly.
    """

    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = {}
        self._lock = asyncio.Lock()
        self.loop: asyncio.AbstractEventLoop | None = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self.loop = loop

    async def connect(self, board_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.setdefault(board_id, set()).add(websocket)

    async def disconnect(self, board_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            connections = self._connections.get(board_id)
            if connections:
                connections.discard(websocket)
                if not connections:
                    self._connections.pop(board_id, None)

    async def _broadcast(self, board_id: int, message: dict) -> None:
        async with self._lock:
            connections = list(self._connections.get(board_id, ()))
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                await self.disconnect(board_id, websocket)

    def publish(self, board_id: int | None, event_type: str, client_id: str | None = None, **extra) -> None:
        if board_id is None or self.loop is None:
            return
        message = {"type": event_type, "board_id": board_id, "client_id": client_id, **extra}
        try:
            asyncio.run_coroutine_threadsafe(self._broadcast(board_id, message), self.loop)
        except RuntimeError:
            logger.debug("Realtime publish skipped: event loop not running.")


hub = BoardHub()

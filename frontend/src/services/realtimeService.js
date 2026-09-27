import { API_BASE_URL } from "./axios";
import { clientId } from "./clientId";

const MIN_RETRY_DELAY_MS = 1000;
const MAX_RETRY_DELAY_MS = 30000;

function buildSocketUrl(boardId, token) {
  const apiUrl = new URL(API_BASE_URL, window.location.origin);
  const protocol = apiUrl.protocol === "https:" ? "wss:" : "ws:";
  const path = `${apiUrl.pathname.replace(/\/$/, "")}/ws/boards/${boardId}`;
  const url = new URL(path, `${protocol}//${apiUrl.host}`);
  if (token) {
    url.searchParams.set("token", token);
  }
  return url.toString();
}

/**
 * Opens a live-updates WebSocket for a board with automatic reconnect
 * (exponential backoff). Events carrying our own `client_id` are dropped,
 * since the action that caused them already updated local state optimistically.
 */
export function connectBoardSocket(boardId, { getToken, onEvent }) {
  let socket = null;
  let closedByCaller = false;
  let retryDelay = MIN_RETRY_DELAY_MS;
  let retryTimer = null;

  function scheduleReconnect() {
    if (closedByCaller) {
      return;
    }
    retryTimer = window.setTimeout(open, retryDelay);
    retryDelay = Math.min(retryDelay * 2, MAX_RETRY_DELAY_MS);
  }

  function open() {
    if (closedByCaller) {
      return;
    }
    const token = getToken?.();
    if (!token) {
      scheduleReconnect();
      return;
    }

    socket = new WebSocket(buildSocketUrl(boardId, token));

    socket.addEventListener("open", () => {
      retryDelay = MIN_RETRY_DELAY_MS;
    });

    socket.addEventListener("message", (event) => {
      let data;
      try {
        data = JSON.parse(event.data);
      } catch {
        return;
      }
      if (data?.client_id && data.client_id === clientId) {
        return;
      }
      onEvent?.(data);
    });

    socket.addEventListener("close", scheduleReconnect);
    socket.addEventListener("error", () => socket?.close());
  }

  open();

  return {
    close() {
      closedByCaller = true;
      if (retryTimer) {
        window.clearTimeout(retryTimer);
        retryTimer = null;
      }
      socket?.close();
      socket = null;
    },
  };
}

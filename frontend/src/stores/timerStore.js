import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { timerService } from "@/services/timerService";
import { normalizeApiError } from "@/services/axios";
import { useUiStore } from "./uiStore";
import { useBoardStore } from "./boardStore";

const TIMER_META_KEY = "track_timer_meta_v1";

const parseJson = (value, fallback = null) => {
  try {
    return JSON.parse(value);
  } catch {
    return fallback;
  }
};

const extractPayload = (payload) => payload?.data || payload;

const extractSession = (payload) =>
  payload?.active_session || payload?.session || payload?.time_session || payload || null;

const extractTimeSummary = (payload) =>
  payload?.summary ||
  payload?.time_summary ||
  payload?.card_time ||
  payload ||
  {};

const parseApiDate = (value) => {
  if (!value) {
    return null;
  }
  if (value instanceof Date) {
    return value;
  }
  const raw = String(value);
  const hasZone = /(?:Z|[+-]\d{2}:\d{2})$/.test(raw);
  const normalized = hasZone ? raw : `${raw}Z`;
  const parsed = new Date(normalized);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }
  return parsed;
};

const toSecondsSince = (isoDate, nowMs) => {
  if (!isoDate) {
    return 0;
  }
  const started = parseApiDate(isoDate);
  if (!started) {
    return 0;
  }
  const startedMs = started.getTime();
  return Math.max(0, Math.floor((nowMs - startedMs) / 1000));
};

let ticker = null;

export const useTimerStore = defineStore("timer", () => {
  const saved = parseJson(localStorage.getItem(TIMER_META_KEY), {});
  const activeSession = ref(saved?.activeSession || null);
  const nowMs = ref(Date.now());
  const totalByCard = ref({});
  const sessionsByCard = ref({});

  const hasActiveTimer = computed(() => Boolean(activeSession.value?.id));
  const activeCardId = computed(() => activeSession.value?.card_id ?? null);
  const liveElapsedSeconds = computed(() =>
    activeSession.value
      ? toSecondsSince(activeSession.value.started_at, nowMs.value)
      : 0,
  );

  function persistTimerMeta() {
    localStorage.setItem(
      TIMER_META_KEY,
      JSON.stringify({
        activeSession: activeSession.value
          ? {
              id: activeSession.value.id,
              card_id: activeSession.value.card_id,
              user_id: activeSession.value.user_id,
              started_at: activeSession.value.started_at,
            }
          : null,
      }),
    );
  }

  function startTicker() {
    stopTicker();
    nowMs.value = Date.now();
    ticker = window.setInterval(() => {
      nowMs.value = Date.now();
    }, 1000);
  }

  function stopTicker() {
    if (ticker) {
      clearInterval(ticker);
      ticker = null;
    }
  }

  function setActiveSession(session) {
    activeSession.value = session || null;
    persistTimerMeta();
    if (activeSession.value) {
      startTicker();
    } else {
      stopTicker();
    }
  }

  function clearActiveTimer() {
    setActiveSession(null);
  }

  function updateBoardCardTotal(cardId, seconds) {
    if (cardId == null || seconds == null) {
      return;
    }
    const boardStore = useBoardStore();
    boardStore.patchCard(cardId, {
      total_tracked_seconds: seconds,
    });
  }

  function applySummary(cardId, payload) {
    const summary = extractTimeSummary(extractPayload(payload));
    const totalSeconds =
      summary.total_seconds ??
      summary.total_tracked_seconds ??
      summary.total ??
      null;

    if (totalSeconds != null) {
      totalByCard.value[cardId] = totalSeconds;
      updateBoardCardTotal(cardId, totalSeconds);
    }

    return summary;
  }

  async function bootstrapActiveTimer() {
    const uiStore = useUiStore();
    try {
      const payload = await timerService.getActiveTimer();
      const sessionCandidate = extractSession(extractPayload(payload));
      if (sessionCandidate?.id && !sessionCandidate?.ended_at) {
        setActiveSession(sessionCandidate);
      } else {
        setActiveSession(null);
      }
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      setActiveSession(null);
      throw normalized;
    }
  }

  async function startTimer(cardId) {
    const uiStore = useUiStore();

    if (hasActiveTimer.value && activeCardId.value !== cardId) {
      const err = {
        status: 400,
        message: "Stop the current timer before starting another card timer.",
      };
      uiStore.setError(err.message);
      throw err;
    }

    try {
      const payload = await timerService.startTimer(cardId);
      const cleanPayload = extractPayload(payload);
      const session = extractSession(cleanPayload);
      if (!session?.id) {
        throw new Error("Timer start did not return a session.");
      }
      setActiveSession(session);
      applySummary(cardId, cleanPayload);
      return session;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function stopTimer() {
    if (!activeSession.value?.card_id) {
      return null;
    }

    const uiStore = useUiStore();
    const cardId = activeSession.value.card_id;

    try {
      const payload = await timerService.stopTimer(cardId);
      const cleanPayload = extractPayload(payload);
      applySummary(cardId, cleanPayload);
      setActiveSession(null);
      return cleanPayload;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function fetchCardSummary(cardId) {
    const uiStore = useUiStore();
    try {
      const payload = await timerService.getCardTime(cardId);
      return applySummary(cardId, extractPayload(payload));
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function fetchTimeSessions(cardId) {
    const uiStore = useUiStore();
    try {
      const payload = await timerService.getTimeSessions(cardId);
      const rows = Array.isArray(payload)
        ? payload
        : payload?.sessions || payload?.items || [];
      sessionsByCard.value[cardId] = rows;
      return rows;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function updateTimeSession(sessionId, durationSeconds) {
    const uiStore = useUiStore();
    try {
      const payload = await timerService.updateTimeSession(sessionId, durationSeconds);
      const cleanPayload = extractPayload(payload);
      const sessionRow = extractSession(cleanPayload);
      const cardId = sessionRow?.card_id;
      if (cardId != null) {
        const sessions = sessionsByCard.value[cardId] || [];
        const nextSessions = sessions.map((entry) =>
          entry.id === sessionRow.id ? sessionRow : entry,
        );
        sessionsByCard.value[cardId] = nextSessions;
        applySummary(cardId, cleanPayload);
      }
      return cleanPayload;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function deleteTimeSession(sessionId) {
    const uiStore = useUiStore();
    try {
      let resolvedCardId = null;
      for (const [cardIdKey, rows] of Object.entries(sessionsByCard.value)) {
        if ((rows || []).some((row) => row.id === sessionId)) {
          resolvedCardId = Number(cardIdKey);
          break;
        }
      }

      const payload = await timerService.deleteTimeSession(sessionId);
      const cleanPayload = extractPayload(payload);
      const cardId = cleanPayload.card_id ?? resolvedCardId;
      if (cardId != null) {
        const sessions = sessionsByCard.value[cardId] || [];
        sessionsByCard.value[cardId] = sessions.filter((row) => row.id !== sessionId);
        applySummary(cardId, cleanPayload);
      }
      return cleanPayload;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  function totalSecondsForCard(cardId, baseTotal = 0) {
    const persisted = totalByCard.value[cardId];
    const baseline = persisted != null ? persisted : baseTotal;

    if (activeSession.value?.card_id === cardId) {
      return baseline + liveElapsedSeconds.value;
    }

    return baseline;
  }

  return {
    activeSession,
    hasActiveTimer,
    activeCardId,
    liveElapsedSeconds,
    totalByCard,
    sessionsByCard,
    bootstrapActiveTimer,
    startTimer,
    stopTimer,
    fetchCardSummary,
    fetchTimeSessions,
    updateTimeSession,
    deleteTimeSession,
    totalSecondsForCard,
    clearActiveTimer,
  };
});

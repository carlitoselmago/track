import { beforeEach, describe, expect, it, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { useTimerStore } from "@/stores/timerStore";
import { timerService } from "@/services/timerService";

vi.mock("@/services/timerService", () => ({
  timerService: {
    startTimer: vi.fn(),
    stopTimer: vi.fn(),
    getCardTime: vi.fn(),
    getActiveTimer: vi.fn(),
    getTimeSessions: vi.fn(),
  },
}));

describe("timerStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
    vi.clearAllMocks();
  });

  it("starts timer and tracks active session", async () => {
    const startedAt = new Date(Date.now() - 4000).toISOString();
    timerService.startTimer.mockResolvedValue({
      session: { id: 1, card_id: 10, user_id: 2, started_at: startedAt },
      summary: { total_seconds: 120 },
    });

    const store = useTimerStore();
    await store.startTimer(10);

    expect(store.hasActiveTimer).toBe(true);
    expect(store.activeCardId).toBe(10);
    expect(store.totalSecondsForCard(10, 0)).toBeGreaterThanOrEqual(120);
  });

  it("hydrates active timer from backend", async () => {
    timerService.getActiveTimer.mockResolvedValue({
      active_session: {
        id: 3,
        card_id: 7,
        user_id: 1,
        started_at: new Date().toISOString(),
        ended_at: null,
      },
    });

    const store = useTimerStore();
    await store.bootstrapActiveTimer();

    expect(store.hasActiveTimer).toBe(true);
    expect(store.activeCardId).toBe(7);
  });
});

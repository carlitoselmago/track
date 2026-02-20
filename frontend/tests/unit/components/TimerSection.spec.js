import { beforeEach, describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import TimerSection from "@/components/cards/TimerSection.vue";
import { useTimerStore } from "@/stores/timerStore";

vi.mock("@/services/timerService", () => ({
  timerService: {
    startTimer: vi.fn(),
    stopTimer: vi.fn(),
    getCardTime: vi.fn(),
    getActiveTimer: vi.fn(),
    getTimeSessions: vi.fn(),
  },
}));

describe("TimerSection", () => {
  let pinia;

  beforeEach(() => {
    pinia = createPinia();
    setActivePinia(pinia);
    vi.clearAllMocks();
  });

  it("disables start when another card timer is running", () => {
    const timerStore = useTimerStore();
    timerStore.activeSession = {
      id: 1,
      card_id: 99,
      user_id: 1,
      started_at: new Date().toISOString(),
    };

    const wrapper = mount(TimerSection, {
      props: {
        card: {
          id: 5,
          total_tracked_seconds: 0,
        },
      },
      global: {
        plugins: [pinia],
      },
    });

    const buttons = wrapper.findAll("button");
    expect(buttons[0].element.disabled).toBe(true);
  });
});

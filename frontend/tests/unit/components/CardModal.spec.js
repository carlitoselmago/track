import { beforeEach, describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import CardModal from "@/components/cards/CardModal.vue";
import { useCardStore } from "@/stores/cardStore";
import { useBoardStore } from "@/stores/boardStore";

vi.mock("@/services/cardService", () => ({
  cardService: {
    createCard: vi.fn(),
    getCard: vi.fn(),
    updateCard: vi.fn(),
    deleteCard: vi.fn(),
    moveCard: vi.fn(),
    reorderCards: vi.fn(),
  },
}));

vi.mock("@/services/checklistService", () => ({
  checklistService: {
    createChecklist: vi.fn(),
    updateChecklist: vi.fn(),
    deleteChecklist: vi.fn(),
    createChecklistItem: vi.fn(),
    updateChecklistItem: vi.fn(),
    deleteChecklistItem: vi.fn(),
  },
}));

vi.mock("@/services/labelService", () => ({
  labelService: {
    getBoardLabels: vi.fn(),
    createLabel: vi.fn(),
    updateLabel: vi.fn(),
    deleteLabel: vi.fn(),
    assignLabel: vi.fn(),
    unassignLabel: vi.fn(),
  },
}));

vi.mock("@/services/imageService", () => ({
  imageService: {
    uploadCardImage: vi.fn(),
    getCardImages: vi.fn(),
    deleteImage: vi.fn(),
    setCardCover: vi.fn(),
    getImageContentUrl: vi.fn().mockReturnValue("/image"),
  },
}));

vi.mock("@/services/timerService", () => ({
  timerService: {
    startTimer: vi.fn(),
    stopTimer: vi.fn(),
    getCardTime: vi.fn().mockResolvedValue({ total_seconds: 0 }),
    getActiveTimer: vi.fn(),
    getTimeSessions: vi.fn(),
  },
}));

describe("CardModal", () => {
  let pinia;

  beforeEach(() => {
    pinia = createPinia();
    setActivePinia(pinia);
    vi.clearAllMocks();
  });

  it("renders modal sections when card is active", async () => {
    const boardStore = useBoardStore();
    boardStore.currentBoard = {
      id: 1,
      labels: [],
      lists: [],
    };

    const cardStore = useCardStore();
    cardStore.isModalOpen = true;
    cardStore.isLoading = false;
    cardStore.activeCard = {
      id: 7,
      title: "Card A",
      description: "",
      labels: [],
      checklists: [],
      images: [],
      total_tracked_seconds: 0,
    };

    const wrapper = mount(CardModal, {
      global: {
        plugins: [pinia],
        stubs: {
          teleport: true,
        },
      },
    });

    expect(wrapper.text()).toContain("Card A");
    expect(wrapper.text()).toContain("Delete card");
  });
});

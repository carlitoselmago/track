import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import KanbanBoardView from "@/views/KanbanBoardView.vue";
import { boardService } from "@/services/boardService";
import { labelService } from "@/services/labelService";
import { useBoardStore } from "@/stores/boardStore";

vi.mock("@/services/boardService", () => ({
  boardService: {
    getBoards: vi.fn(),
    getBoard: vi.fn(),
    createBoard: vi.fn(),
    updateBoard: vi.fn(),
    deleteBoard: vi.fn(),
  },
}));

vi.mock("@/services/listService", () => ({
  listService: {
    createList: vi.fn(),
    updateList: vi.fn(),
    deleteList: vi.fn(),
    reorderLists: vi.fn().mockResolvedValue({}),
  },
}));

vi.mock("@/services/cardService", () => ({
  cardService: {
    createCard: vi.fn(),
    getCard: vi.fn(),
    updateCard: vi.fn(),
    deleteCard: vi.fn(),
    moveCard: vi.fn().mockResolvedValue({}),
    reorderCards: vi.fn().mockResolvedValue({}),
  },
}));

vi.mock("@/services/labelService", () => ({
  labelService: {
    getBoardLabels: vi.fn(),
  },
}));

describe("KanbanBoardView", () => {
  let pinia;

  beforeEach(() => {
    pinia = createPinia();
    setActivePinia(pinia);
    vi.clearAllMocks();
  });

  it("loads board and renders title", async () => {
    boardService.getBoard.mockResolvedValue({
      id: 1,
      name: "Roadmap",
      color_hex: "#16A34A",
      lists: [],
      labels: [],
    });
    labelService.getBoardLabels.mockResolvedValue([]);

    const wrapper = mount(KanbanBoardView, {
      props: { boardId: 1 },
      global: {
        plugins: [pinia],
        stubs: {
          teleport: true,
        },
      },
    });

    await flushPromises();
    const boardStore = useBoardStore();

    expect(boardService.getBoard).toHaveBeenCalledWith(1);
    expect(boardStore.currentBoard?.name).toBe("Roadmap");
    expect(wrapper.text()).toContain("Roadmap");
  });
});

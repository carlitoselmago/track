import { beforeEach, describe, expect, it, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { useBoardStore } from "@/stores/boardStore";
import { cardService } from "@/services/cardService";

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
    reorderLists: vi.fn(),
  },
}));

vi.mock("@/services/labelService", () => ({
  labelService: {
    getBoardLabels: vi.fn(),
  },
}));

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

describe("boardStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it("rolls back card move when persistence fails", async () => {
    const store = useBoardStore();
    store.currentBoard = {
      id: 99,
      lists: [
        {
          id: 1,
          title: "Todo",
          position: 0,
          cards: [
            { id: 11, list_id: 1, position: 0 },
            { id: 12, list_id: 1, position: 1 },
          ],
        },
        {
          id: 2,
          title: "Doing",
          position: 1,
          cards: [],
        },
      ],
    };

    const snapshot = store.snapshotLists();
    const moved = store.currentBoard.lists[0].cards.pop();
    store.currentBoard.lists[1].cards.push(moved);

    cardService.moveCard.mockRejectedValue(new Error("move fail"));

    await expect(
      store.persistCardMove({
        fromListId: 1,
        toListId: 2,
        newIndex: 0,
        snapshot,
      }),
    ).rejects.toBeTruthy();

    expect(store.currentBoard.lists[0].cards).toHaveLength(2);
    expect(store.currentBoard.lists[1].cards).toHaveLength(0);
  });
});

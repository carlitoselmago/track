import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { boardService } from "@/services/boardService";
import { listService } from "@/services/listService";
import { cardService } from "@/services/cardService";
import { labelService } from "@/services/labelService";
import { normalizeApiError } from "@/services/axios";
import { useUiStore } from "./uiStore";

const DEFAULT_BOARD_COLOR = "#16A34A";

const sortByPosition = (a, b) => (a.position ?? 0) - (b.position ?? 0);

const clone = (value) => JSON.parse(JSON.stringify(value));

const extractPayload = (payload) => payload?.data || payload;

function normalizeCard(card, listId) {
  return {
    id: card.id,
    list_id: card.list_id ?? listId,
    board_id: card.board_id,
    title: card.title || "",
    description: card.description || "",
    position: card.position ?? 0,
    labels: card.labels || [],
    checklists: card.checklists || [],
    images: card.images || [],
    cover_image_id: card.cover_image_id ?? null,
    total_tracked_seconds: card.total_tracked_seconds ?? 0,
    assignees: card.assignees || [],
  };
}

function normalizeList(list) {
  const cards = (list.cards || [])
    .map((card) => normalizeCard(card, list.id))
    .sort(sortByPosition);

  return {
    id: list.id,
    board_id: list.board_id,
    title: list.title || "",
    position: list.position ?? 0,
    cards,
  };
}

function normalizeBoard(board) {
  const lists = (board.lists || []).map(normalizeList).sort(sortByPosition);
  return {
    id: board.id,
    name: board.name || "Untitled board",
    description: board.description || "",
    color_hex: board.color_hex || DEFAULT_BOARD_COLOR,
    labels: board.labels || [],
    members: board.members || [],
    lists,
  };
}

export const useBoardStore = defineStore("board", () => {
  const boards = ref([]);
  const currentBoard = ref(null);
  const isLoading = ref(false);

  const hasBoardLoaded = computed(() => Boolean(currentBoard.value?.id));

  const findList = (listId) =>
    currentBoard.value?.lists.find((list) => list.id === listId);

  const findCardLocation = (cardId) => {
    if (!currentBoard.value) {
      return null;
    }

    for (const list of currentBoard.value.lists) {
      const cardIndex = list.cards.findIndex((card) => card.id === cardId);
      if (cardIndex >= 0) {
        return {
          listId: list.id,
          cardIndex,
          card: list.cards[cardIndex],
        };
      }
    }

    return null;
  };

  const setListsPositions = () => {
    currentBoard.value.lists.forEach((list, index) => {
      list.position = index;
    });
  };

  const setCardsPositions = (listId) => {
    const list = findList(listId);
    if (!list) {
      return;
    }
    list.cards.forEach((card, index) => {
      card.position = index;
      card.list_id = listId;
    });
  };

  function upsertBoardSummary(board) {
    const existingIndex = boards.value.findIndex((item) => item.id === board.id);
    const summary = {
      id: board.id,
      name: board.name,
      color_hex: board.color_hex || DEFAULT_BOARD_COLOR,
      description: board.description || "",
    };

    if (existingIndex < 0) {
      boards.value.push(summary);
      return;
    }

    boards.value[existingIndex] = {
      ...boards.value[existingIndex],
      ...summary,
    };
  }

  async function fetchBoards() {
    const uiStore = useUiStore();
    isLoading.value = true;
    uiStore.clearError();

    try {
      const payload = await boardService.getBoards();
      const rows = extractPayload(payload);
      boards.value = (Array.isArray(rows) ? rows : rows?.items || []).map(
        (board) => ({
          id: board.id,
          name: board.name || "Untitled board",
          color_hex: board.color_hex || DEFAULT_BOARD_COLOR,
          description: board.description || "",
        }),
      );
      return boards.value;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    } finally {
      isLoading.value = false;
    }
  }

  async function createBoard(payload) {
    const uiStore = useUiStore();
    uiStore.clearError();
    try {
      const response = await boardService.createBoard(payload);
      const board = normalizeBoard(extractPayload(response));
      upsertBoardSummary(board);
      return board;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function updateBoard(boardId, payload) {
    const uiStore = useUiStore();
    uiStore.clearError();
    try {
      const response = await boardService.updateBoard(boardId, payload);
      const board = normalizeBoard(extractPayload(response));
      upsertBoardSummary(board);
      if (currentBoard.value?.id === boardId) {
        currentBoard.value = {
          ...currentBoard.value,
          ...board,
        };
      }
      return board;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function deleteBoard(boardId) {
    const uiStore = useUiStore();
    uiStore.clearError();
    try {
      await boardService.deleteBoard(boardId);
      boards.value = boards.value.filter((board) => board.id !== boardId);
      if (currentBoard.value?.id === boardId) {
        currentBoard.value = null;
      }
      return true;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function loadBoard(boardId) {
    const uiStore = useUiStore();
    isLoading.value = true;
    uiStore.clearError();

    try {
      const payload = await boardService.getBoard(boardId);
      const board = normalizeBoard(extractPayload(payload));

      if (!board.labels?.length) {
        try {
          const labelsPayload = await labelService.getBoardLabels(boardId);
          const labels = extractPayload(labelsPayload);
          board.labels = Array.isArray(labels) ? labels : labels?.items || [];
        } catch {
          board.labels = [];
        }
      }
      try {
        const membersPayload = await boardService.getBoardMembers(boardId);
        const members = extractPayload(membersPayload);
        board.members = Array.isArray(members) ? members : members?.items || [];
      } catch {
        board.members = [];
      }

      currentBoard.value = board;
      upsertBoardSummary(board);
      return board;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    } finally {
      isLoading.value = false;
    }
  }

  async function createList(title) {
    if (!currentBoard.value) {
      return null;
    }
    const uiStore = useUiStore();
    uiStore.clearError();
    try {
      const response = await listService.createList(currentBoard.value.id, {
        title,
      });
      const list = normalizeList(extractPayload(response));
      currentBoard.value.lists.push(list);
      currentBoard.value.lists.sort(sortByPosition);
      return list;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function updateList(listId, payload) {
    const uiStore = useUiStore();
    try {
      const response = await listService.updateList(listId, payload);
      const updated = normalizeList(extractPayload(response));
      const index = currentBoard.value?.lists.findIndex((list) => list.id === listId);
      if (index >= 0) {
        currentBoard.value.lists[index] = {
          ...currentBoard.value.lists[index],
          ...updated,
        };
      }
      return updated;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function deleteList(listId) {
    const uiStore = useUiStore();
    const previous = clone(currentBoard.value?.lists || []);
    currentBoard.value.lists = currentBoard.value.lists.filter(
      (list) => list.id !== listId,
    );

    try {
      await listService.deleteList(listId);
    } catch (error) {
      currentBoard.value.lists = previous;
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function reorderLists({ oldIndex, newIndex }) {
    if (!currentBoard.value || oldIndex === newIndex) {
      return;
    }

    const uiStore = useUiStore();
    const previous = clone(currentBoard.value.lists);
    const moved = currentBoard.value.lists.splice(oldIndex, 1)[0];
    currentBoard.value.lists.splice(newIndex, 0, moved);
    setListsPositions();

    try {
      await listService.reorderLists(currentBoard.value.id, {
        lists: currentBoard.value.lists.map((list) => ({
          id: list.id,
          position: list.position,
        })),
      });
    } catch (error) {
      currentBoard.value.lists = previous;
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function persistListReorder(snapshot) {
    if (!currentBoard.value) {
      return;
    }
    const uiStore = useUiStore();
    setListsPositions();
    try {
      await listService.reorderLists(currentBoard.value.id, {
        lists: currentBoard.value.lists.map((list) => ({
          id: list.id,
          position: list.position,
        })),
      });
    } catch (error) {
      if (snapshot) {
        currentBoard.value.lists = clone(snapshot);
      }
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function createCard(listId, payload) {
    const uiStore = useUiStore();
    uiStore.clearError();
    try {
      const response = await cardService.createCard(listId, payload);
      const card = normalizeCard(extractPayload(response), listId);
      const list = findList(listId);
      if (list) {
        list.cards.push(card);
        list.cards.sort(sortByPosition);
      }
      return card;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  function patchCard(cardId, patch) {
    const location = findCardLocation(cardId);
    if (!location) {
      return;
    }
    location.card = {
      ...location.card,
      ...patch,
    };
    const list = findList(location.listId);
    if (list) {
      list.cards.splice(location.cardIndex, 1, location.card);
    }
  }

  function removeCard(cardId) {
    if (!currentBoard.value) {
      return;
    }

    currentBoard.value.lists.forEach((list) => {
      list.cards = list.cards.filter((card) => card.id !== cardId);
    });
  }

  async function moveCard({ fromListId, toListId, oldIndex, newIndex }) {
    if (!currentBoard.value) {
      return;
    }

    const uiStore = useUiStore();
    const previous = clone(currentBoard.value.lists);
    const source = findList(fromListId);
    const target = findList(toListId);

    if (!source || !target) {
      return;
    }

    const [movedCard] = source.cards.splice(oldIndex, 1);
    if (!movedCard) {
      return;
    }
    target.cards.splice(newIndex, 0, movedCard);
    setCardsPositions(fromListId);
    if (fromListId !== toListId) {
      setCardsPositions(toListId);
    }

    try {
      if (fromListId === toListId) {
        await cardService.reorderCards(fromListId, {
          cards: source.cards.map((card) => ({
            id: card.id,
            position: card.position,
          })),
        });
      } else {
        await cardService.moveCard(movedCard.id, {
          list_id: toListId,
          position: newIndex,
        });
        await Promise.all([
          cardService.reorderCards(fromListId, {
            cards: source.cards.map((card) => ({
              id: card.id,
              position: card.position,
            })),
          }),
          cardService.reorderCards(toListId, {
            cards: target.cards.map((card) => ({
              id: card.id,
              position: card.position,
            })),
          }),
        ]);
      }
    } catch (error) {
      currentBoard.value.lists = previous;
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function persistCardMove({ fromListId, toListId, newIndex, snapshot }) {
    if (!currentBoard.value) {
      return;
    }

    const uiStore = useUiStore();
    const source = findList(fromListId);
    const target = findList(toListId);

    if (!source || !target) {
      return;
    }

    setCardsPositions(fromListId);
    if (toListId !== fromListId) {
      setCardsPositions(toListId);
    }

    try {
      if (fromListId === toListId) {
        await cardService.reorderCards(fromListId, {
          cards: source.cards.map((card) => ({
            id: card.id,
            position: card.position,
          })),
        });
        return;
      }

      const movedCard = target.cards[newIndex];
      if (!movedCard) {
        return;
      }

      await cardService.moveCard(movedCard.id, {
        list_id: toListId,
        position: newIndex,
      });

      await Promise.all([
        cardService.reorderCards(fromListId, {
          cards: source.cards.map((card) => ({
            id: card.id,
            position: card.position,
          })),
        }),
        cardService.reorderCards(toListId, {
          cards: target.cards.map((card) => ({
            id: card.id,
            position: card.position,
          })),
        }),
      ]);
    } catch (error) {
      if (snapshot) {
        currentBoard.value.lists = clone(snapshot);
      }
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  function snapshotLists() {
    return clone(currentBoard.value?.lists || []);
  }

  function setBoardLabels(labels) {
    if (!currentBoard.value) {
      return;
    }
    currentBoard.value.labels = labels;
  }

  async function addBoardMember(boardId, userId, role = "member") {
    await boardService.addBoardMember(boardId, userId, role);
    if (currentBoard.value?.id === Number(boardId)) {
      const membersPayload = await boardService.getBoardMembers(boardId);
      currentBoard.value.members = extractPayload(membersPayload) || [];
    }
  }

  return {
    boards,
    currentBoard,
    isLoading,
    hasBoardLoaded,
    fetchBoards,
    createBoard,
    updateBoard,
    deleteBoard,
    loadBoard,
    createList,
    updateList,
    deleteList,
    reorderLists,
    createCard,
    patchCard,
    removeCard,
    moveCard,
    persistListReorder,
    persistCardMove,
    snapshotLists,
    setBoardLabels,
    addBoardMember,
  };
});

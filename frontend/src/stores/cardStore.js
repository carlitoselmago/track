import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { cardService } from "@/services/cardService";
import { checklistService } from "@/services/checklistService";
import { labelService } from "@/services/labelService";
import { imageService } from "@/services/imageService";
import { timerService } from "@/services/timerService";
import { normalizeApiError } from "@/services/axios";
import { useBoardStore } from "./boardStore";
import { useUiStore } from "./uiStore";

const extractPayload = (payload) => payload?.data || payload;

const normalizeCardDetail = (card) => ({
  id: card.id,
  list_id: card.list_id,
  board_id: card.board_id,
  title: card.title || "",
  description: card.description || "",
  labels: card.labels || [],
  checklists: card.checklists || [],
  images: card.images || [],
  cover_image_id: card.cover_image_id ?? null,
  total_tracked_seconds: card.total_tracked_seconds ?? 0,
  time_summary: card.time_summary || null,
  assignees: card.assignees || [],
});

export const useCardStore = defineStore("card", () => {
  const isModalOpen = ref(false);
  const isLoading = ref(false);
  const activeCardId = ref(null);
  const activeCard = ref(null);

  const hasActiveCard = computed(() => Boolean(activeCard.value?.id));

  const syncCardSummaryToBoard = () => {
    if (!activeCard.value?.id) {
      return;
    }
    const boardStore = useBoardStore();
    boardStore.patchCard(activeCard.value.id, {
      title: activeCard.value.title,
      description: activeCard.value.description,
      labels: activeCard.value.labels,
      checklists: activeCard.value.checklists,
      images: activeCard.value.images,
      cover_image_id: activeCard.value.cover_image_id,
      total_tracked_seconds: activeCard.value.total_tracked_seconds,
      assignees: activeCard.value.assignees,
    });
  };

  function closeModal() {
    isModalOpen.value = false;
    isLoading.value = false;
    activeCardId.value = null;
    activeCard.value = null;
  }

  async function openModal(cardId) {
    const uiStore = useUiStore();
    uiStore.clearError();
    isModalOpen.value = true;
    isLoading.value = true;
    activeCardId.value = cardId;

    try {
      const payload = await cardService.getCard(cardId);
      activeCard.value = normalizeCardDetail(extractPayload(payload));
      await fetchTimeSummary(cardId);
      syncCardSummaryToBoard();
      return activeCard.value;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    } finally {
      isLoading.value = false;
    }
  }

  async function saveCard(patch) {
    if (!activeCard.value?.id) {
      return null;
    }
    const uiStore = useUiStore();
    uiStore.clearError();
    try {
      const payload = await cardService.updateCard(activeCard.value.id, patch);
      activeCard.value = normalizeCardDetail(extractPayload(payload));
      syncCardSummaryToBoard();
      return activeCard.value;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function deleteCard() {
    if (!activeCard.value?.id) {
      return;
    }

    const uiStore = useUiStore();
    const boardStore = useBoardStore();
    uiStore.clearError();
    try {
      await cardService.deleteCard(activeCard.value.id);
      boardStore.removeCard(activeCard.value.id);
      closeModal();
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function addChecklist(title) {
    if (!activeCard.value?.id) {
      return null;
    }
    const payload = await checklistService.createChecklist(activeCard.value.id, {
      title,
    });
    const checklist = extractPayload(payload);
    activeCard.value.checklists.push(checklist);
    syncCardSummaryToBoard();
    return checklist;
  }

  async function updateChecklist(checklistId, patch) {
    const payload = await checklistService.updateChecklist(checklistId, patch);
    const updated = extractPayload(payload);
    const index = activeCard.value.checklists.findIndex((item) => item.id === checklistId);
    if (index >= 0) {
      activeCard.value.checklists[index] = updated;
    }
    syncCardSummaryToBoard();
    return updated;
  }

  async function deleteChecklist(checklistId) {
    await checklistService.deleteChecklist(checklistId);
    activeCard.value.checklists = activeCard.value.checklists.filter(
      (item) => item.id !== checklistId,
    );
    syncCardSummaryToBoard();
  }

  async function addChecklistItem(checklistId, content) {
    const payload = await checklistService.createChecklistItem(checklistId, { content });
    const item = extractPayload(payload);
    const checklist = activeCard.value.checklists.find((row) => row.id === checklistId);
    if (checklist) {
      checklist.items = checklist.items || [];
      checklist.items.push(item);
    }
    syncCardSummaryToBoard();
    return item;
  }

  async function updateChecklistItem(itemId, patch) {
    const payload = await checklistService.updateChecklistItem(itemId, patch);
    const updated = extractPayload(payload);
    for (const checklist of activeCard.value.checklists) {
      const idx = (checklist.items || []).findIndex((item) => item.id === itemId);
      if (idx >= 0) {
        checklist.items[idx] = updated;
        break;
      }
    }
    syncCardSummaryToBoard();
    return updated;
  }

  async function deleteChecklistItem(itemId) {
    await checklistService.deleteChecklistItem(itemId);
    for (const checklist of activeCard.value.checklists) {
      checklist.items = (checklist.items || []).filter((item) => item.id !== itemId);
    }
    syncCardSummaryToBoard();
  }

  async function toggleLabel(label) {
    if (!activeCard.value?.id) {
      return null;
    }

    const alreadyAssigned = activeCard.value.labels.some((row) => row.id === label.id);
    if (alreadyAssigned) {
      await labelService.unassignLabel(activeCard.value.id, label.id);
      activeCard.value.labels = activeCard.value.labels.filter(
        (row) => row.id !== label.id,
      );
    } else {
      await labelService.assignLabel(activeCard.value.id, label.id);
      activeCard.value.labels.push(label);
    }
    syncCardSummaryToBoard();
  }

  async function createBoardLabel(name, color_hex) {
    const boardStore = useBoardStore();
    if (!boardStore.currentBoard?.id) {
      return null;
    }

    const payload = await labelService.createLabel(boardStore.currentBoard.id, {
      name,
      color_hex,
    });
    const label = extractPayload(payload);
    boardStore.setBoardLabels([...(boardStore.currentBoard.labels || []), label]);
    return label;
  }

  async function refreshImages() {
    if (!activeCard.value?.id) {
      return [];
    }
    const payload = await imageService.getCardImages(activeCard.value.id);
    const images = extractPayload(payload);
    activeCard.value.images = Array.isArray(images) ? images : images?.items || [];
    syncCardSummaryToBoard();
    return activeCard.value.images;
  }

  async function uploadImage(file) {
    if (!activeCard.value?.id || !file) {
      return null;
    }
    await imageService.uploadCardImage(activeCard.value.id, file);
    const refreshed = await cardService.getCard(activeCard.value.id);
    activeCard.value = normalizeCardDetail(extractPayload(refreshed));
    syncCardSummaryToBoard();
    return activeCard.value.images;
  }

  async function deleteImage(imageId) {
    await imageService.deleteImage(imageId);
    activeCard.value.images = activeCard.value.images.filter((img) => img.id !== imageId);
    if (activeCard.value.cover_image_id === imageId) {
      const fallback = activeCard.value.images[activeCard.value.images.length - 1];
      activeCard.value.cover_image_id = fallback?.id || null;
    }
    syncCardSummaryToBoard();
  }

  async function setCover(imageId) {
    if (!activeCard.value?.id) {
      return;
    }
    await imageService.setCardCover(activeCard.value.id, imageId);
    const refreshed = await cardService.getCard(activeCard.value.id);
    activeCard.value = normalizeCardDetail(extractPayload(refreshed));
    syncCardSummaryToBoard();
  }

  async function fetchTimeSummary(cardId = activeCard.value?.id) {
    if (!cardId) {
      return null;
    }
    const payload = await timerService.getCardTime(cardId);
    const summary = extractPayload(payload);
    if (activeCard.value?.id === cardId) {
      activeCard.value.time_summary = summary;
      activeCard.value.total_tracked_seconds =
        summary.total_seconds ??
        summary.total_tracked_seconds ??
        activeCard.value.total_tracked_seconds;
      syncCardSummaryToBoard();
    }
    return summary;
  }

  async function assignUser(userId) {
    if (!activeCard.value?.id) {
      return;
    }
    await cardService.assignUser(activeCard.value.id, userId);
    const refreshed = await cardService.getCard(activeCard.value.id);
    activeCard.value = normalizeCardDetail(extractPayload(refreshed));
    syncCardSummaryToBoard();
  }

  async function unassignUser(userId) {
    if (!activeCard.value?.id) {
      return;
    }
    await cardService.unassignUser(activeCard.value.id, userId);
    activeCard.value.assignees = (activeCard.value.assignees || []).filter((user) => user.id !== userId);
    syncCardSummaryToBoard();
  }

  return {
    isModalOpen,
    isLoading,
    activeCardId,
    activeCard,
    hasActiveCard,
    openModal,
    closeModal,
    saveCard,
    deleteCard,
    addChecklist,
    updateChecklist,
    deleteChecklist,
    addChecklistItem,
    updateChecklistItem,
    deleteChecklistItem,
    toggleLabel,
    createBoardLabel,
    refreshImages,
    uploadImage,
    deleteImage,
    setCover,
    fetchTimeSummary,
    assignUser,
    unassignUser,
  };
});

<template>
  <section class="container section">
    <div v-if="boardStore.isLoading" class="loading-row">
      <LoadingSpinner />
    </div>

    <template v-else-if="boardStore.currentBoard">
      <BoardHeader :board="boardStore.currentBoard" :board-id="props.boardId" />

      <div
        ref="listsWrapRef"
        class="lists-wrap content"
        :class="{ dragging: isBackgroundDragging }"
        @mousedown="startBackgroundDrag"
        @mousemove="onBackgroundDrag"
        @mouseleave="stopBackgroundDrag"
      >
        <draggable
          v-model="boardStore.currentBoard.lists"
          item-key="id"
          class="lists"
          :animation="140"
          handle=".list-drag-handle"
          @start="listDragSnapshot = boardStore.snapshotLists()"
          @end="onListDragEnd"
        >
          <template #item="{ element }">
            <ListColumn
              :list="element"
              :active-timer-card-id="timerStore.activeCardId"
              @add-card="onAddCard"
              @open-card="openCard"
              @delete-list="onDeleteList"
              @rename-list="onRenameList"
              @card-drag-start="cardDragSnapshot = boardStore.snapshotLists()"
              @card-drag-end="onCardDragEnd"
            />
          </template>
        </draggable>
        <AddListForm @create="onCreateList" />
      </div>

      <CardModal />
    </template>
  </section>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import draggable from "vuedraggable";
import { useRoute, useRouter } from "vue-router";
import BoardHeader from "@/components/kanban/BoardHeader.vue";
import ListColumn from "@/components/kanban/ListColumn.vue";
import AddListForm from "@/components/kanban/AddListForm.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import CardModal from "@/components/cards/CardModal.vue";
import { useBoardStore } from "@/stores/boardStore";
import { useCardStore } from "@/stores/cardStore";
import { useTimerStore } from "@/stores/timerStore";

const props = defineProps({
  boardId: {
    type: [String, Number],
    required: true,
  },
});

const route = useRoute();
const router = useRouter();
const boardStore = useBoardStore();
const cardStore = useCardStore();
const timerStore = useTimerStore();

const listDragSnapshot = ref(null);
const cardDragSnapshot = ref(null);
const listsWrapRef = ref(null);
const isBackgroundDragging = ref(false);
const dragStartX = ref(0);
const dragStartScrollLeft = ref(0);

const loadBoard = async () => {
  await boardStore.loadBoard(props.boardId);
  const routeCardId = getRouteCardId();
  if (routeCardId) {
    await openCardFromRoute(routeCardId);
  } else if (cardStore.isModalOpen) {
    cardStore.closeModal();
  }
};

onMounted(() => {
  loadBoard();
  window.addEventListener("mouseup", stopBackgroundDrag);
});

onBeforeUnmount(() => {
  window.removeEventListener("mouseup", stopBackgroundDrag);
});

watch(
  () => props.boardId,
  () => loadBoard(),
);

watch(
  () => route.query.card,
  async () => {
    const routeCardId = getRouteCardId();
    if (!routeCardId) {
      if (cardStore.isModalOpen) {
        cardStore.closeModal();
      }
      return;
    }
    await openCardFromRoute(routeCardId);
  },
);

watch(
  () => cardStore.isModalOpen,
  async (isOpen) => {
    if (!isOpen && getRouteCardId()) {
      await syncCardQuery(null);
    }
  },
);

async function onCreateList(title) {
  await boardStore.createList(title);
}

async function onAddCard({ listId, title }) {
  await boardStore.createCard(listId, { title });
}

async function openCard(cardId) {
  await cardStore.openModal(cardId);
  await syncCardQuery(cardId);
}

async function openCardFromRoute(cardId) {
  if (!isCardInCurrentBoard(cardId)) {
    await syncCardQuery(null);
    return;
  }
  if (cardStore.isModalOpen && cardStore.activeCard?.id === cardId) {
    return;
  }
  await cardStore.openModal(cardId);
}

function isCardInCurrentBoard(cardId) {
  return (boardStore.currentBoard?.lists || []).some((list) =>
    (list.cards || []).some((card) => Number(card.id) === Number(cardId)),
  );
}

function getRouteCardId() {
  const raw = Array.isArray(route.query.card) ? route.query.card[0] : route.query.card;
  const value = Number(raw);
  if (!Number.isFinite(value) || value <= 0) {
    return null;
  }
  return value;
}

async function syncCardQuery(cardId) {
  const currentCardId = getRouteCardId();
  const nextCardId = cardId ? Number(cardId) : null;
  if (currentCardId === nextCardId) {
    return;
  }
  const nextQuery = { ...route.query };
  if (!nextCardId) {
    delete nextQuery.card;
  } else {
    nextQuery.card = String(nextCardId);
  }
  await router.replace({
    name: "board",
    params: { boardId: props.boardId },
    query: nextQuery,
  });
}

async function onRenameList({ listId, title }) {
  await boardStore.updateList(listId, { title });
}

async function onDeleteList(listId) {
  await boardStore.deleteList(listId);
}

async function onListDragEnd(evt) {
  if (evt.oldIndex === evt.newIndex) {
    return;
  }
  await boardStore.persistListReorder(listDragSnapshot.value);
}

async function onCardDragEnd(payload) {
  if (
    payload.oldIndex === payload.newIndex &&
    payload.fromListId === payload.toListId
  ) {
    return;
  }

  await boardStore.persistCardMove({
    ...payload,
    snapshot: cardDragSnapshot.value,
  });
}

function shouldSkipBackgroundDrag(target) {
  if (!target || !(target instanceof Element)) {
    return true;
  }

  if (
    target.closest(".column") ||
    target.closest(".card") ||
    target.closest(".panel") ||
    target.closest("button") ||
    target.closest("input") ||
    target.closest("textarea") ||
    target.closest("select") ||
    target.closest("a")
  ) {
    return true;
  }

  return false;
}

function startBackgroundDrag(event) {
  if (event.button !== 0) {
    return;
  }
  if (shouldSkipBackgroundDrag(event.target)) {
    return;
  }

  const container = listsWrapRef.value;
  if (!container) {
    return;
  }

  isBackgroundDragging.value = true;
  dragStartX.value = event.clientX;
  dragStartScrollLeft.value = container.scrollLeft;
}

function onBackgroundDrag(event) {
  if (!isBackgroundDragging.value) {
    return;
  }
  const container = listsWrapRef.value;
  if (!container) {
    return;
  }

  event.preventDefault();
  const delta = event.clientX - dragStartX.value;
  container.scrollLeft = dragStartScrollLeft.value - delta;
}

function stopBackgroundDrag() {
  isBackgroundDragging.value = false;
}
</script>

<style scoped lang="less">
.section {
  display: grid;
  gap: @space-4;
}

.loading-row {
  display: flex;
  justify-content: center;
}

.lists-wrap {
  display: flex;
  gap: @space-3;
  overflow-x: auto;
  align-items: start;
  cursor: grab;
  scrollbar-width: thin;
  scrollbar-color: rgba(15, 23, 42, 0.2) transparent;
}

.lists-wrap::-webkit-scrollbar {
  height: calc(10px * @ui-scale);
}

.lists-wrap::-webkit-scrollbar-track {
  background: transparent;
}

.lists-wrap::-webkit-scrollbar-thumb {
  background: rgba(15, 23, 42, 0.2);
  border-radius: calc(999px * @ui-scale);
}

.lists-wrap::-webkit-scrollbar-thumb:hover {
  background: rgba(15, 23, 42, 0.32);
}

.lists-wrap::-webkit-scrollbar-button {
  display: none;
  width: 0;
  height: 0;
}

.lists-wrap.dragging {
  cursor: grabbing;
  user-select: none;
}

.lists {
  display: flex;
  gap: @space-3;
  align-items: flex-start;
}
</style>


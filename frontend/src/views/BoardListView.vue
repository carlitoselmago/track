<template>
  <section class="container section">
    <div class="content">
      <header class="header">
        <h1>Your Boards</h1>
        <RouterLink
          v-if="authStore.user?.is_system_admin"
          to="/admin/users"
          class="admin-link"
        >
          Manage users
        </RouterLink>
      </header>

      <div v-if="boardStore.isLoading" class="loading-row">
        <LoadingSpinner />
      </div>

      <template v-else>
        <p v-if="boardStore.boards.length === 0" class="empty-note">
          No boards yet. Create your first board to begin organizing cards.
        </p>

        <div class="grid">
          <draggable
            v-model="boardStore.boards"
            item-key="id"
            tag="div"
            class="board-list-draggable"
            handle=".board-drag-handle"
            :animation="140"
            :delay="180"
            :delay-on-touch-only="true"
            :touch-start-threshold="4"
            @end="onBoardsDragEnd"
          >
            <template #item="{ element }">
              <BoardCard
                :board="element"
                @open="openBoard"
                @edit="startEditBoard"
                @delete="confirmDeleteBoard"
              />
            </template>
          </draggable>

          <button type="button" class="add-new-tile" @click="isCreateModalOpen = true">
            <span class="plus">+</span>
            <span>Add new</span>
          </button>
        </div>
      </template>

      <BaseModal v-model="isCreateModalOpen" title="Create board">
        <CreateBoardForm @create="handleCreateBoard" />
      </BaseModal>

      <BaseModal v-model="isEditModalOpen" title="Edit board">
        <form class="edit-form" @submit.prevent="saveBoardEdit">
          <BaseInput v-model="editName" label="Name" />
          <BaseInput v-model="editDescription" label="Description" type="textarea" />
          <div class="color-field">
            <span>Color</span>
            <label class="color-picker">
              <input v-model="editColor" type="color" class="color-input" aria-label="Board color" />
              <span class="swatch" :style="{ background: editColor }" />
              <span class="hex">{{ editColor.toUpperCase() }}</span>
            </label>
          </div>
          <div class="edit-actions">
            <BaseButton variant="subtle" @click="isEditModalOpen = false">Cancel</BaseButton>
            <BaseButton type="submit">Save changes</BaseButton>
          </div>
        </form>
      </BaseModal>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import draggable from "vuedraggable";
import { RouterLink, useRouter } from "vue-router";
import CreateBoardForm from "@/components/boards/CreateBoardForm.vue";
import BoardCard from "@/components/boards/BoardCard.vue";
import BaseModal from "@/components/common/BaseModal.vue";
import BaseInput from "@/components/common/BaseInput.vue";
import BaseButton from "@/components/common/BaseButton.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import { useBoardStore } from "@/stores/boardStore";
import { useAuthStore } from "@/stores/authStore";

const router = useRouter();
const boardStore = useBoardStore();
const authStore = useAuthStore();
const isCreateModalOpen = ref(false);
const isEditModalOpen = ref(false);
const editBoardId = ref(null);
const editName = ref("");
const editDescription = ref("");
const editColor = ref("#16A34A");

onMounted(() => {
  loadBoards();
});

function boardOrderStorageKey() {
  const userId = authStore.user?.id || "anon";
  return `track.boards.order.${userId}`;
}

function saveBoardOrderToStorage() {
  if (typeof window === "undefined") {
    return;
  }
  const ids = (boardStore.boards || []).map((board) => Number(board.id));
  window.localStorage.setItem(boardOrderStorageKey(), JSON.stringify(ids));
}

function applyBoardOrderFromStorage() {
  if (typeof window === "undefined" || boardStore.boards.length < 2) {
    return;
  }

  const raw = window.localStorage.getItem(boardOrderStorageKey());
  if (!raw) {
    return;
  }

  let savedIds = [];
  try {
    savedIds = JSON.parse(raw);
  } catch {
    return;
  }

  if (!Array.isArray(savedIds) || !savedIds.length) {
    return;
  }

  const orderIndex = new Map(savedIds.map((id, index) => [Number(id), index]));
  boardStore.boards.sort((a, b) => {
    const aIndex = orderIndex.has(Number(a.id)) ? orderIndex.get(Number(a.id)) : Number.MAX_SAFE_INTEGER;
    const bIndex = orderIndex.has(Number(b.id)) ? orderIndex.get(Number(b.id)) : Number.MAX_SAFE_INTEGER;
    if (aIndex !== bIndex) {
      return aIndex - bIndex;
    }
    return Number(a.id) - Number(b.id);
  });
}

async function loadBoards() {
  await boardStore.fetchBoards();
  applyBoardOrderFromStorage();
}

async function handleCreateBoard(payload) {
  const board = await boardStore.createBoard(payload);
  saveBoardOrderToStorage();
  isCreateModalOpen.value = false;
  if (board?.id) {
    await router.push({ name: "board", params: { boardId: board.id } });
  }
}

async function openBoard(boardId) {
  await router.push({ name: "board", params: { boardId } });
}

function startEditBoard(board) {
  editBoardId.value = board.id;
  editName.value = board.name || "";
  editDescription.value = board.description || "";
  editColor.value = board.color_hex || "#16A34A";
  isEditModalOpen.value = true;
}

async function saveBoardEdit() {
  if (!editBoardId.value) {
    return;
  }
  await boardStore.updateBoard(editBoardId.value, {
    name: editName.value.trim(),
    description: editDescription.value.trim(),
    color_hex: editColor.value,
  });
  isEditModalOpen.value = false;
}

async function confirmDeleteBoard(board) {
  const ok = window.confirm(`Delete board "${board.name}"?`);
  if (!ok) {
    return;
  }
  await boardStore.deleteBoard(board.id);
  saveBoardOrderToStorage();
}

function onBoardsDragEnd(event) {
  if (event.oldIndex === event.newIndex) {
    return;
  }
  saveBoardOrderToStorage();
}
</script>

<style scoped lang="less">
.section {
  display: grid;
  gap: @space-4;
}

.header h1 {
  margin: 0;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: @space-2;
}

.admin-link {
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(999px * @ui-scale);
  padding: calc(7px * @ui-scale) calc(12px * @ui-scale);
  font-size: calc(13px * @ui-scale);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(calc(260px * @ui-scale), 1fr));
  gap: @space-3;
  align-items: stretch;
}

.board-list-draggable {
  display: contents;
}

.add-new-tile {
  border: calc(1px * @ui-scale) dashed @border;
  border-radius: @radius;
  min-height: calc(116px * @ui-scale);
  background: #fff;
  display: grid;
  place-content: center;
  gap: calc(6px * @ui-scale);
  color: @text-muted;
  cursor: pointer;
  transition: border-color 140ms ease, background 140ms ease, color 140ms ease;
  @media (prefers-color-scheme: dark) {
    background: @bg-dark;
    border-color: @surface-muted-dark;
    color: @text-muted-dark;
  }
}

.add-new-tile:hover {
  border-color: color-mix(in srgb, @primary 45%, @border);
  background: @surface-muted;
  color: @text;
}

.plus {
  font-size: calc(22px * @ui-scale);
  line-height: 1;
}

.empty-note {
  margin: 0 0 @space-3;
  color: @text-muted;
}

.loading-row {
  display: flex;
  justify-content: center;
  padding: @space-4;
}

.edit-form {
  display: grid;
  gap: @space-3;
}

.color-field {
  display: grid;
  gap: calc(6px * @ui-scale);
  font-size: calc(12px * @ui-scale);
  color: @text-muted;
}

.color-picker {
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(8px * @ui-scale);
  background: #fff;
  min-width: calc(150px * @ui-scale);
  padding: calc(6px * @ui-scale) calc(10px * @ui-scale);
  display: inline-flex;
  align-items: center;
  gap: calc(8px * @ui-scale);
  position: relative;
  cursor: pointer;
}

.color-picker:hover {
  background: @surface-muted;
}

.color-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.swatch {
  width: calc(18px * @ui-scale);
  height: calc(18px * @ui-scale);
  border-radius: calc(999px * @ui-scale);
  border: calc(1px * @ui-scale) solid rgba(15, 23, 42, 0.2);
  flex-shrink: 0;
}

.hex {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: calc(12px * @ui-scale);
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: @space-2;
}
</style>

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

      <CreateBoardForm @create="handleCreateBoard" />

      <div v-if="boardStore.isLoading" class="loading-row">
        <LoadingSpinner />
      </div>

      <EmptyState
        v-else-if="boardStore.boards.length === 0"
        title="No boards yet"
        description="Create your first board to begin organizing cards."
      />

      <div v-else class="grid">
        <BoardCard
          v-for="board in boardStore.boards"
          :key="board.id"
          :board="board"
          @open="openBoard"
          @edit="startEditBoard"
          @delete="confirmDeleteBoard"
        />
      </div>

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
import { RouterLink, useRouter } from "vue-router";
import CreateBoardForm from "@/components/boards/CreateBoardForm.vue";
import BoardCard from "@/components/boards/BoardCard.vue";
import BaseModal from "@/components/common/BaseModal.vue";
import BaseInput from "@/components/common/BaseInput.vue";
import BaseButton from "@/components/common/BaseButton.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import EmptyState from "@/components/common/EmptyState.vue";
import { useBoardStore } from "@/stores/boardStore";
import { useAuthStore } from "@/stores/authStore";

const router = useRouter();
const boardStore = useBoardStore();
const authStore = useAuthStore();
const isEditModalOpen = ref(false);
const editBoardId = ref(null);
const editName = ref("");
const editDescription = ref("");
const editColor = ref("#16A34A");

onMounted(() => {
  boardStore.fetchBoards();
});

async function handleCreateBoard(payload) {
  const board = await boardStore.createBoard(payload);
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
}
</script>

<style scoped lang="less">
.section {
  display: grid;
  gap: var(--space-4);
}

.header h1 {
  margin: 0;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.admin-link {
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: calc(999px * var(--ui-scale));
  padding: calc(7px * var(--ui-scale)) calc(12px * var(--ui-scale));
  background: #fff;
  font-size: calc(13px * var(--ui-scale));
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(calc(260px * var(--ui-scale)), 1fr));
  gap: var(--space-3);
}

.loading-row {
  display: flex;
  justify-content: center;
  padding: var(--space-4);
}

.edit-form {
  display: grid;
  gap: var(--space-3);
}

.color-field {
  display: grid;
  gap: calc(6px * var(--ui-scale));
  font-size: calc(12px * var(--ui-scale));
  color: var(--text-muted);
}

.color-picker {
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: calc(8px * var(--ui-scale));
  background: #fff;
  min-width: calc(150px * var(--ui-scale));
  padding: calc(6px * var(--ui-scale)) calc(10px * var(--ui-scale));
  display: inline-flex;
  align-items: center;
  gap: calc(8px * var(--ui-scale));
  position: relative;
  cursor: pointer;
}

.color-picker:hover {
  background: var(--surface-muted);
}

.color-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.swatch {
  width: calc(18px * var(--ui-scale));
  height: calc(18px * var(--ui-scale));
  border-radius: calc(999px * var(--ui-scale));
  border: calc(1px * var(--ui-scale)) solid rgba(15, 23, 42, 0.2);
  flex-shrink: 0;
}

.hex {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: calc(12px * var(--ui-scale));
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
}
</style>


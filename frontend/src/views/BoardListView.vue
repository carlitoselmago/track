<template>
  <section class="container section">
    <header class="header">
      <h1>Your Boards</h1>
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
      <BoardCard v-for="board in boardStore.boards" :key="board.id" :board="board" />
    </div>
  </section>
</template>

<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import CreateBoardForm from "@/components/boards/CreateBoardForm.vue";
import BoardCard from "@/components/boards/BoardCard.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import EmptyState from "@/components/common/EmptyState.vue";
import { useBoardStore } from "@/stores/boardStore";

const router = useRouter();
const boardStore = useBoardStore();

onMounted(() => {
  boardStore.fetchBoards();
});

async function handleCreateBoard(payload) {
  const board = await boardStore.createBoard(payload);
  if (board?.id) {
    await router.push({ name: "board", params: { boardId: board.id } });
  }
}
</script>

<style scoped>
.section {
  display: grid;
  gap: var(--space-4);
}

.header h1 {
  margin: 0;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--space-3);
}

.loading-row {
  display: flex;
  justify-content: center;
  padding: var(--space-4);
}
</style>

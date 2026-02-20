<template>
  <RouterLink :to="{ name: 'board', params: { boardId: board.id } }" class="board-card">
    <span class="swatch" :style="{ background: board.color_hex || '#16A34A' }" />
    <div>
      <h3>{{ board.name }}</h3>
      <p>{{ board.description || "No description" }}</p>
    </div>
  </RouterLink>
</template>

<script setup>
import { RouterLink } from "vue-router";

defineProps({
  board: {
    type: Object,
    required: true,
  },
});
</script>

<style scoped>
.board-card {
  display: flex;
  gap: var(--space-3);
  align-items: center;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-4);
  transition: transform 140ms ease;
}

.board-card:hover {
  transform: translateY(-2px);
}

.swatch {
  width: 22px;
  height: 22px;
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

h3 {
  margin: 0 0 4px;
}

p {
  margin: 0;
  font-size: 13px;
  color: var(--text-muted);
}
</style>

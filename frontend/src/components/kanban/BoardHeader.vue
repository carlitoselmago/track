<template>
  <header class="board-header" :style="{ borderColor: board?.color_hex || '#16A34A' }">
    <div class="left">
      <span class="dot" :style="{ background: board?.color_hex || '#16A34A' }" />
      <div>
        <h1>{{ board?.name || "Board" }}</h1>
        <p>{{ board?.description || "No description" }}</p>
      </div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  board: {
    type: Object,
    required: false,
    default: null,
  },
});
</script>

<style scoped>
.board-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--surface);
  border: 1px solid var(--border);
  border-left-width: 5px;
  border-radius: var(--radius);
  padding: var(--space-4);
}

.left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
}

h1 {
  margin: 0;
  font-size: 22px;
}

p {
  margin: 4px 0 0;
  color: var(--text-muted);
  font-size: 13px;
}
</style>

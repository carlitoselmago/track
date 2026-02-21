<template>
  <article class="board-card" @click="$emit('open', board.id)">
    <span class="swatch" :style="{ background: board.color_hex || '#16A34A' }" />
    <div class="content">
      <h3>{{ board.name }}</h3>
      <p v-if="board.description">{{ board.description }}</p>
    </div>
    <div class="actions">
      <button type="button" class="action-btn" @click.stop="$emit('edit', board)">Edit</button>
      <button type="button" class="action-btn danger" @click.stop="$emit('delete', board)">Delete</button>
    </div>
  </article>
</template>

<script setup>
defineProps({
  board: {
    type: Object,
    required: true,
  },
});

defineEmits(["open", "edit", "delete"]);
</script>

<style scoped lang="less">
.board-card {
  display: flex;
  gap: var(--space-3);
  align-items: center;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-4);
  transition: transform 140ms ease;
  cursor: pointer;
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

.content {
  min-width: 0;
  flex: 1;
}

h3 {
  margin: 0 0 4px;
}

p {
  margin: 0;
  font-size: 13px;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.action-btn {
  border: 1px solid var(--border);
  background: #fff;
  border-radius: 8px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
}

.action-btn.danger {
  color: var(--danger);
}
</style>


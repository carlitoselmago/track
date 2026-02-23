<template>
  <article class="board-card" @click="$emit('open', board.id)">
    <button
      type="button"
      class="board-drag-handle"
      aria-label="Drag board"
      title="Drag board"
      @click.stop
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M9 6h6M9 12h6M9 18h6" />
      </svg>
    </button>
    <span class="swatch" :style="{ background: board.color_hex || '#16A34A' }" />
    <div class="content">
      <h3>{{ board.name }}</h3>
      <p v-if="board.description">{{ board.description }}</p>
    </div>
    <div class="actions">
      <button type="button" class="action-btn btn" @click.stop="$emit('edit', board)">Edit</button>
      <button type="button" class="action-btn btn danger" @click.stop="$emit('delete', board)">Delete</button>
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
  gap: @space-3;
  align-items: flex-start;
 
  border-radius: @radius;
  padding: @space-4;
  transition: transform 140ms ease;
  cursor: pointer;
  h3{
    margin: 0px;
    @media (prefers-color-scheme: dark) {
      color:@text-dark;
    }
  }
}

.board-card:hover {
  transform: translateY(calc(-2px * @ui-scale));
}

.board-drag-handle {
  width: calc(28px * @ui-scale);
  height: calc(28px * @ui-scale);
  min-width: calc(28px * @ui-scale);
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(8px * @ui-scale);
  background: transparent;
  color: @text-muted;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  padding: 0;
  flex-shrink: 0;
}

.board-drag-handle:active {
  cursor: grabbing;
}

.board-drag-handle svg {
  width: calc(14px * @ui-scale);
  height: calc(14px * @ui-scale);
  fill: none;
  stroke: currentColor;
  stroke-width: 2.1;
  stroke-linecap: round;
}

.swatch {
  width: calc(22px * @ui-scale);
  height: calc(22px * @ui-scale);
  border-radius: calc(999px * @ui-scale);
  border: calc(1px * @ui-scale) solid rgba(0, 0, 0, 0.1);
}

.content {
  min-width: 0;
  flex: 1;
}

h3 {
  margin: 0 0 calc(4px * @ui-scale);
}

p {
  margin: 0;
  font-size: calc(13px * @ui-scale);
  color: @text-muted;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: calc(6px * @ui-scale);
  margin-left: auto;
}

.action-btn {

 
  border-radius: calc(8px * @ui-scale);
  padding: calc(4px * @ui-scale) calc(8px * @ui-scale);
  font-size: calc(12px * @ui-scale);
  cursor: pointer;
}

.action-btn.danger {
  color: @danger;
}
</style>




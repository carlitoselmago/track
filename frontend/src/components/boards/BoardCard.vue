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
  gap: @space-3;
  align-items: center;
  background: @surface;
  border: calc(1px * @ui-scale) solid @border;
  border-radius: @radius;
  padding: @space-4;
  transition: transform 140ms ease;
  cursor: pointer;
  h3{
    margin: 0px;
  }
}

.board-card:hover {
  transform: translateY(calc(-2px * @ui-scale));
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
}

.action-btn {
  border: calc(1px * @ui-scale) solid @border;
  background: #fff;
  border-radius: calc(8px * @ui-scale);
  padding: calc(4px * @ui-scale) calc(8px * @ui-scale);
  font-size: calc(12px * @ui-scale);
  cursor: pointer;
}

.action-btn.danger {
  color: @danger;
}
</style>




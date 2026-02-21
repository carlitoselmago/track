<template>
  <header class="board-header" :style="{ borderColor: board?.color_hex || '#16A34A' }">
    <div class="left">
      <span class="dot" :style="{ background: board?.color_hex || '#16A34A' }" />
      <div>
        <h1>{{ board?.name || "Board" }}</h1>
        <p v-if="board?.description">{{ board.description }}</p>
      </div>
    </div>
    <div class="nav-links">
      <RouterLink
        :to="{ name: 'board', params: { boardId: resolvedBoardId } }"
        class="link"
        :class="{ active: route?.name === 'board' }"
      >
        Kanban
      </RouterLink>
      <RouterLink
        :to="{ name: 'board-calendar', params: { boardId: resolvedBoardId } }"
        class="link"
        :class="{ active: route?.name === 'board-calendar' }"
      >
        Calendar
      </RouterLink>
    </div>
  </header>
</template>

<script setup>
import { computed } from "vue";
import { RouterLink, useRoute } from "vue-router";

const route = useRoute();

const props = defineProps({
  boardId: {
    type: [String, Number],
    default: null,
  },
  board: {
    type: Object,
    required: false,
    default: null,
  },
});

const resolvedBoardId = computed(() => props.boardId ?? props.board?.id ?? "");
</script>

<style scoped lang="less">
.board-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(0, 0, 0, 0.2);
  padding: var(--space-3) var(--space-6);
 
  a{
    background-color: white;
  }
  h1{
    font-size: calc(20px * var(--ui-scale));
    display: inline;
    margin-right: calc(10px * var(--ui-scale));
    color:white
  }
  p{
    margin: 0;
    color:white;
    display: inline;
    opacity: 0.4;
  }
}

.left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.dot {
  width: calc(12px * var(--ui-scale));
  height: calc(12px * var(--ui-scale));
  border-radius: calc(999px * var(--ui-scale));
}

h1 {
  margin: 0;
  font-size: calc(22px * var(--ui-scale));
}

p {
  margin: calc(4px * var(--ui-scale)) 0 0;
  color: var(--text-muted);
  font-size: calc(13px * var(--ui-scale));
}

.nav-links {
  display: flex;
  gap: var(--space-2);
}

.link {
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: calc(999px * var(--ui-scale));
  padding: calc(6px * var(--ui-scale)) calc(12px * var(--ui-scale));
  font-size: calc(13px * var(--ui-scale));
  color: var(--text-muted);
}

.link.active {
  border-color: var(--primary);
  color: var(--primary);
  font-weight: 700;
}
</style>



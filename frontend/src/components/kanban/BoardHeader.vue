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
    font-size: 20px;
    display: inline;
    margin-right: 10px;
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

.nav-links {
  display: flex;
  gap: var(--space-2);
}

.link {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 13px;
  color: var(--text-muted);
}

.link.active {
  border-color: var(--primary);
  color: var(--primary);
  font-weight: 700;
}
</style>


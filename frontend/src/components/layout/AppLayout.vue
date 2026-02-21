<template>
  <TopNav />
  <main class="page" :style="pageStyle">
    <RouterView />
  </main>
</template>

<script setup>
import { computed } from "vue";
import { RouterView, useRoute } from "vue-router";
import { useBoardStore } from "@/stores/boardStore";
import TopNav from "./TopNav.vue";

const route = useRoute();
const boardStore = useBoardStore();

const pageStyle = computed(() => {
  const boardRoutes = new Set(["board", "board-calendar"]);
  if (!boardRoutes.has(route.name)) {
    return {};
  }

  const color = boardStore.currentBoard?.color_hex;
  if (!color) {
    return {};
  }

  return {
    backgroundColor: color,
  };
});
</script>

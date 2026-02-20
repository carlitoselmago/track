<template>
  <div v-if="uiStore.errorMessage" class="error-banner">
    <div class="container inner">
      <span>{{ uiStore.errorMessage }}</span>
      <button type="button" class="dismiss" @click="uiStore.clearError">x</button>
    </div>
  </div>
</template>

<script setup>
import { useUiStore } from "@/stores/uiStore";

const uiStore = useUiStore();
</script>

<style scoped>
.error-banner {
  background: #fee2e2;
  color: #7f1d1d;
  border-bottom: 1px solid #fecaca;
}

.inner {
  min-height: 42px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.dismiss {
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-size: 16px;
}
</style>

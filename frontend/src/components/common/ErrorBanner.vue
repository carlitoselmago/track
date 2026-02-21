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

<style scoped lang="less">
.error-banner {
  background: #fee2e2;
  color: #7f1d1d;
  border-bottom: calc(1px * @ui-scale) solid #fecaca;
}

.inner {
  min-height: calc(42px * @ui-scale);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: @space-3;
}

.dismiss {
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-size: calc(16px * @ui-scale);
}
</style>




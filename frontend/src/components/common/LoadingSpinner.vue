<template>
  <div class="spinner" />
</template>

<style scoped lang="less">
.spinner {
  width: calc(22px * var(--ui-scale));
  height: calc(22px * var(--ui-scale));
  border-radius: calc(999px * var(--ui-scale));
  border: calc(3px * var(--ui-scale)) solid var(--surface-muted);
  border-top-color: var(--primary);
  animation: spin 700ms linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>



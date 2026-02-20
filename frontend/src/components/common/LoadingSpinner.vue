<template>
  <div class="spinner" />
</template>

<style scoped lang="less">
.spinner {
  width: 22px;
  height: 22px;
  border-radius: 999px;
  border: 3px solid var(--surface-muted);
  border-top-color: var(--primary);
  animation: spin 700ms linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>


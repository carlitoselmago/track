<template>
  <div class="spinner" />
</template>

<style scoped lang="less">
.spinner {
  width: calc(22px * @ui-scale);
  height: calc(22px * @ui-scale);
  border-radius: calc(999px * @ui-scale);
  border: calc(3px * @ui-scale) solid @surface-muted;
  border-top-color: @primary;
  animation: spin 700ms linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>




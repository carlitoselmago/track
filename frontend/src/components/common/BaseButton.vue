<template>
  <button
    class="base-button"
    :class="{
      danger: variant === 'danger',
      subtle: variant === 'subtle',
      block,
    }"
    :type="type"
    :disabled="disabled || loading"
  >
    <span v-if="loading">...</span>
    <slot v-else />
  </button>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: "button",
  },
  variant: {
    type: String,
    default: "primary",
  },
  loading: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  block: {
    type: Boolean,
    default: false,
  },
});
</script>

<style scoped lang="less">
.base-button {
  border: 0;
  border-radius: calc(8px * @ui-scale);
  background: @primary;
  color: #fff;
  font-weight: 600;
  padding: calc(10px * @ui-scale) calc(14px * @ui-scale);
  cursor: pointer;
  transition: transform 120ms ease;
}

.base-button:hover:not(:disabled) {
  transform: translateY(calc(-1px * @ui-scale));
}

.base-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.base-button.danger {
  background: @danger;
}



.base-button.block {
  width: 100%;
}
</style>



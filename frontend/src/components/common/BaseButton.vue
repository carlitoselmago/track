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

<style scoped>
.base-button {
  border: 0;
  border-radius: 8px;
  background: var(--primary);
  color: #fff;
  font-weight: 600;
  padding: 10px 14px;
  cursor: pointer;
  transition: transform 120ms ease;
}

.base-button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.base-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.base-button.danger {
  background: var(--danger);
}

.base-button.subtle {
  background: var(--surface-muted);
  color: var(--text);
}

.base-button.block {
  width: 100%;
}
</style>

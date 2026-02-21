<template>
  <teleport to="body">
    <div v-if="modelValue" class="overlay" @click.self="$emit('update:modelValue', false)">
      <section class="modal">
        <header class="modal-header">
          <slot name="title">
            <h3 class="modal-title">{{ title }}</h3>
          </slot>
          <div class="header-actions">
            <slot name="header-actions"></slot>
            <button
              type="button"
              class="close"
              aria-label="Close"
              @click="$emit('update:modelValue', false)"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M6 6l12 12M18 6L6 18" />
              </svg>
            </button>
          </div>
        </header>
        <div class="modal-body">
          <slot />
        </div>
      </section>
    </div>
  </teleport>
</template>

<script setup>
defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: "",
  },
});

defineEmits(["update:modelValue"]);
</script>

<style scoped lang="less">
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: grid;
  place-items: center;
  padding: var(--space-4);
  z-index: 20;
}

.modal {
  width: min(760px, 100%);
  max-height: calc(100vh - 48px);
  overflow: auto;
  border-radius: 14px;
  background: var(--surface);
  box-shadow: var(--shadow);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  padding: var(--space-4);
  border-bottom: 1px solid var(--border);
}

.modal-title {
  margin: 0;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal-body {
  padding: var(--space-4);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.close {
  border: 1px solid var(--border);
  width: 30px;
  height: 30px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  cursor: pointer;
  color: var(--text-muted);
  transition: all 140ms ease;
}

.close svg {
  width: 14px;
  height: 14px;
  stroke: currentColor;
  stroke-width: 2.4;
  stroke-linecap: round;
}

.close:hover {
  color: var(--text);
  border-color: var(--text-muted);
  background: var(--surface-muted);
}
</style>


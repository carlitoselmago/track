<template>
  <teleport to="body">
    <div v-if="modelValue" class="overlay" @click.self="$emit('update:modelValue', false)">
      <section class="modal">
        <header class="modal-header">
          <h3>{{ title }}</h3>
          <button type="button" class="close" @click="$emit('update:modelValue', false)">
            x
          </button>
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

<style scoped>
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
  padding: var(--space-4);
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  margin: 0;
}

.modal-body {
  padding: var(--space-4);
}

.close {
  border: 0;
  background: transparent;
  cursor: pointer;
  font-size: 18px;
}
</style>

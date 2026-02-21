<template>
  <div ref="root" class="action-menu">
    <button
      type="button"
      class="trigger"
      :aria-expanded="isOpen ? 'true' : 'false'"
      aria-haspopup="menu"
      aria-label="Actions"
      @click="toggle"
    >
      <slot name="icon">
        <svg viewBox="0 0 24 24" aria-hidden="true" class="default-icon">
          <path d="M4 7h16M4 12h16M4 17h16" />
        </svg>
      </slot>
    </button>

    <div v-if="isOpen" class="menu" role="menu">
      <button
        v-for="item in items"
        :key="item.value"
        type="button"
        class="menu-item"
        :class="{ danger: item.variant === 'danger' }"
        role="menuitem"
        @click="select(item.value)"
      >
        {{ item.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";

const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["select"]);

const isOpen = ref(false);
const root = ref(null);

function toggle() {
  isOpen.value = !isOpen.value;
}

function select(value) {
  emit("select", value);
  isOpen.value = false;
}

function onDocumentClick(event) {
  if (!root.value || root.value.contains(event.target)) {
    return;
  }
  isOpen.value = false;
}

onMounted(() => {
  document.addEventListener("click", onDocumentClick);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", onDocumentClick);
});
</script>

<style scoped lang="less">
.action-menu {
  position: relative;
}

.trigger {
  border: 1px solid var(--border);
  width: 30px;
  height: 30px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  color: var(--text);
  cursor: pointer;
  transition: all 140ms ease;
}

.trigger:hover {
  color: var(--text);
  border-color: var(--text-muted);
  background: var(--surface-muted);
}

.default-icon {
  width: 14px;
  height: 14px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2.1;
  stroke-linecap: round;
}

.menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  min-width: 130px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  z-index: 20;
  padding: 6px;
  display: grid;
  gap: 4px;
}

.menu-item {
  border: 0;
  background: transparent;
  color: var(--text);
  text-align: left;
  border-radius: 6px;
  padding: 7px 8px;
  cursor: pointer;
}

.menu-item:hover {
  background: var(--surface-muted);
}

.menu-item.danger {
  color: var(--danger);
}
</style>

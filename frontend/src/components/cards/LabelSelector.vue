<template>
  <section class="panel">
    <header>
      <h4>Labels</h4>
    </header>

    <div class="labels">
      <button
        v-for="label in boardLabels"
        :key="label.id"
        type="button"
        class="label"
        :class="{ active: selectedLabelIds.has(label.id) }"
        :style="{ borderColor: label.color_hex, background: selectedLabelIds.has(label.id) ? label.color_hex : '#fff' }"
        @click="$emit('toggle-label', label)"
      >
        {{ label.name }}
      </button>
    </div>

    <div class="create">
      <input v-model="name" class="input" placeholder="New label name" />
      <label class="color-picker">
        <input v-model="colorHex" type="color" class="color-input" aria-label="Label color" />
        <span class="swatch" :style="{ background: colorHex }" />
        <span class="hex">{{ colorHex.toUpperCase() }}</span>
      </label>
      <button type="button" class="btn" @click="create">Create</button>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from "vue";

const props = defineProps({
  boardLabels: {
    type: Array,
    default: () => [],
  },
  selectedLabels: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["toggle-label", "create-label"]);

const name = ref("");
const colorHex = ref("#16A34A");

const selectedLabelIds = computed(
  () => new Set((props.selectedLabels || []).map((label) => label.id)),
);

function create() {
  if (!name.value.trim()) {
    return;
  }
  emit("create-label", {
    name: name.value.trim(),
    color_hex: colorHex.value,
  });
  name.value = "";
  colorHex.value = "#16A34A";
}
</script>

<style scoped lang="less">
.panel {
  display: grid;
  gap: var(--space-3);
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-3);
}

header h4 {
  margin: 0;
}

.labels {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.label {
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: calc(999px * var(--ui-scale));
  padding: calc(6px * var(--ui-scale)) calc(10px * var(--ui-scale));
  cursor: pointer;
  font-size: calc(12px * var(--ui-scale));
}

.label.active {
  color: #fff;
}

.create {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: var(--space-2);
}

.color-picker {
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: calc(8px * var(--ui-scale));
  background: #fff;
  min-width: calc(132px * var(--ui-scale));
  padding: calc(4px * var(--ui-scale)) calc(8px * var(--ui-scale));
  display: inline-flex;
  align-items: center;
  gap: calc(8px * var(--ui-scale));
  position: relative;
  cursor: pointer;
}

.color-picker:hover {
  background: var(--surface-muted);
}

.color-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.swatch {
  width: calc(18px * var(--ui-scale));
  height: calc(18px * var(--ui-scale));
  border-radius: calc(999px * var(--ui-scale));
  border: calc(1px * var(--ui-scale)) solid rgba(15, 23, 42, 0.2);
  flex-shrink: 0;
}

.hex {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: calc(12px * var(--ui-scale));
  color: var(--text-muted);
}

.input {
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: calc(8px * var(--ui-scale));
  padding: calc(7px * var(--ui-scale)) calc(8px * var(--ui-scale));
}

.btn {
  border: 0;
  border-radius: calc(8px * var(--ui-scale));
  padding: calc(7px * var(--ui-scale)) calc(10px * var(--ui-scale));
  background: var(--surface-muted);
  cursor: pointer;
}
</style>



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
  border: 1px solid var(--border);
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
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 12px;
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
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #fff;
  min-width: 132px;
  padding: 4px 8px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
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
  width: 18px;
  height: 18px;
  border-radius: 999px;
  border: 1px solid rgba(15, 23, 42, 0.2);
  flex-shrink: 0;
}

.hex {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 12px;
  color: var(--text-muted);
}

.input {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 8px;
}

.btn {
  border: 0;
  border-radius: 8px;
  padding: 7px 10px;
  background: var(--surface-muted);
  cursor: pointer;
}
</style>


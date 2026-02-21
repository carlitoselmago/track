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
  gap: @space-3;
  border: calc(1px * @ui-scale) solid @border;
  border-radius: @radius;
  padding: @space-3;
}

header h4 {
  margin: 0;
}

.labels {
  display: flex;
  flex-wrap: wrap;
  gap: @space-2;
}

.label {
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(999px * @ui-scale);
  padding: calc(6px * @ui-scale) calc(10px * @ui-scale);
  cursor: pointer;
  font-size: calc(12px * @ui-scale);
}

.label.active {
  color: #fff;
}

.create {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: @space-2;
}

.color-picker {
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(8px * @ui-scale);
  background: #fff;
  min-width: calc(132px * @ui-scale);
  padding: calc(4px * @ui-scale) calc(8px * @ui-scale);
  display: inline-flex;
  align-items: center;
  gap: calc(8px * @ui-scale);
  position: relative;
  cursor: pointer;
}

.color-picker:hover {
  background: @surface-muted;
}

.color-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.swatch {
  width: calc(18px * @ui-scale);
  height: calc(18px * @ui-scale);
  border-radius: calc(999px * @ui-scale);
  border: calc(1px * @ui-scale) solid rgba(15, 23, 42, 0.2);
  flex-shrink: 0;
}

.hex {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: calc(12px * @ui-scale);
  color: @text-muted;
}

.input {
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(8px * @ui-scale);
  padding: calc(7px * @ui-scale) calc(8px * @ui-scale);
}

.btn {
  border: 0;
  border-radius: calc(8px * @ui-scale);
  padding: calc(7px * @ui-scale) calc(10px * @ui-scale);
  background: @surface-muted;
  cursor: pointer;
}
</style>




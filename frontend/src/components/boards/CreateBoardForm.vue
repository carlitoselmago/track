<template>
  <form class="panel" @submit.prevent="submit">
    <BaseInput v-model="name" label="Board name" placeholder="Sprint planning" />
    <BaseInput
      v-model="description"
      label="Description"
      type="textarea"
      placeholder="Optional"
    />
    <div class="row">
      <div class="color">
        <span>Color</span>
        <label class="color-picker">
          <input v-model="colorHex" type="color" class="color-input" aria-label="Board color" />
          <span class="swatch" :style="{ background: colorHex }" />
          <span class="hex">{{ colorHex.toUpperCase() }}</span>
        </label>
      </div>
      <BaseButton type="submit" :loading="submitting">Create board</BaseButton>
    </div>
  </form>
</template>

<script setup>
import { ref } from "vue";
import BaseInput from "@/components/common/BaseInput.vue";
import BaseButton from "@/components/common/BaseButton.vue";

const emit = defineEmits(["create"]);

const name = ref("");
const description = ref("");
const colorHex = ref("#16A34A");
const submitting = ref(false);

async function submit() {
  if (!name.value.trim()) {
    return;
  }
  submitting.value = true;
  try {
    await emit("create", {
      name: name.value.trim(),
      description: description.value.trim(),
      color_hex: colorHex.value,
    });
    name.value = "";
    description.value = "";
    colorHex.value = "#16A34A";
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped lang="less">
.panel {
  display: grid;
  gap: var(--space-3);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-4);
}

.row {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: var(--space-3);
}

.color {
  display: grid;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
}

.color-picker {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #fff;
  min-width: 150px;
  padding: 6px 10px;
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
}
</style>


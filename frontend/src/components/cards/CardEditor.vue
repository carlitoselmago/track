<template>
  <section class="editor">
    <BaseInput
      v-model="draftDescription"
      label="Description"
      type="textarea"
      @update:model-value="onDescriptionChange"
    />
    <p class="hint">Changes are saved automatically.</p>
  </section>
</template>

<script setup>
import { ref, watch } from "vue";
import BaseInput from "@/components/common/BaseInput.vue";

const props = defineProps({
  card: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["save"]);

const draftDescription = ref("");
const lastSyncedDescription = ref("");
const saveTimer = ref(null);

watch(
  () => props.card,
  (card) => {
    draftDescription.value = card?.description || "";
    lastSyncedDescription.value = draftDescription.value;
  },
  { immediate: true, deep: true },
);

function scheduleSave() {
  if (saveTimer.value) {
    clearTimeout(saveTimer.value);
  }
  saveTimer.value = setTimeout(() => {
    const description = draftDescription.value.trim();
    if (description === lastSyncedDescription.value) {
      return;
    }
    emit("save", { description });
    lastSyncedDescription.value = description;
  }, 350);
}

function onDescriptionChange() {
  scheduleSave();
}
</script>

<style scoped lang="less">
.editor {
  display: grid;
  gap: var(--space-3);
}

.hint {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
}
</style>

<template>
  <section class="editor">
    <BaseInput v-model="draftTitle" label="Title" @update:model-value="onTitleChange" />
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

const draftTitle = ref("");
const draftDescription = ref("");
const lastSyncedTitle = ref("");
const lastSyncedDescription = ref("");
const saveTimer = ref(null);

watch(
  () => props.card,
  (card) => {
    draftTitle.value = card?.title || "";
    draftDescription.value = card?.description || "";
    lastSyncedTitle.value = draftTitle.value;
    lastSyncedDescription.value = draftDescription.value;
  },
  { immediate: true, deep: true },
);

function scheduleSave() {
  if (saveTimer.value) {
    clearTimeout(saveTimer.value);
  }
  saveTimer.value = setTimeout(() => {
    const title = draftTitle.value.trim();
    const description = draftDescription.value.trim();
    if (title === lastSyncedTitle.value && description === lastSyncedDescription.value) {
      return;
    }
    emit("save", { title, description });
    lastSyncedTitle.value = title;
    lastSyncedDescription.value = description;
  }, 350);
}

function onTitleChange() {
  scheduleSave();
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


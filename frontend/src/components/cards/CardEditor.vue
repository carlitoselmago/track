<template>
  <section class="editor">
    <header class="editor-head">
      <h4>Description</h4>
    </header>

    <button
      v-if="!isEditing && !draftDescription"
      type="button"
      class="empty-button"
      @click="startEditing"
    >
      Add description
    </button>

    <button
      v-else-if="!isEditing"
      type="button"
      class="preview"
      @click="startEditing"
    >
      {{ draftDescription }}
    </button>

    <textarea
      v-else
      ref="textareaRef"
      v-model="draftDescription"
      class="editor-input"
      rows="4"
      placeholder="Add description"
      @input="onDescriptionChange"
      @blur="finishEditing"
      @keydown.esc.prevent="cancelEditing"
    />
  </section>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from "vue";

const props = defineProps({
  card: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["save"]);

const draftDescription = ref("");
const lastSyncedDescription = ref("");
const isEditing = ref(false);
const textareaRef = ref(null);
let saveTimer = null;

watch(
  () => [props.card?.id, props.card?.description],
  ([, description]) => {
    if (isEditing.value) {
      return;
    }
    draftDescription.value = description || "";
    lastSyncedDescription.value = draftDescription.value;
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  if (saveTimer) {
    clearTimeout(saveTimer);
  }
});

async function startEditing() {
  isEditing.value = true;
  await nextTick();
  textareaRef.value?.focus();
}

function cancelEditing() {
  draftDescription.value = lastSyncedDescription.value;
  isEditing.value = false;
}

function finishEditing() {
  commitNow();
  isEditing.value = false;
}

function scheduleSave() {
  if (saveTimer) {
    clearTimeout(saveTimer);
  }
  saveTimer = setTimeout(() => {
    commitNow();
  }, 320);
}

function commitNow() {
  const value = draftDescription.value.trim() ? draftDescription.value : "";
  if (value === lastSyncedDescription.value) {
    return;
  }
  emit("save", { description: value });
  lastSyncedDescription.value = value;
}

function onDescriptionChange() {
  scheduleSave();
}
</script>

<style scoped lang="less">
.editor {
  display: grid;
  gap: @space-2;
}

.editor-head h4 {
  margin: 0;
  font-size: calc(13px * @ui-scale);
  color: @text-muted;
  font-weight: 600;
  @media (prefers-color-scheme: dark) {
    color: @text-muted-dark;
  }
}

.empty-button,
.preview {
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(10px * @ui-scale);
  background: #fff;
  color: @text;
  text-align: left;
  width: 100%;
  padding: calc(10px * @ui-scale) calc(12px * @ui-scale);
  cursor: text;
}

.empty-button {
  color: @text-muted;
  font-style: italic;
  min-height: calc(44px * @ui-scale);
  @media (prefers-color-scheme: dark) {
    background-color: @surface-muted-dark;
    border-color:@bg-dark;
  }
}

.preview {
  white-space: pre-wrap;
  line-height: 1.45;
  min-height: calc(44px * @ui-scale);
}

.editor-input {
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(10px * @ui-scale);
  background: #fff;
  color: @text;
  width: 100%;
  min-height: calc(108px * @ui-scale);
  resize: vertical;
  padding: calc(10px * @ui-scale) calc(12px * @ui-scale);
  line-height: 1.45;
}

.editor-input:focus {
  outline: calc(2px * @ui-scale) solid color-mix(in srgb, @primary 26%, white);
  border-color: color-mix(in srgb, @primary 50%, @border);
}
</style>



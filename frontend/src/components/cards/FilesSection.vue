<template>
  <section
    class="panel"
    :class="{ 'drag-active': isDragActive && props.showUploadControls }"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
  >
    <header>
      <h4>Files</h4>
      <template v-if="props.showUploadControls">
        <input
          ref="fileInputRef"
          type="file"
          class="native-file-input"
          @change="upload"
          multiple
        />
        <button type="button" class="add-file-btn" @click="openFilePicker">
          Add file
        </button>
      </template>
    </header>
    <p v-if="props.showUploadControls" class="drop-help">Drop files anywhere in this panel or on the card modal.</p>

    <div v-if="!card.images?.length" class="grid">
      <figure class="item placeholder">
        <div class="file-tile">
          <span>FILES</span>
        </div>
        <figcaption>
          <span class="muted">No files yet</span>
        </figcaption>
      </figure>
    </div>

    <div v-else class="grid">
      <figure
        v-for="file in card.images"
        :key="file.id"
        class="item"
        :class="{ cover: card.cover_image_id === file.id }"
      >
        <img v-if="isImage(file)" :src="fileUrl(file.id)" alt="" />
        <div v-else class="file-tile">
          <span>{{ extension(file.original_filename) }}</span>
        </div>
        <figcaption>
          <span v-if="card.cover_image_id === file.id" class="cover-tag">Cover</span>
          <button
            v-if="isImage(file) && card.cover_image_id !== file.id"
            type="button"
            class="link"
            @click="$emit('set-cover', file.id)"
          >
            Set cover
          </button>
          <button type="button" class="link danger" @click="$emit('delete-file', file.id)">
            Delete
          </button>
        </figcaption>
      </figure>
    </div>
  </section>
</template>

<script setup>
import { ref } from "vue";
import { imageService } from "@/services/imageService";

const props = defineProps({
  card: {
    type: Object,
    required: true,
  },
  showUploadControls: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits(["upload-files", "set-cover", "delete-file"]);

const isDragActive = ref(false);
const fileInputRef = ref(null);

function openFilePicker() {
  fileInputRef.value?.click();
}

function upload(event) {
  const files = Array.from(event.target.files || []);
  if (!files.length) {
    return;
  }
  emit("upload-files", files);
  event.target.value = "";
}

function onDragOver(event) {
  if (!props.showUploadControls) {
    return;
  }
  const hasFiles = Array.from(event.dataTransfer?.types || []).includes("Files");
  if (hasFiles) {
    isDragActive.value = true;
  }
}

function onDragLeave() {
  if (!props.showUploadControls) {
    return;
  }
  isDragActive.value = false;
}

function onDrop(event) {
  if (!props.showUploadControls) {
    return;
  }
  isDragActive.value = false;
  const files = Array.from(event.dataTransfer?.files || []);
  if (!files.length) {
    return;
  }
  emit("upload-files", files);
}

function isImage(file) {
  return String(file?.mime_type || "").startsWith("image/");
}

function extension(filename) {
  const value = String(filename || "");
  const lastDot = value.lastIndexOf(".");
  if (lastDot < 0 || lastDot === value.length - 1) {
    return "FILE";
  }
  return value.slice(lastDot + 1).toUpperCase().slice(0, 8);
}

function fileUrl(fileId) {
  return imageService.getImageContentUrl(fileId);
}
</script>

<style scoped lang="less">
.panel {
  display: grid;
  gap: var(--space-3);
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-3);
  transition: border-color 120ms ease, background 120ms ease;
}

.panel.drag-active {
  border-color: var(--primary);
  background: #ecfdf3;
}

header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

header h4 {
  margin: 0;
}

.native-file-input {
  display: none;
}

.add-file-btn {
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: calc(8px * var(--ui-scale));
  background: #fff;
  color: var(--text);
  padding: calc(7px * var(--ui-scale)) calc(12px * var(--ui-scale));
  cursor: pointer;
}

.add-file-btn:hover {
  background: var(--surface-muted);
}

.drop-help {
  margin: 0;
  color: var(--text-muted);
  font-size: calc(12px * var(--ui-scale));
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(calc(120px * var(--ui-scale)), 1fr));
  gap: var(--space-2);
}

.item {
  margin: 0;
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: calc(10px * var(--ui-scale));
  overflow: hidden;
  background: #fff;
}

.item.placeholder {
  border-style: dashed;
}

.item.cover {
  border-color: var(--primary);
}

img,
.file-tile {
  width: 100%;
  aspect-ratio: 4 / 3;
  display: block;
}

img {
  object-fit: cover;
}

.file-tile {
  display: grid;
  place-items: center;
  background: #f1f5f9;
  color: var(--text-muted);
  font-weight: 700;
  letter-spacing: 0.04em;
}

figcaption {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: calc(4px * var(--ui-scale));
  padding: calc(6px * var(--ui-scale));
  flex-wrap: wrap;
}

.link {
  border: 0;
  background: transparent;
  cursor: pointer;
  color: var(--text-muted);
  font-size: calc(11px * var(--ui-scale));
}

.danger {
  color: var(--danger);
}

.cover-tag {
  background: var(--primary);
  color: #fff;
  border-radius: calc(999px * var(--ui-scale));
  padding: calc(2px * var(--ui-scale)) calc(8px * var(--ui-scale));
  font-size: calc(10px * var(--ui-scale));
  font-weight: 700;
  margin-right: auto;
}

.muted {
  color: var(--text-muted);
  font-size: calc(12px * var(--ui-scale));
}
</style>


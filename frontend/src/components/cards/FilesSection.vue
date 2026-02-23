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
        <button
          v-if="isImage(file)"
          type="button"
          class="preview-btn"
          :aria-label="`Open image ${file.original_filename || file.id}`"
          @click="openViewer(file.id)"
        >
          <img :src="fileUrl(file.id)" :alt="file.original_filename || ''" />
        </button>
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

  <teleport to="body">
    <div
      v-if="viewerOpen"
      class="viewer-overlay"
      @click.self="closeViewer"
    >
      <button type="button" class="viewer-close" aria-label="Close image preview" @click="closeViewer">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M6 6l12 12M18 6L6 18" />
        </svg>
      </button>
      <figure v-if="viewerFile" class="viewer-stage" @click.stop>
        <img :src="viewerUrl" :alt="viewerFile.original_filename || 'Image preview'" />
        <figcaption v-if="viewerFile.original_filename">{{ viewerFile.original_filename }}</figcaption>
      </figure>
    </div>
  </teleport>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
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
const viewerImageId = ref(null);
const viewerOpen = computed(() => viewerImageId.value != null);
const viewerFile = computed(() =>
  (props.card?.images || []).find((file) => file.id === viewerImageId.value) || null,
);
const viewerUrl = computed(() => (viewerFile.value ? fileUrl(viewerFile.value.id) : ""));

onMounted(() => {
  window.addEventListener("keydown", onWindowKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", onWindowKeydown);
});

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

function openViewer(fileId) {
  viewerImageId.value = fileId;
}

function closeViewer() {
  viewerImageId.value = null;
}

function onWindowKeydown(event) {
  if (event.key === "Escape" && viewerOpen.value) {
    closeViewer();
  }
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
  gap: @space-3;
  border: calc(1px * @ui-scale) solid @border;
  border-radius: @radius;
  padding: @space-3;
  transition: border-color 120ms ease, background 120ms ease;
  @media (prefers-color-scheme: dark) {
    border-color:@surface-muted-dark;
  }
}

.panel.drag-active {
  border-color: @primary;
  background: #ecfdf3;
}

header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: @space-2;
}

header h4 {
  margin: 0;
}

.native-file-input {
  display: none;
}

.add-file-btn {
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(8px * @ui-scale);
  background: #fff;
  color: @text;
  padding: calc(7px * @ui-scale) calc(12px * @ui-scale);
  cursor: pointer;
}

.add-file-btn:hover {
  background: @surface-muted;
}

.drop-help {
  margin: 0;
  color: @text-muted;
  font-size: calc(12px * @ui-scale);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(calc(120px * @ui-scale), 1fr));
  gap: @space-2;
}

.item {
  margin: 0;
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(10px * @ui-scale);
  overflow: hidden;
  background: #fff;
}

.item.placeholder {
  border-style: dashed;
}

.item.cover {
  border-color: @primary;
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

.preview-btn {
  border: 0;
  padding: 0;
  margin: 0;
  background: transparent;
  display: block;
  width: 100%;
  cursor: zoom-in;
}

.file-tile {
  display: grid;
  place-items: center;
  background: #f1f5f9;
  color: @text-muted;
  font-weight: 700;
  letter-spacing: 0.04em;
}

figcaption {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: calc(4px * @ui-scale);
  padding: calc(6px * @ui-scale);
  flex-wrap: wrap;
}

.link {
  border: 0;
  background: transparent;
  cursor: pointer;
 
  font-size: calc(11px * @ui-scale);
}

.danger {
  color: @danger;
}

.cover-tag {
  background: @primary;
  color: #fff;
  border-radius: calc(999px * @ui-scale);
  padding: calc(2px * @ui-scale) calc(8px * @ui-scale);
  font-size: calc(10px * @ui-scale);
  font-weight: 700;
  margin-right: auto;
}

.muted {
  color: @text-muted;
  font-size: calc(12px * @ui-scale);
}

.viewer-overlay {
  position: fixed;
  inset: 0;
  z-index: 60;
  background: rgba(4, 7, 12, 0.92);
  display: grid;
  place-items: center;
  padding: @space-4;
}

.viewer-stage {
  margin: 0;
  display: grid;
  gap: @space-2;
  justify-items: center;
  max-width: min(95vw, calc(1400px * @ui-scale));
  max-height: calc(100vh - calc(72px * @ui-scale));
}

.viewer-stage img {
  width: auto;
  height: auto;
  max-width: 100%;
  max-height: calc(100vh - calc(130px * @ui-scale));
  object-fit: contain;
  border-radius: calc(10px * @ui-scale);
  box-shadow: 0 calc(20px * @ui-scale) calc(60px * @ui-scale) rgba(0, 0, 0, 0.35);
}

.viewer-stage figcaption {
  color: rgba(255, 255, 255, 0.84);
  font-size: calc(12px * @ui-scale);
  padding: 0;
  justify-content: center;
}

.viewer-close {
  position: absolute;
  top: calc(14px * @ui-scale);
  right: calc(14px * @ui-scale);
  width: calc(38px * @ui-scale);
  height: calc(38px * @ui-scale);
  border-radius: calc(999px * @ui-scale);
  border: calc(1px * @ui-scale) solid rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.viewer-close svg {
  width: calc(14px * @ui-scale);
  height: calc(14px * @ui-scale);
  stroke: currentColor;
  stroke-width: 2.4;
  fill: none;
  stroke-linecap: round;
}
</style>


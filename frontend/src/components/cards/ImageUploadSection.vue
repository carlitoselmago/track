<template>
  <section
    class="panel"
    :class="{ 'drag-active': isDragActive }"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
  >
    <header>
      <h4>Images</h4>
      <input type="file" accept="image/*" @change="upload" />
    </header>
    <p class="drop-help">Drop image files anywhere in this panel to upload.</p>

    <div v-if="!card.images?.length" class="empty">No images uploaded.</div>

    <div v-else class="grid">
      <figure
        v-for="image in card.images"
        :key="image.id"
        class="item"
        :class="{ cover: card.cover_image_id === image.id }"
      >
        <img :src="imageUrl(image.id)" alt="" />
        <figcaption>
          <span v-if="card.cover_image_id === image.id" class="cover-tag">Cover</span>
          <button type="button" class="link" @click="$emit('set-cover', image.id)">
            Set cover
          </button>
          <button type="button" class="link danger" @click="$emit('delete-image', image.id)">
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
});

const emit = defineEmits(["upload-image", "set-cover", "delete-image"]);
const isDragActive = ref(false);

function upload(event) {
  const file = event.target.files?.[0];
  if (!file) {
    return;
  }
  emit("upload-image", file);
  event.target.value = "";
}

function onDragOver(event) {
  const hasFiles = Array.from(event.dataTransfer?.types || []).includes("Files");
  if (hasFiles) {
    isDragActive.value = true;
  }
}

function onDragLeave() {
  isDragActive.value = false;
}

function onDrop(event) {
  isDragActive.value = false;
  const files = Array.from(event.dataTransfer?.files || []);
  const imageFiles = files.filter((file) => file.type.startsWith("image/"));
  if (!imageFiles.length) {
    return;
  }
  imageFiles.forEach((file) => emit("upload-image", file));
}

function imageUrl(imageId) {
  return imageService.getImageContentUrl(imageId);
}
</script>

<style scoped lang="less">
.panel {
  display: grid;
  gap: var(--space-3);
  border: 1px solid var(--border);
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

.drop-help {
  margin: 0;
  color: var(--text-muted);
  font-size: 12px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--space-2);
}

.item {
  margin: 0;
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
}

.item.cover {
  border-color: var(--primary);
}

img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  display: block;
}

figcaption {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 4px;
  padding: 6px;
  flex-wrap: wrap;
}

.link {
  border: 0;
  background: transparent;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 11px;
}

.danger {
  color: var(--danger);
}

.empty {
  color: var(--text-muted);
  font-size: 13px;
}

.cover-tag {
  background: var(--primary);
  color: #fff;
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 10px;
  font-weight: 700;
  margin-right: auto;
}
</style>


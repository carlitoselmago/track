<template>
  <section class="panel">
    <header>
      <h4>Images</h4>
      <input type="file" accept="image/*" @change="upload" />
    </header>

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
import { imageService } from "@/services/imageService";

const props = defineProps({
  card: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["upload-image", "set-cover", "delete-image"]);

function upload(event) {
  const file = event.target.files?.[0];
  if (!file) {
    return;
  }
  emit("upload-image", file);
  event.target.value = "";
}

function imageUrl(imageId) {
  return imageService.getImageContentUrl(imageId);
}
</script>

<style scoped>
.panel {
  display: grid;
  gap: var(--space-3);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-3);
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
  justify-content: space-between;
  align-items: center;
  gap: 4px;
  padding: 6px;
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
</style>

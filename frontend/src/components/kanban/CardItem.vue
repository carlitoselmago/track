<template>
  <article class="card" @click="$emit('open', card.id)">
    <img
      v-if="coverImageId"
      class="cover-image"
      :src="imageUrl(coverImageId)"
      alt=""
    />
    <h4>{{ card.title }}</h4>
    <div v-if="card.labels?.length" class="labels">
      <span
        v-for="label in card.labels"
        :key="label.id"
        class="label"
        :style="{ background: label.color_hex }"
      />
    </div>
    <div class="meta">
      <span v-if="checklistTotal">{{ checklistDone }}/{{ checklistTotal }} checklist</span>
      <span v-if="imageCount">{{ imageCount }} image</span>
      <span v-if="isActiveTimer" class="running">timer running</span>
    </div>
  </article>
</template>

<script setup>
import { computed } from "vue";
import { imageService } from "@/services/imageService";

const props = defineProps({
  card: {
    type: Object,
    required: true,
  },
  isActiveTimer: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["open"]);

const imageCount = computed(() => props.card.images?.length || 0);
const coverImageId = computed(() => props.card.cover_image_id ?? null);

const checklistStats = computed(() => {
  const allChecklists = props.card.checklists || [];
  let total = 0;
  let done = 0;
  allChecklists.forEach((checklist) => {
    (checklist.items || []).forEach((item) => {
      total += 1;
      if (item.is_done) {
        done += 1;
      }
    });
  });
  return { total, done };
});

const checklistTotal = computed(() => checklistStats.value.total);
const checklistDone = computed(() => checklistStats.value.done);

function imageUrl(imageId) {
  return imageService.getImageContentUrl(imageId);
}
</script>

<style scoped lang="less">
.card {
  display: grid;
  gap: var(--space-2);
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface);
  padding: var(--space-3);
  cursor: pointer;
}

.cover-image {
  width: 100%;
  aspect-ratio: 16 / 7;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid var(--border);
}

h4 {
  margin: 0;
  font-size: 14px;
}

.labels {
  display: flex;
  gap: 6px;
}

.label {
  width: 18px;
  height: 6px;
  border-radius: 999px;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 11px;
  color: var(--text-muted);
}

.running {
  color: var(--primary);
  font-weight: 700;
}
</style>


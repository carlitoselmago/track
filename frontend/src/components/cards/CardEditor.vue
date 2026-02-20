<template>
  <section class="editor">
    <BaseInput v-model="draftTitle" label="Title" />
    <BaseInput v-model="draftDescription" label="Description" type="textarea" />
    <BaseButton @click="save">Save card</BaseButton>
  </section>
</template>

<script setup>
import { ref, watch } from "vue";
import BaseInput from "@/components/common/BaseInput.vue";
import BaseButton from "@/components/common/BaseButton.vue";

const props = defineProps({
  card: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["save"]);

const draftTitle = ref("");
const draftDescription = ref("");

watch(
  () => props.card,
  (card) => {
    draftTitle.value = card?.title || "";
    draftDescription.value = card?.description || "";
  },
  { immediate: true, deep: true },
);

function save() {
  emit("save", {
    title: draftTitle.value.trim(),
    description: draftDescription.value.trim(),
  });
}
</script>

<style scoped>
.editor {
  display: grid;
  gap: var(--space-3);
}
</style>

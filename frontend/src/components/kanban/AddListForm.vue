<template>
  <form class="panel" @submit.prevent="submit">
    <BaseInput v-model="title" placeholder="Add another list" />
    <BaseButton type="submit" :disabled="!title.trim()">Add list</BaseButton>
  </form>
</template>

<script setup>
import { ref } from "vue";
import BaseInput from "@/components/common/BaseInput.vue";
import BaseButton from "@/components/common/BaseButton.vue";

const emit = defineEmits(["create"]);

const title = ref("");

async function submit() {
  if (!title.value.trim()) {
    return;
  }
  await emit("create", title.value.trim());
  title.value = "";
}
</script>

<style scoped>
.panel {
  width: 300px;
  min-width: 300px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
}
</style>

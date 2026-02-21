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

<style scoped lang="less">
.panel {
  width: calc(300px * var(--ui-scale));
  min-width: calc(300px * var(--ui-scale));
  background: var(--surface);
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
}
</style>



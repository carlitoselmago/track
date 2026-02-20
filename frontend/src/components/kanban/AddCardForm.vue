<template>
  <form class="add-card" @submit.prevent="submit">
    <input v-model="title" class="input" placeholder="Add a card" />
    <button type="submit" class="btn" :disabled="!title.trim()">Add</button>
  </form>
</template>

<script setup>
import { ref } from "vue";

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
.add-card {
  display: flex;
  gap: var(--space-2);
}

.input {
  flex: 1;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 10px;
}

.btn {
  border: 0;
  border-radius: 8px;
  padding: 8px 10px;
  background: var(--surface-muted);
  cursor: pointer;
}
</style>


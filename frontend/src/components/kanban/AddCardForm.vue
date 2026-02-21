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
  gap: @space-2;
}

.input {
  flex: 1;
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(8px * @ui-scale);
  padding: calc(8px * @ui-scale) calc(10px * @ui-scale);
  background-color: black;
  border:none;
}

.btn {
  border: 0;
  border-radius: calc(8px * @ui-scale);
  padding: calc(8px * @ui-scale) calc(10px * @ui-scale);
  background: @surface-muted;
  cursor: pointer;
  border-color: black !important;
  @media (prefers-color-scheme: dark) {
    background-color: @surface-dark;
  }
}
</style>




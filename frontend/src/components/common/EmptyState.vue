<template>
  <div class="empty-state">
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: "Nothing here yet",
  },
  description: {
    type: String,
    default: "",
  },
});
</script>

<style scoped>
.empty-state {
  background: var(--surface);
  border: 1px dashed var(--border);
  border-radius: var(--radius);
  padding: var(--space-5);
  text-align: center;
}

.empty-state h3 {
  margin: 0 0 var(--space-2);
}

.empty-state p {
  margin: 0;
  color: var(--text-muted);
}
</style>

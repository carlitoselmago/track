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

<style scoped lang="less">
.empty-state {
  background: @surface;
  border: calc(1px * @ui-scale) dashed @border;
  border-radius: @radius;
  padding: @space-5;
  text-align: center;
}

.empty-state h3 {
  margin: 0 0 @space-2;
}

.empty-state p {
  margin: 0;
  color: @text-muted;
}
</style>




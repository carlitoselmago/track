<template>
  <BaseModal :model-value="modelValue" title="Delete card?" @update:model-value="$emit('update:modelValue', $event)">
    <p>This action cannot be undone.</p>
    <div class="actions">
      <BaseButton variant="subtle" @click="$emit('update:modelValue', false)">Cancel</BaseButton>
      <BaseButton variant="danger" @click="$emit('confirm')">Delete</BaseButton>
    </div>
  </BaseModal>
</template>

<script setup>
import BaseModal from "@/components/common/BaseModal.vue";
import BaseButton from "@/components/common/BaseButton.vue";

defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["update:modelValue", "confirm"]);
</script>

<style scoped lang="less">
p {
  margin-top: 0;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: @space-2;
}
</style>



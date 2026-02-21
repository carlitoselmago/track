<template>
  <label class="field">
    <span v-if="label" class="label">{{ label }}</span>
    <input
      v-if="type !== 'textarea'"
      class="control ui-control"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <textarea
      v-else
      class="control textarea ui-control"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      rows="4"
      @input="$emit('update:modelValue', $event.target.value)"
    />
  </label>
</template>

<script setup>
defineProps({
  modelValue: {
    type: [String, Number],
    default: "",
  },
  label: {
    type: String,
    default: "",
  },
  placeholder: {
    type: String,
    default: "",
  },
  type: {
    type: String,
    default: "text",
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["update:modelValue"]);
</script>

<style scoped lang="less">
.field {
  display: grid;
  gap: calc(6px * @ui-scale);
}

.label {
  font-size: calc(12px * @ui-scale);
  color: @text-muted;
}

.control {
  width: 100%;
  padding: calc(10px * @ui-scale) calc(12px * @ui-scale);
}

.textarea {
  resize: vertical;
}
</style>




<template>
  <label class="field">
    <span v-if="label" class="label">{{ label }}</span>
    <input
      v-if="type !== 'textarea'"
      class="control"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <textarea
      v-else
      class="control textarea"
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
  gap: calc(6px * var(--ui-scale));
}

.label {
  font-size: calc(12px * var(--ui-scale));
  color: var(--text-muted);
}

.control {
  width: 100%;
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: calc(8px * var(--ui-scale));
  background: #fff;
  padding: calc(10px * var(--ui-scale)) calc(12px * var(--ui-scale));
}

.control:focus {
  outline: calc(2px * var(--ui-scale)) solid color-mix(in srgb, var(--primary) 35%, white);
  border-color: color-mix(in srgb, var(--primary) 65%, var(--border));
}

.textarea {
  resize: vertical;
}
</style>



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

<style scoped>
.field {
  display: grid;
  gap: 6px;
}

.label {
  font-size: 12px;
  color: var(--text-muted);
}

.control {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #fff;
  padding: 10px 12px;
}

.control:focus {
  outline: 2px solid color-mix(in srgb, var(--primary) 35%, white);
  border-color: color-mix(in srgb, var(--primary) 65%, var(--border));
}

.textarea {
  resize: vertical;
}
</style>

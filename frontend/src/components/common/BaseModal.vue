<template>
  <teleport to="body">
    <div
      v-if="modelValue"
      class="overlay"
      :class="{ 'mobile-fullscreen-overlay': mobileFullscreen }"
      @click.self="$emit('update:modelValue', false)"
    >
      <section
        class="modal"
        :class="[sizeClass, { 'drop-active': allowFileDrop && isDragActive, 'mobile-fullscreen-modal': mobileFullscreen }]"
        @dragenter.prevent="onDragEnter"
        @dragover.prevent="onDragOver"
        @dragleave.prevent="onDragLeave"
        @drop.prevent="onDrop"
      >
        <header class="modal-header">
          <slot name="title">
            <h3 class="modal-title">{{ title }}</h3>
          </slot>
          <div class="header-actions">
            <slot name="header-actions"></slot>
            <button
              type="button"
              class="close"
              aria-label="Close"
              @click="$emit('update:modelValue', false)"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M6 6l12 12M18 6L6 18" />
              </svg>
            </button>
          </div>
        </header>
        <div class="modal-body">
          <slot />
        </div>
        <div v-if="allowFileDrop && isDragActive" class="drop-overlay">
          <p>{{ dropHint }}</p>
        </div>
      </section>
    </div>
  </teleport>
</template>

<script setup>
import { computed, ref, watch } from "vue";

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: "",
  },
  allowFileDrop: {
    type: Boolean,
    default: false,
  },
  dropHint: {
    type: String,
    default: "Drop files to upload",
  },
  size: {
    type: String,
    default: "md",
  },
  mobileFullscreen: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:modelValue", "file-drop"]);

const dragDepth = ref(0);
const isDragActive = ref(false);
const sizeClass = computed(() => (props.size === "sm" ? "modal-sm" : ""));

watch(
  () => props.modelValue,
  (isOpen) => {
    if (!isOpen) {
      dragDepth.value = 0;
      isDragActive.value = false;
    }
  },
);

function hasFiles(event) {
  return Array.from(event.dataTransfer?.types || []).includes("Files");
}

function onDragEnter(event) {
  if (!props.allowFileDrop || !hasFiles(event)) {
    return;
  }
  dragDepth.value += 1;
  isDragActive.value = true;
}

function onDragOver(event) {
  if (!props.allowFileDrop || !hasFiles(event)) {
    return;
  }
  event.dataTransfer.dropEffect = "copy";
  isDragActive.value = true;
}

function onDragLeave(event) {
  if (!props.allowFileDrop || !hasFiles(event)) {
    return;
  }
  dragDepth.value = Math.max(0, dragDepth.value - 1);
  if (dragDepth.value === 0) {
    isDragActive.value = false;
  }
}

function onDrop(event) {
  if (!props.allowFileDrop) {
    return;
  }
  dragDepth.value = 0;
  isDragActive.value = false;
  const files = Array.from(event.dataTransfer?.files || []);
  if (!files.length) {
    return;
  }
  emit("file-drop", files);
}
</script>

<style scoped lang="less">
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.25);
  display: block;
  padding: @space-4;
  z-index: 30;
  backdrop-filter: blur(20px);
  overflow-y: auto;
  overflow-x: hidden;
  overscroll-behavior: contain;
}

.modal {
  width: min(calc(760px * @ui-scale), 100%);
  margin: 0 auto @space-4;
  border-radius: calc(14px * @ui-scale);
  background: #ebebeb;
  box-shadow: @shadow;
  position: relative;
  @media (prefers-color-scheme: dark) {
    background-color: @bg-dark;
  }
}

.modal.modal-sm {
  width: min(calc(520px * @ui-scale), 100%);
}

.modal.drop-active {
  outline: calc(2px * @ui-scale) dashed color-mix(in srgb, @primary 45%, #ffffff);
  outline-offset: calc(-10px * @ui-scale);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: @space-2;
  padding: @space-3 @space-4;
  border-bottom: calc(1px * @ui-scale) solid @border;
  @media (prefers-color-scheme: dark) {
    border-color:@surface-muted-dark;
  }
}

.modal-title {
  margin: 0;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal-body {
  padding: @space-4;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: calc(6px * @ui-scale);
  flex-shrink: 0;
}

.close {
  border: calc(1px * @ui-scale) solid @border;
  width: calc(30px * @ui-scale);
  height: calc(30px * @ui-scale);
  border-radius: calc(999px * @ui-scale);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  cursor: pointer;
  color: @text-muted;
  transition: all 140ms ease;
}

.close svg {
  width: calc(14px * @ui-scale);
  height: calc(14px * @ui-scale);
  stroke: currentColor;
  stroke-width: 2.4;
  stroke-linecap: round;
}

.close:hover {
  color: @text;
  border-color: @text-muted;
  background: @surface-muted;
}

.drop-overlay {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba(15, 23, 42, 0.36);
  color: #fff;
  border-radius: calc(14px * @ui-scale);
  pointer-events: none;
}

.drop-overlay p {
  margin: 0;
  padding: calc(10px * @ui-scale) calc(14px * @ui-scale);
  border-radius: calc(999px * @ui-scale);
  background: rgba(15, 23, 42, 0.62);
  font-weight: 600;
  font-size: calc(13px * @ui-scale);
}

@media (max-width: 615px) {
  .overlay.mobile-fullscreen-overlay {
    padding: 0;
    margin-top: calc(62px * @ui-scale);
  }

  .modal.mobile-fullscreen-modal {
    width: 100%;
    min-height: calc(100vh - calc(62px * @ui-scale));
    border-radius: 0;
    box-shadow: none;
    margin: 0;
  }
}
</style>


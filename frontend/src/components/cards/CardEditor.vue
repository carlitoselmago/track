<template>
  <section class="editor">
    <header class="editor-head">
      <h4>Description</h4>
    </header>

    <button
      v-if="!isEditing && !hasContent"
      type="button"
      class="empty-button ui-control"
      @click="startEditing"
    >
      Add description
    </button>

    <div
      v-else-if="!isEditing"
      ref="previewRef"
      class="preview ui-control rich-content"
      :style="previewStyle"
      v-html="renderedDescription"
      @click="startEditing"
    />

    <div v-else class="editor-shell">
      <div class="toolbar">
        <button type="button" class="tool-btn ui-btn" :class="{ active: isActive('bold') }" @click="toggleBold">
          B
        </button>
        <button type="button" class="tool-btn ui-btn" :class="{ active: isActive('italic') }" @click="toggleItalic">
          I
        </button>
        <button type="button" class="tool-btn ui-btn" :class="{ active: isActive('underline') }" @click="toggleUnderline">
          U
        </button>
        <button
          type="button"
          class="tool-btn ui-btn"
          :class="{ active: isActive('heading', { level: 2 }) }"
          @click="toggleHeading(2)"
        >
          H2
        </button>
        <button type="button" class="tool-btn ui-btn" :class="{ active: isActive('paragraph') }" @click="setParagraph">
          P
        </button>
        <button
          type="button"
          class="tool-btn ui-btn"
          :class="{ active: isActive('bulletList') }"
          @click="toggleBulletList"
        >
          List
        </button>
        <button
          type="button"
          class="tool-btn ui-btn"
          :class="{ active: isActive('orderedList') }"
          @click="toggleOrderedList"
        >
          1.
        </button>
        <button type="button" class="tool-btn ui-btn" :class="{ active: isActive('link') }" @click="setLink">
          Link
        </button>
        <button type="button" class="tool-btn ui-btn" :disabled="!isActive('link')" @click="unsetLink">
          Unlink
        </button>

        <span class="toolbar-spacer" />
        <button type="button" class="action-btn ui-btn subtle" @click="cancelEditing">Cancel</button>
        <button type="button" class="action-btn ui-btn primary" :disabled="isSaving || !isDirty" @click="saveEditing">
          Save
        </button>
      </div>

      <EditorContent
        v-if="editor"
        :editor="editor"
        class="editor-input rich-content"
        @keydown.esc.prevent="cancelEditing"
      />
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { EditorContent, useEditor } from "@tiptap/vue-3";
import StarterKit from "@tiptap/starter-kit";
import Link from "@tiptap/extension-link";
import Underline from "@tiptap/extension-underline";

const props = defineProps({
  card: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["save"]);

const isEditing = ref(false);
const isSaving = ref(false);
const previewRef = ref(null);
const draftDescription = ref("");
const lastSyncedDescription = ref("");
const previewHeight = ref(null);

const renderedDescription = computed(() => lastSyncedDescription.value || "");
const hasContent = computed(() => hasMeaningfulContent(lastSyncedDescription.value));
const isDirty = computed(() => normalizeStoredHtml(draftDescription.value) !== lastSyncedDescription.value);
const previewStyle = computed(() =>
  previewHeight.value ? { height: `${previewHeight.value}px` } : {},
);

const editor = useEditor({
  content: "<p></p>",
  extensions: [
    StarterKit.configure({
      heading: {
        levels: [1, 2, 3],
      },
    }),
    Underline,
    Link.configure({
      autolink: true,
      linkOnPaste: true,
      openOnClick: true,
      HTMLAttributes: {
        target: "_blank",
        rel: "noopener noreferrer",
      },
    }),
  ],
  onUpdate: ({ editor: tiptapEditor }) => {
    draftDescription.value = normalizeStoredHtml(tiptapEditor.getHTML());
  },
});

watch(
  () => [props.card?.id, props.card?.description],
  async ([, description]) => {
    if (isEditing.value) {
      return;
    }
    const sanitized = normalizeStoredHtml(description || "");
    draftDescription.value = sanitized;
    lastSyncedDescription.value = sanitized;
    if (editor.value) {
      editor.value.commands.setContent(sanitized || "<p></p>", false);
    }
    await nextTick();
    updatePreviewHeight();
  },
  { immediate: true },
);

watch(
  () => editor.value,
  (instance) => {
    if (!instance) {
      return;
    }
    instance.commands.setContent(lastSyncedDescription.value || "<p></p>", false);
  },
  { immediate: true },
);

onMounted(() => {
  window.addEventListener("resize", updatePreviewHeight);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", updatePreviewHeight);
  editor.value?.destroy();
});

async function startEditing() {
  isEditing.value = true;
  await nextTick();
  if (!editor.value) {
    return;
  }
  editor.value.commands.setContent(draftDescription.value || "<p></p>", false);
  editor.value.commands.focus("end");
}

async function saveEditing() {
  if (!isEditing.value || isSaving.value || !editor.value) {
    return;
  }

  const sanitized = normalizeStoredHtml(editor.value.getHTML());
  draftDescription.value = sanitized;

  isSaving.value = true;
  try {
    if (sanitized !== lastSyncedDescription.value) {
      emit("save", { description: sanitized });
      lastSyncedDescription.value = sanitized;
    }
    editor.value.commands.setContent(sanitized || "<p></p>", false);
    isEditing.value = false;
    await nextTick();
    updatePreviewHeight();
  } finally {
    isSaving.value = false;
  }
}

async function cancelEditing() {
  draftDescription.value = lastSyncedDescription.value;
  if (editor.value) {
    editor.value.commands.setContent(lastSyncedDescription.value || "<p></p>", false);
  }
  isEditing.value = false;
  await nextTick();
  updatePreviewHeight();
}

function isActive(name, attrs) {
  return Boolean(editor.value?.isActive(name, attrs));
}

function toggleBold() {
  editor.value?.chain().focus().toggleBold().run();
}

function toggleItalic() {
  editor.value?.chain().focus().toggleItalic().run();
}

function toggleUnderline() {
  editor.value?.chain().focus().toggleUnderline().run();
}

function toggleHeading(level) {
  editor.value?.chain().focus().toggleHeading({ level }).run();
}

function setParagraph() {
  editor.value?.chain().focus().setParagraph().run();
}

function toggleBulletList() {
  editor.value?.chain().focus().toggleBulletList().run();
}

function toggleOrderedList() {
  editor.value?.chain().focus().toggleOrderedList().run();
}

function setLink() {
  if (!editor.value) {
    return;
  }
  const currentHref = editor.value.getAttributes("link").href || "";
  const rawUrl = window.prompt("Enter link URL", currentHref);
  if (rawUrl === null) {
    return;
  }
  const trimmed = rawUrl.trim();
  if (!trimmed) {
    editor.value.chain().focus().unsetLink().run();
    return;
  }
  const href = sanitizeHref(trimmed);
  if (!href) {
    return;
  }
  editor.value
    .chain()
    .focus()
    .extendMarkRange("link")
    .setLink({
      href,
      target: "_blank",
      rel: "noopener noreferrer",
    })
    .run();
}

function unsetLink() {
  editor.value?.chain().focus().unsetLink().run();
}

function updatePreviewHeight() {
  if (isEditing.value || !previewRef.value) {
    previewHeight.value = null;
    return;
  }
  previewHeight.value = previewRef.value.scrollHeight;
}

function hasMeaningfulContent(html) {
  if (!html) {
    return false;
  }
  const doc = new DOMParser().parseFromString(`<div>${html}</div>`, "text/html");
  const root = doc.body.firstElementChild;
  const text = (root?.textContent || "").replace(/\u00a0/g, " ").trim();
  return Boolean(text);
}

function normalizeStoredHtml(input) {
  const sanitized = sanitizeHtml(input);
  if (!hasMeaningfulContent(sanitized)) {
    return "";
  }
  return sanitized;
}

function sanitizeHtml(input) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(`<div>${input || ""}</div>`, "text/html");
  const wrapper = doc.body.firstElementChild;
  if (!wrapper) {
    return "";
  }

  const allowedTags = new Set([
    "p",
    "br",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "h1",
    "h2",
    "h3",
    "ul",
    "ol",
    "li",
    "blockquote",
    "a",
  ]);

  const walk = (node) => {
    if (!node) {
      return;
    }

    if (node.nodeType === Node.TEXT_NODE) {
      return;
    }

    if (node.nodeType !== Node.ELEMENT_NODE) {
      node.remove();
      return;
    }

    const element = node;
    const tag = element.tagName.toLowerCase();
    if (!allowedTags.has(tag)) {
      const fragment = doc.createDocumentFragment();
      while (element.firstChild) {
        fragment.appendChild(element.firstChild);
      }
      element.replaceWith(fragment);
      return;
    }

    for (const attr of [...element.attributes]) {
      const name = attr.name.toLowerCase();
      if (tag === "a" && name === "href") {
        const safeHref = sanitizeHref(attr.value);
        if (safeHref) {
          element.setAttribute("href", safeHref);
        } else {
          element.removeAttribute("href");
        }
        continue;
      }
      element.removeAttribute(attr.name);
    }

    if (tag === "a" && element.getAttribute("href")) {
      element.setAttribute("target", "_blank");
      element.setAttribute("rel", "noopener noreferrer");
    }

    for (const child of [...element.childNodes]) {
      walk(child);
    }
  };

  for (const child of [...wrapper.childNodes]) {
    walk(child);
  }

  return wrapper.innerHTML.trim();
}

function sanitizeHref(value) {
  const raw = String(value || "").trim();
  if (!raw) {
    return "";
  }
  const normalized = raw.match(/^[a-zA-Z][a-zA-Z\d+\-.]*:/) ? raw : `https://${raw}`;
  try {
    const parsed = new URL(normalized);
    if (parsed.protocol === "http:" || parsed.protocol === "https:" || parsed.protocol === "mailto:") {
      return parsed.toString();
    }
    return "";
  } catch {
    return "";
  }
}
</script>

<style scoped lang="less">
.editor {
  display: grid;
  gap: @space-2;
}

.editor-head h4 {
  margin: 0;
  font-size: calc(13px * @ui-scale);
  color: @text-muted;
  font-weight: 600;
}

.empty-button,
.preview {
  border-radius: calc(10px * @ui-scale);
  text-align: left;
  width: 100%;
  padding: calc(10px * @ui-scale) calc(12px * @ui-scale);
  cursor: text;
}

.empty-button {
  color: @text-muted;
  font-style: italic;
  min-height: calc(44px * @ui-scale);
}

.preview {
  min-height: calc(44px * @ui-scale);
  overflow: hidden;
}

.editor-shell {
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(10px * @ui-scale);
  overflow: hidden;
  background: #fff;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: calc(6px * @ui-scale);
  flex-wrap: wrap;
  border-bottom: calc(1px * @ui-scale) solid @border;
  padding: calc(8px * @ui-scale);
  background: @surface-muted;
}

.toolbar-spacer {
  flex: 1;
}

.tool-btn,
.action-btn {
  min-height: calc(30px * @ui-scale);
  padding: calc(4px * @ui-scale) calc(8px * @ui-scale);
  font-size: calc(12px * @ui-scale);
}

.tool-btn.active {
  border-color: color-mix(in srgb, @primary 60%, @border);
  background: color-mix(in srgb, @primary 14%, #fff);
}

.action-btn.subtle {
  background: @surface-muted;
}

.action-btn.primary {
  background: @primary;
  border-color: @primary;
  color: #fff;
}

.editor-input {
  width: 100%;
}

.editor-input :deep(.tiptap) {
  min-height: calc(200px * @ui-scale);
  max-height: calc(480px * @ui-scale);
  overflow: auto;
  padding: calc(10px * @ui-scale) calc(12px * @ui-scale);
  line-height: 1.45;
  outline: none;
}

.editor-input :deep(.tiptap:focus) {
  box-shadow: inset 0 0 0 calc(2px * @ui-scale) color-mix(in srgb, @primary 24%, #fff);
}

</style>

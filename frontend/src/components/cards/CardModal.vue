<template>
  <BaseModal
    v-model="isOpen"
    :title="cardStore.activeCard?.title || 'Card details'"
    mobile-fullscreen
    :allow-file-drop="Boolean(cardStore.activeCard?.id)"
    drop-hint="Drop files to upload to this card"
    @file-drop="onMainModalFilesDrop"
  >
    <template #title>
      <div class="title-wrap">
        <button
          v-if="!isTitleEditing"
          type="button"
          class="title-button"
          @click="startTitleEdit"
        >
          {{ cardStore.activeCard?.title || "Untitled card" }}
        </button>
        <input
          v-else
          ref="titleInputRef"
          v-model="draftTitle"
          class="title-input"
          @blur="commitTitleEdit"
          @keydown.enter.prevent="commitTitleEdit"
          @keydown.esc.prevent="cancelTitleEdit"
        />
      </div>
    </template>

    <template #header-actions>
      <ActionMenu
        :items="cardActions"
        @select="onActionSelect"
      />
    </template>

    <div v-if="cardStore.isLoading" class="loading">
      <LoadingSpinner />
    </div>

    <template v-else-if="cardStore.activeCard">
      <div class="sections">
        <section v-if="coverImageId" class="cover-preview">
          <img :src="coverImageUrl" alt="" />
          <span>Cover image</span>
        </section>

        <CardEditor :card="cardStore.activeCard" @save="saveCard" />

        <section v-if="showMetaSummary" class="meta-summary">
          <div v-if="hasLabels" class="meta-group">
            <h4>Labels</h4>
            <div class="chips">
              <span
                v-for="label in cardStore.activeCard.labels"
                :key="label.id"
                class="label-chip"
                :style="labelChipStyle(label.color_hex)"
              >
                {{ label.name }}
              </span>
            </div>
          </div>

          <div v-if="hasAssignees" class="meta-group">
            <h4>Assignees</h4>
            <div class="chips">
              <span
                v-for="user in cardStore.activeCard.assignees"
                :key="user.id"
                class="assignee-chip"
              >
                {{ displayUser(user) }}
              </span>
            </div>
          </div>
        </section>

        <TimerSection
          :card="cardStore.activeCard"
          @refresh-summary="cardStore.fetchTimeSummary()"
        />

        <ChecklistSection
          v-if="hasChecklists"
          :card="cardStore.activeCard"
          :show-checklist-create="false"
          @add-checklist="cardStore.addChecklist"
          @update-checklist="({ checklistId, patch }) => cardStore.updateChecklist(checklistId, patch)"
          @delete-checklist="cardStore.deleteChecklist"
          @add-item="({ checklistId, content }) => cardStore.addChecklistItem(checklistId, content)"
          @update-item="({ itemId, patch }) => cardStore.updateChecklistItem(itemId, patch)"
          @delete-item="cardStore.deleteChecklistItem"
        />

        <FilesSection
          v-if="hasFiles"
          :card="cardStore.activeCard"
          :show-upload-controls="false"
          @set-cover="cardStore.setCover"
          @delete-file="cardStore.deleteFile"
          @upload-files="onUploadFiles"
        />

        <section class="add-actions">
          <h4>Add</h4>
          <div class="add-buttons">
            <button type="button" class="add-btn" @click="openAdd('labels')">+ Label</button>
            <button type="button" class="add-btn" @click="openAdd('assignees')">+ Assignee</button>
            <button type="button" class="add-btn" @click="openAdd('checklist')">+ Checklist</button>
            <button type="button" class="add-btn" @click="openAdd('files')">+ File</button>
          </div>
        </section>
      </div>
    </template>
  </BaseModal>

  <BaseModal
    v-model="isAddOpen"
    :title="addTitle"
    size="sm"
    :allow-file-drop="addPanel === 'files' && Boolean(cardStore.activeCard?.id)"
    drop-hint="Drop files to upload"
    @file-drop="onAddModalFilesDrop"
  >
    <template v-if="addPanel === 'labels'">
      <section class="mini-panel">
        <h4>Assign label</h4>
        <div class="chips">
          <button
            v-for="label in (boardStore.currentBoard?.labels || []).filter(Boolean)"
            :key="label.id"
            type="button"
            class="label-chip button-chip"
            :class="{ active: selectedLabelIds.has(label.id) }"
            :style="labelChipStyle(label.color_hex)"
            @click="cardStore.toggleLabel(label)"
          >
            {{ label.name }}
          </button>
        </div>
        <div v-if="(boardStore.currentBoard?.labels || []).length" class="label-manage-list">
          <div
            v-for="label in (boardStore.currentBoard?.labels || []).filter(Boolean)"
            :key="`manage-${label.id}`"
            class="label-edit-row"
          >
            <input
              :value="getLabelEdit(label).name"
              class="text-input"
              :placeholder="label.name"
              @input="setLabelEditName(label, $event.target.value)"
              @keydown.enter.prevent="saveLabelEdit(label)"
            />
            <label class="color-picker small">
              <input
                :value="getLabelEdit(label).color_hex"
                type="color"
                class="color-input"
                :aria-label="`Color for ${label.name}`"
                @input="setLabelEditColor(label, $event.target.value)"
              />
              <span class="swatch" :style="{ background: getLabelEdit(label).color_hex }" />
            </label>
            <button
              type="button"
              class="mini-btn"
              :disabled="!canSaveLabelEdit(label)"
              @click="saveLabelEdit(label)"
            >
              Save
            </button>
            <button type="button" class="mini-btn danger" @click="deleteLabel(label)">Delete</button>
          </div>
        </div>
        <div class="mini-form">
          <input
            v-model="newLabelName"
            class="text-input"
            placeholder="New label name"
            @keydown.enter.prevent="createAndAssignLabel"
          />
          <label class="color-picker">
            <input v-model="newLabelColor" type="color" class="color-input" aria-label="New label color" />
            <span class="swatch" :style="{ background: newLabelColor }" />
          </label>
          <button type="button" class="mini-btn" @click="createAndAssignLabel">Create</button>
        </div>
      </section>
    </template>

    <template v-else-if="addPanel === 'assignees'">
      <section class="mini-panel">
        <h4>Add assignee</h4>
        <div class="mini-form">
          <select v-model="selectedAssigneeId" class="text-input">
            <option value="">Select board user...</option>
            <option
              v-for="user in assignableUsers"
              :key="user.id"
              :value="String(user.id)"
            >
              {{ displayUser(user) }}
            </option>
          </select>
          <button type="button" class="mini-btn" :disabled="!selectedAssigneeId" @click="addAssignee">
            Add
          </button>
        </div>
      </section>
    </template>

    <template v-else-if="addPanel === 'checklist'">
      <section class="mini-panel">
        <h4>New checklist</h4>
        <div class="mini-form">
          <input
            v-model="newChecklistTitle"
            class="text-input"
            placeholder="Checklist title"
            @keydown.enter.prevent="addChecklist"
          />
          <button type="button" class="mini-btn" :disabled="!newChecklistTitle.trim()" @click="addChecklist">
            Add
          </button>
        </div>
      </section>
    </template>

    <template v-else-if="addPanel === 'files'">
      <section class="mini-panel">
        <h4>Upload files</h4>
        <input
          ref="addFileInputRef"
          type="file"
          class="native-file-input"
          multiple
          @change="onAddFilesInput"
        />
        <button type="button" class="mini-btn" @click="openAddFilePicker">Choose files</button>
        <p class="mini-hint">Or drag files into this modal.</p>
      </section>
    </template>
  </BaseModal>

  <ConfirmDeleteDialog
    v-model="confirmOpen"
    @confirm="deleteCard"
  />
</template>

<script setup>
import { computed, nextTick, ref, watch } from "vue";
import BaseModal from "@/components/common/BaseModal.vue";
import ActionMenu from "@/components/common/ActionMenu.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import CardEditor from "./CardEditor.vue";
import ChecklistSection from "./ChecklistSection.vue";
import FilesSection from "./FilesSection.vue";
import TimerSection from "./TimerSection.vue";
import ConfirmDeleteDialog from "./ConfirmDeleteDialog.vue";
import { useCardStore } from "@/stores/cardStore";
import { useBoardStore } from "@/stores/boardStore";
import { imageService } from "@/services/imageService";

const cardStore = useCardStore();
const boardStore = useBoardStore();

const confirmOpen = ref(false);
const cardActions = [{ label: "Delete", value: "delete", variant: "danger" }];
const isTitleEditing = ref(false);
const isTitleSaving = ref(false);
const draftTitle = ref("");
const titleInputRef = ref(null);

const addPanel = ref(null);
const newLabelName = ref("");
const newLabelColor = ref("#16A34A");
const labelEdits = ref({});
const selectedAssigneeId = ref("");
const newChecklistTitle = ref("");
const addFileInputRef = ref(null);

const coverImageId = computed(() => cardStore.activeCard?.cover_image_id ?? null);
const coverImageUrl = computed(() =>
  coverImageId.value ? imageService.getImageContentUrl(coverImageId.value) : "",
);

const hasLabels = computed(() => (cardStore.activeCard?.labels || []).length > 0);
const hasAssignees = computed(() => (cardStore.activeCard?.assignees || []).length > 0);
const hasChecklists = computed(() => (cardStore.activeCard?.checklists || []).length > 0);
const hasFiles = computed(() => (cardStore.activeCard?.images || []).length > 0);
const showMetaSummary = computed(() => hasLabels.value || hasAssignees.value);

const selectedLabelIds = computed(
  () => new Set((cardStore.activeCard?.labels || []).map((label) => label.id)),
);

const boardUsers = computed(() =>
  (boardStore.currentBoard?.members || []).map((entry) => entry.user || entry),
);

const assignableUsers = computed(() => {
  const selectedIds = new Set((cardStore.activeCard?.assignees || []).map((row) => row.id));
  return boardUsers.value.filter((user) => !selectedIds.has(user.id));
});

const isOpen = computed({
  get: () => cardStore.isModalOpen,
  set: (value) => {
    if (!value) {
      addPanel.value = null;
      cardStore.closeModal();
    }
  },
});

const isAddOpen = computed({
  get: () => Boolean(addPanel.value),
  set: (value) => {
    if (!value) {
      addPanel.value = null;
    }
  },
});

const addTitle = computed(() => {
  if (addPanel.value === "labels") {
    return "Add label";
  }
  if (addPanel.value === "assignees") {
    return "Add assignee";
  }
  if (addPanel.value === "checklist") {
    return "Add checklist";
  }
  if (addPanel.value === "files") {
    return "Add files";
  }
  return "Add";
});

watch(
  () => cardStore.activeCard?.id,
  () => {
    draftTitle.value = cardStore.activeCard?.title || "";
    isTitleEditing.value = false;
    resetAddDrafts();
    addPanel.value = null;
  },
);

watch(
  () => boardStore.currentBoard?.labels,
  () => {
    if (addPanel.value === "labels") {
      syncLabelEdits();
    }
  },
  { deep: true },
);

function resetAddDrafts() {
  newLabelName.value = "";
  newLabelColor.value = "#16A34A";
  labelEdits.value = {};
  selectedAssigneeId.value = "";
  newChecklistTitle.value = "";
}

async function saveCard(payload) {
  await cardStore.saveCard(payload);
  await cardStore.fetchTimeSummary();
}

async function deleteCard() {
  await cardStore.deleteCard();
  confirmOpen.value = false;
}

function onActionSelect(action) {
  if (action === "delete") {
    confirmOpen.value = true;
  }
}

function openAdd(panel) {
  addPanel.value = panel;
  if (panel === "labels") {
    syncLabelEdits();
  }
}

async function onUploadFiles(files) {
  await cardStore.uploadFiles(files);
}

async function onMainModalFilesDrop(files) {
  if (!cardStore.activeCard?.id) {
    return;
  }
  addPanel.value = "files";
  await onUploadFiles(files);
}

async function onAddModalFilesDrop(files) {
  if (addPanel.value !== "files") {
    return;
  }
  await onUploadFiles(files);
}

function openAddFilePicker() {
  addFileInputRef.value?.click();
}

async function onAddFilesInput(event) {
  const files = Array.from(event.target.files || []);
  if (!files.length) {
    return;
  }
  await onUploadFiles(files);
  event.target.value = "";
}

async function createAndAssignLabel() {
  const name = newLabelName.value.trim();
  if (!name) {
    return;
  }
  const label = await cardStore.createBoardLabel(name, newLabelColor.value);
  if (label?.id) {
    await cardStore.toggleLabel(label);
  }
  newLabelName.value = "";
  syncLabelEdits();
}

function syncLabelEdits() {
  const next = {};
  for (const label of boardStore.currentBoard?.labels || []) {
    if (!label) {
      continue;
    }
    const existing = labelEdits.value[label.id];
    next[label.id] = {
      name: existing?.name ?? label.name,
      color_hex: existing?.color_hex ?? label.color_hex,
    };
  }
  labelEdits.value = next;
}

function getLabelEdit(label) {
  if (!label?.id) {
    return { name: "", color_hex: "#16A34A" };
  }
  if (!labelEdits.value[label.id]) {
    labelEdits.value[label.id] = {
      name: label.name || "",
      color_hex: label.color_hex || "#16A34A",
    };
  }
  return labelEdits.value[label.id];
}

function setLabelEditName(label, value) {
  const edit = getLabelEdit(label);
  edit.name = String(value || "");
}

function setLabelEditColor(label, value) {
  const edit = getLabelEdit(label);
  edit.color_hex = String(value || "");
}

function normalizedHex(value) {
  const raw = String(value || "").trim();
  return raw ? raw.toUpperCase() : "";
}

function canSaveLabelEdit(label) {
  const edit = labelEdits.value[label.id];
  if (!edit) {
    return false;
  }
  const name = String(edit.name || "").trim();
  if (!name) {
    return false;
  }
  const color = normalizedHex(edit.color_hex);
  return name !== label.name || color !== normalizedHex(label.color_hex);
}

async function saveLabelEdit(label) {
  if (!canSaveLabelEdit(label)) {
    return;
  }
  const edit = labelEdits.value[label.id];
  await cardStore.updateBoardLabel(label.id, {
    name: String(edit.name || "").trim(),
    color_hex: normalizedHex(edit.color_hex) || label.color_hex,
  });
  syncLabelEdits();
}

async function deleteLabel(label) {
  const ok = window.confirm(`Delete label "${label.name}"?`);
  if (!ok) {
    return;
  }
  await cardStore.deleteBoardLabel(label.id);
  syncLabelEdits();
}

async function addAssignee() {
  if (!selectedAssigneeId.value) {
    return;
  }
  await cardStore.assignUser(Number(selectedAssigneeId.value));
  selectedAssigneeId.value = "";
}

async function addChecklist() {
  const title = newChecklistTitle.value.trim();
  if (!title) {
    return;
  }
  await cardStore.addChecklist(title);
  newChecklistTitle.value = "";
  addPanel.value = null;
}

function displayUser(user) {
  return user?.full_name || user?.name || user?.email || "User";
}

function labelChipStyle(colorHex) {
  return {
    borderColor: colorHex,
    backgroundColor: colorHex,
    color: "#fff",
  };
}

async function startTitleEdit() {
  draftTitle.value = cardStore.activeCard?.title || "";
  isTitleEditing.value = true;
  await nextTick();
  titleInputRef.value?.focus();
  titleInputRef.value?.select();
}

function cancelTitleEdit() {
  draftTitle.value = cardStore.activeCard?.title || "";
  isTitleEditing.value = false;
}

async function commitTitleEdit() {
  if (!isTitleEditing.value || isTitleSaving.value) {
    return;
  }
  isTitleSaving.value = true;
  const title = draftTitle.value.trim();
  try {
    if (!title) {
      cancelTitleEdit();
      return;
    }
    if (title !== (cardStore.activeCard?.title || "")) {
      await saveCard({ title });
    }
    isTitleEditing.value = false;
  } finally {
    isTitleSaving.value = false;
  }
}
</script>

<style scoped lang="less">
.loading {
  display: flex;
  justify-content: center;
  padding: var(--space-6);
}

.sections {
  display: grid;
  gap: var(--space-3);
}

.title-wrap {
  flex: 1;
  min-width: 0;
}

.title-button {
  border: 0;
  background: transparent;
  padding: 0;
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
  text-align: left;
  width: 100%;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: text;
}

.title-input {
  width: 100%;
  min-width: 0;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 18px;
  font-weight: 700;
  padding: 6px 8px;
}

.title-input:focus {
  outline: 2px solid color-mix(in srgb, var(--primary) 28%, white);
  border-color: color-mix(in srgb, var(--primary) 55%, var(--border));
}

.cover-preview {
  display: grid;
  gap: 8px;
}

.cover-preview img {
  width: 100%;
  max-height: 220px;
  object-fit: contain;
  border-radius: 10px;
  border: 1px solid var(--border);
  background-color: #2d2d2d;
}

.cover-preview span {
  font-size: 12px;
  color: var(--text-muted);
}

.meta-summary {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: #fff;
  padding: var(--space-3);
  display: grid;
  gap: var(--space-3);
}

.meta-group {
  display: grid;
  gap: 8px;
}

.meta-group h4 {
  margin: 0;
  color: var(--text-muted);
  font-size: 13px;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.label-chip,
.assignee-chip {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
}

.assignee-chip {
  background: #fff;
  color: var(--text);
}

.add-actions {
  border: 1px dashed var(--border);
  border-radius: var(--radius);
  background: #fff;
  padding: var(--space-3);
  display: grid;
  gap: 10px;
}

.add-actions h4 {
  margin: 0;
  color: var(--text-muted);
  font-size: 13px;
}

.add-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.add-btn {
  border: 1px solid var(--border);
  border-radius: 999px;
  background: #fff;
  color: var(--text);
  padding: 7px 12px;
  cursor: pointer;
}

.add-btn:hover {
  background: var(--surface-muted);
}

.mini-panel {
  display: grid;
  gap: var(--space-3);
}

.mini-panel h4 {
  margin: 0;
  color: var(--text-muted);
  font-size: 13px;
}

.mini-form {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 8px;
  align-items: center;
}

.label-manage-list {
  display: grid;
  gap: 8px;
}

.label-edit-row {
  display: grid;
  grid-template-columns: 1fr auto auto auto;
  gap: 8px;
  align-items: center;
}

.text-input {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #fff;
  padding: 8px 10px;
}

.mini-btn {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #fff;
  color: var(--text);
  padding: 8px 10px;
  cursor: pointer;
}

.mini-btn:hover {
  background: var(--surface-muted);
}

.mini-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mini-btn.danger {
  color: var(--danger);
}

.button-chip {
  cursor: pointer;
  opacity: 0.85;
}

.button-chip.active {
  box-shadow: inset 0 0 0 2px rgba(255, 255, 255, 0.85);
  opacity: 1;
}

.color-picker {
  position: relative;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.color-picker.small {
  width: 32px;
  height: 32px;
}

.color-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.swatch {
  position: absolute;
  inset: 0;
}

.native-file-input {
  display: none;
}

.mini-hint {
  margin: 0;
  color: var(--text-muted);
  font-size: 12px;
}
</style>

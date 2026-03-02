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
          class="title-input ui-control"
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
          <button type="button" class="cover-preview-btn" @click="openImageViewer(coverImageId)">
            <img :src="coverImageUrl" alt="" />
          </button>
          <span>Cover image</span>
        </section>

        <CardEditor :card="cardStore.activeCard" @save="saveCard" />

        <section v-if="showMetaSummary" class="meta-summary">
          <div v-if="hasLabels" class="meta-group">
            <h4 class="ui-section-title">Labels</h4>
            <div class="chips">
              <span
                v-for="label in cardStore.activeCard.labels"
                :key="label.id"
                class="label-chip ui-chip"
                :style="labelChipStyle(label.color_hex)"
              >
                {{ label.name }}
              </span>
            </div>
          </div>

          <div v-if="hasAssignees" class="meta-group">
            <h4 class="ui-section-title">Assignees</h4>
            <div class="chips">
              <span
                v-for="user in cardStore.activeCard.assignees"
                :key="user.id"
                class="assignee-chip ui-chip"
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
          @reorder-checklists="(snapshot) => cardStore.reorderChecklists(snapshot)"
          @reorder-items="({ checklistId, snapshot }) => cardStore.reorderChecklistItems(checklistId, snapshot)"
        />

        <FilesSection
          v-if="hasFiles"
          :card="cardStore.activeCard"
          :show-upload-controls="false"
          @set-cover="cardStore.setCover"
          @delete-file="cardStore.deleteFile"
          @upload-files="onUploadFiles"
          @preview-image="openImageViewer"
        />

        <section class="add-actions">
          <h4 class="ui-section-title">Add</h4>
          <div class="add-buttons">
            <button type="button" class="add-btn ui-btn ui-btn-pill" @click="openAdd('labels')">+ Label</button>
            <button type="button" class="add-btn ui-btn ui-btn-pill" @click="openAdd('assignees')">+ Assignee</button>
            <button type="button" class="add-btn ui-btn ui-btn-pill" @click="openAdd('checklist')">+ Checklist</button>
            <button type="button" class="add-btn ui-btn ui-btn-pill" @click="openAdd('files')">+ File</button>
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
        <h4 class="ui-section-title">Assign label</h4>
        <div class="chips">
          <button
            v-for="label in (boardStore.currentBoard?.labels || []).filter(Boolean)"
            :key="label.id"
            type="button"
            class="label-chip ui-chip button-chip"
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
              class="text-input ui-control"
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
              class="mini-btn ui-btn"
              :disabled="!canSaveLabelEdit(label)"
              @click="saveLabelEdit(label)"
            >
              Save
            </button>
            <button type="button" class="mini-btn ui-btn danger" @click="deleteLabel(label)">Delete</button>
          </div>
        </div>
        <div class="mini-form">
          <input
            v-model="newLabelName"
            class="text-input ui-control"
            placeholder="New label name"
            @keydown.enter.prevent="createAndAssignLabel"
          />
          <label class="color-picker">
            <input v-model="newLabelColor" type="color" class="color-input" aria-label="New label color" />
            <span class="swatch" :style="{ background: newLabelColor }" />
          </label>
          <button type="button" class="mini-btn ui-btn" @click="createAndAssignLabel">Create</button>
        </div>
      </section>
    </template>

    <template v-else-if="addPanel === 'assignees'">
      <section class="mini-panel">
        <h4 class="ui-section-title">Add assignee</h4>
        <div class="mini-form">
          <select v-model="selectedAssigneeId" class="text-input ui-control">
            <option value="">Select board user...</option>
            <option
              v-for="user in assignableUsers"
              :key="user.id"
              :value="String(user.id)"
            >
              {{ displayUser(user) }}
            </option>
          </select>
          <button type="button" class="mini-btn ui-btn" :disabled="!selectedAssigneeId" @click="addAssignee">
            Add
          </button>
        </div>
      </section>
    </template>

    <template v-else-if="addPanel === 'checklist'">
      <section class="mini-panel">
        <h4 class="ui-section-title">New checklist</h4>
        <div class="mini-form">
          <input
            v-model="newChecklistTitle"
            class="text-input ui-control"
            placeholder="Checklist title"
            @keydown.enter.prevent="addChecklist"
          />
          <button type="button" class="mini-btn ui-btn" :disabled="!newChecklistTitle.trim()" @click="addChecklist">
            Add
          </button>
        </div>
      </section>
    </template>

    <template v-else-if="addPanel === 'files'">
      <section class="mini-panel">
        <h4 class="ui-section-title">Upload files</h4>
        <input
          ref="addFileInputRef"
          type="file"
          class="native-file-input"
          multiple
          @change="onAddFilesInput"
        />
        <button type="button" class="mini-btn ui-btn" @click="openAddFilePicker">Choose files</button>
        <p class="mini-hint">Or drag files into this modal.</p>
      </section>
    </template>
  </BaseModal>

  <BaseModal
    v-model="isMoveOpen"
    title="Move card"
    size="sm"
  >
    <section class="mini-panel">
      <h4 class="ui-section-title">Choose board and column</h4>
      <p v-if="moveLoadError" class="move-error">{{ moveLoadError }}</p>
      <div class="mini-form single-col">
        <select
          v-model="selectedMoveBoardId"
          class="text-input ui-control"
          :disabled="isMoveLoading"
          @change="onMoveBoardChange"
        >
          <option value="">Select board...</option>
          <option v-for="board in moveBoards" :key="board.id" :value="String(board.id)">
            {{ board.name }}
          </option>
        </select>
        <select
          v-model="selectedMoveListId"
          class="text-input ui-control"
          :disabled="isMoveLoading || !selectedMoveBoardId || !moveLists.length"
        >
          <option value="">Select column...</option>
          <option v-for="list in moveLists" :key="list.id" :value="String(list.id)">
            {{ list.title }}
          </option>
        </select>
      </div>
      <div class="edit-actions">
        <BaseButton variant="subtle" @click="isMoveOpen = false">Cancel</BaseButton>
        <BaseButton :disabled="!selectedMoveListId || isMoveSubmitting" @click="submitMoveCard">
          Move card
        </BaseButton>
      </div>
    </section>
  </BaseModal>

  <teleport to="body">
    <div v-if="isImageViewerOpen" class="viewer-overlay" @click.self="closeImageViewer">
      <button type="button" class="viewer-close" aria-label="Close image preview" @click="closeImageViewer">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M6 6l12 12M18 6L6 18" />
        </svg>
      </button>
      <button
        type="button"
        class="viewer-arrow left"
        aria-label="Previous image"
        :disabled="!canNavigateImages"
        @click.stop="showPreviousImage"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M15 18l-6-6 6-6" />
        </svg>
      </button>
      <figure v-if="viewerImage" class="viewer-stage" @click.stop>
        <img :src="viewerImage.url" :alt="viewerImage.name || 'Image preview'" />
        <figcaption v-if="viewerImage.name">{{ viewerImage.name }}</figcaption>
      </figure>
      <button
        type="button"
        class="viewer-arrow right"
        aria-label="Next image"
        :disabled="!canNavigateImages"
        @click.stop="showNextImage"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M9 6l6 6-6 6" />
        </svg>
      </button>
    </div>
  </teleport>

  <ConfirmDeleteDialog
    v-model="confirmOpen"
    @confirm="deleteCard"
  />
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
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
import { boardService } from "@/services/boardService";

const cardStore = useCardStore();
const boardStore = useBoardStore();

const confirmOpen = ref(false);
const cardActions = [
  { label: "Move", value: "move" },
  { label: "Delete", value: "delete", variant: "danger" },
];
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
const isMoveOpen = ref(false);
const moveBoards = ref([]);
const moveLists = ref([]);
const selectedMoveBoardId = ref("");
const selectedMoveListId = ref("");
const isMoveLoading = ref(false);
const isMoveSubmitting = ref(false);
const moveLoadError = ref("");
const viewerImageId = ref(null);

const coverImageId = computed(() => cardStore.activeCard?.cover_image_id ?? null);
const coverImageUrl = computed(() =>
  coverImageId.value ? imageService.getImageContentUrl(coverImageId.value) : "",
);
const imageFiles = computed(() =>
  (cardStore.activeCard?.images || [])
    .filter((file) => String(file?.mime_type || "").startsWith("image/"))
    .map((file) => ({
      id: file.id,
      name: file.original_filename || "",
      url: imageService.getImageContentUrl(file.id),
    })),
);
const viewerImageIndex = computed(() =>
  imageFiles.value.findIndex((file) => file.id === viewerImageId.value),
);
const viewerImage = computed(() => {
  if (viewerImageIndex.value < 0) {
    return null;
  }
  return imageFiles.value[viewerImageIndex.value] || null;
});
const isImageViewerOpen = computed(() => viewerImage.value != null);
const canNavigateImages = computed(() => imageFiles.value.length > 1);

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
    resetMoveDrafts();
    closeImageViewer();
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

onMounted(() => {
  window.addEventListener("paste", onWindowPaste);
  window.addEventListener("keydown", onWindowKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener("paste", onWindowPaste);
  window.removeEventListener("keydown", onWindowKeydown);
});

function resetAddDrafts() {
  newLabelName.value = "";
  newLabelColor.value = "#16A34A";
  labelEdits.value = {};
  selectedAssigneeId.value = "";
  newChecklistTitle.value = "";
}

function resetMoveDrafts() {
  isMoveOpen.value = false;
  moveBoards.value = [];
  moveLists.value = [];
  selectedMoveBoardId.value = "";
  selectedMoveListId.value = "";
  isMoveLoading.value = false;
  isMoveSubmitting.value = false;
  moveLoadError.value = "";
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
  if (action === "move") {
    openMoveDialog();
    return;
  }
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

async function onWindowPaste(event) {
  if (!cardStore.isModalOpen || !cardStore.activeCard?.id) {
    return;
  }

  const clipboardItems = Array.from(event.clipboardData?.items || []);
  if (!clipboardItems.length) {
    return;
  }

  const imageFiles = clipboardItems
    .filter((item) => item.kind === "file" && String(item.type || "").startsWith("image/"))
    .map((item, index) => {
      const file = item.getAsFile?.();
      if (!file) {
        return null;
      }
      const extension = (file.type || "image/png").split("/")[1] || "png";
      return new File([file], file.name || `clipboard-image-${Date.now()}-${index}.${extension}`, {
        type: file.type || "image/png",
      });
    })
    .filter(Boolean);

  if (!imageFiles.length) {
    return;
  }

  event.preventDefault();
  await onUploadFiles(imageFiles);
}

function onWindowKeydown(event) {
  if (!isImageViewerOpen.value) {
    return;
  }
  if (event.key === "Escape") {
    closeImageViewer();
    return;
  }
  if (event.key === "ArrowLeft") {
    event.preventDefault();
    showPreviousImage();
    return;
  }
  if (event.key === "ArrowRight") {
    event.preventDefault();
    showNextImage();
  }
}

function openImageViewer(imageId) {
  if (!imageId || !imageFiles.value.some((file) => file.id === imageId)) {
    return;
  }
  viewerImageId.value = imageId;
}

function closeImageViewer() {
  viewerImageId.value = null;
}

function showPreviousImage() {
  if (!canNavigateImages.value || viewerImageIndex.value < 0) {
    return;
  }
  const nextIndex = (viewerImageIndex.value - 1 + imageFiles.value.length) % imageFiles.value.length;
  viewerImageId.value = imageFiles.value[nextIndex].id;
}

function showNextImage() {
  if (!canNavigateImages.value || viewerImageIndex.value < 0) {
    return;
  }
  const nextIndex = (viewerImageIndex.value + 1) % imageFiles.value.length;
  viewerImageId.value = imageFiles.value[nextIndex].id;
}

async function openMoveDialog() {
  if (!cardStore.activeCard?.id) {
    return;
  }
  isMoveOpen.value = true;
  await loadMoveBoardsAndLists();
}

async function loadMoveBoardsAndLists() {
  isMoveLoading.value = true;
  moveLoadError.value = "";
  try {
    const boardsPayload = await boardService.getBoards();
    const rows = Array.isArray(boardsPayload)
      ? boardsPayload
      : boardsPayload?.items || [];
    moveBoards.value = rows.map((board) => ({
      id: Number(board.id),
      name: board.name || "Untitled board",
    }));

    const defaultBoardId = Number(cardStore.activeCard?.board_id || moveBoards.value[0]?.id || 0);
    selectedMoveBoardId.value = defaultBoardId ? String(defaultBoardId) : "";
    if (defaultBoardId) {
      await loadListsForMoveBoard(defaultBoardId);
    }
  } catch (error) {
    moveLoadError.value = error?.message || "Could not load boards";
    moveBoards.value = [];
    moveLists.value = [];
  } finally {
    isMoveLoading.value = false;
  }
}

async function onMoveBoardChange() {
  selectedMoveListId.value = "";
  if (!selectedMoveBoardId.value) {
    moveLists.value = [];
    return;
  }
  await loadListsForMoveBoard(Number(selectedMoveBoardId.value));
}

async function loadListsForMoveBoard(boardId) {
  isMoveLoading.value = true;
  moveLoadError.value = "";
  try {
    let lists = [];
    if (boardStore.currentBoard?.id === boardId) {
      lists = boardStore.currentBoard?.lists || [];
    } else {
      const boardPayload = await boardService.getBoard(boardId);
      lists = boardPayload?.lists || boardPayload?.data?.lists || [];
    }

    moveLists.value = [...lists]
      .map((list) => ({
        id: Number(list.id),
        title: list.title || "Untitled column",
        position: Number(list.position ?? 0),
      }))
      .sort((a, b) => a.position - b.position);

    if (moveLists.value.length) {
      selectedMoveListId.value = String(moveLists.value[0].id);
    }
  } catch (error) {
    moveLoadError.value = error?.message || "Could not load columns";
    moveLists.value = [];
  } finally {
    isMoveLoading.value = false;
  }
}

async function submitMoveCard() {
  const listId = Number(selectedMoveListId.value || 0);
  if (!listId || isMoveSubmitting.value) {
    return;
  }
  isMoveSubmitting.value = true;
  try {
    await cardStore.moveCardToList(listId);
    isMoveOpen.value = false;
  } finally {
    isMoveSubmitting.value = false;
  }
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
  padding: @space-6;
}

.sections {
  display: grid;
  gap: @space-3;
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
  font-size: calc(20px * @ui-scale);
  font-weight: 700;
  color: @text;
  text-align: left;
  width: 100%;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: text;
  @media (prefers-color-scheme: dark) {
    color:@text-dark;
  }
}

.title-input {
  width: 100%;
  min-width: 0;
  font-size: calc(18px * @ui-scale);
  font-weight: 700;
  padding: calc(6px * @ui-scale) calc(8px * @ui-scale);
}

.title-input:focus {
  outline: calc(2px * @ui-scale) solid color-mix(in srgb, @primary 28%, white);
  border-color: color-mix(in srgb, @primary 55%, @border);
}

.cover-preview {
  display: grid;
  gap: calc(8px * @ui-scale);
}

.cover-preview-btn {
  border: 0;
  background: transparent;
  padding: 0;
  margin: 0;
  cursor: zoom-in;
}

.cover-preview img {
  width: 100%;
  max-height: calc(220px * @ui-scale);
  object-fit: contain;
  border-radius: calc(10px * @ui-scale);
  border: calc(1px * @ui-scale) solid @border;
  background-color: #2d2d2d;
  @media (prefers-color-scheme: dark) {
    border-color:@bg-dark;
  }
}

.cover-preview span {
  font-size: calc(12px * @ui-scale);
  color: @text-muted;
  @media (prefers-color-scheme: dark) {
    color: @text-muted-dark;
  }
}

.meta-summary {

  border-radius: @radius;
 
  padding: @space-3;
 
  
 
  @media (prefers-color-scheme: dark) {
    border-color:@surface-muted-dark;
    
  }
}

.meta-group {
  display: grid;
  gap: calc(8px * @ui-scale);
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: calc(8px * @ui-scale);
}

.label-chip,
.assignee-chip {
  line-height: 1.1;
}



.add-actions {
  border: calc(1px * @ui-scale) dashed @border;
  border-radius: @radius;
  background: #fff;
  padding: @space-3;
  display: grid;
  gap: calc(10px * @ui-scale);
  @media (prefers-color-scheme: dark) {
    background-color:@bg-dark;
    border-color:@surface-muted-dark;
  }
}

.add-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: calc(8px * @ui-scale);
}

.add-btn {
  padding: calc(7px * @ui-scale) calc(12px * @ui-scale);
}

.mini-panel {
  display: grid;
  gap: @space-3;
}

.mini-form {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: calc(8px * @ui-scale);
  align-items: center;
}

.mini-form.single-col {
  grid-template-columns: 1fr;
}

.label-manage-list {
  display: grid;
  gap: calc(8px * @ui-scale);
}

.label-edit-row {
  display: grid;
  grid-template-columns: 1fr auto auto auto;
  gap: calc(8px * @ui-scale);
  align-items: center;
}

.text-input {
  width: 100%;
  padding: calc(8px * @ui-scale) calc(10px * @ui-scale);
}

.mini-btn {
  padding: calc(8px * @ui-scale) calc(10px * @ui-scale);
}

.mini-btn.danger {
  color: @danger;
}

.button-chip {
  cursor: pointer;
  opacity: 0.85;
}

.button-chip.active {
  box-shadow: inset 0 0 0 calc(2px * @ui-scale) rgba(255, 255, 255, 0.85);
  opacity: 1;
}

.color-picker {
  position: relative;
  width: calc(36px * @ui-scale);
  height: calc(36px * @ui-scale);
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(8px * @ui-scale);
  overflow: hidden;
}

.color-picker.small {
  width: calc(32px * @ui-scale);
  height: calc(32px * @ui-scale);
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
  color: @text-muted;
  font-size: calc(12px * @ui-scale);
}

.move-error {
  margin: 0;
  color: @danger;
  font-size: calc(12px * @ui-scale);
}

.viewer-overlay {
  position: fixed;
  inset: 0;
  z-index: 60;
  background: rgba(4, 7, 12, 0.92);
  display: grid;
  place-items: center;
  padding: @space-4;
}

.viewer-stage {
  margin: 0;
  display: grid;
  gap: @space-2;
  justify-items: center;
  max-width: min(95vw, calc(1400px * @ui-scale));
  max-height: calc(100vh - calc(72px * @ui-scale));
}

.viewer-stage img {
  width: auto;
  height: auto;
  max-width: 100%;
  max-height: calc(100vh - calc(130px * @ui-scale));
  object-fit: contain;
  border-radius: calc(10px * @ui-scale);
  box-shadow: 0 calc(20px * @ui-scale) calc(60px * @ui-scale) rgba(0, 0, 0, 0.35);
}

.viewer-stage figcaption {
  color: rgba(255, 255, 255, 0.84);
  font-size: calc(12px * @ui-scale);
  padding: 0;
  justify-content: center;
}

.viewer-close,
.viewer-arrow {
  position: absolute;
  border-radius: calc(999px * @ui-scale);
  border: calc(1px * @ui-scale) solid rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.viewer-close {
  top: calc(14px * @ui-scale);
  right: calc(14px * @ui-scale);
  width: calc(38px * @ui-scale);
  height: calc(38px * @ui-scale);
}

.viewer-arrow {
  top: 50%;
  transform: translateY(-50%);
  width: calc(42px * @ui-scale);
  height: calc(42px * @ui-scale);
}

.viewer-arrow.left {
  left: calc(16px * @ui-scale);
}

.viewer-arrow.right {
  right: calc(16px * @ui-scale);
}

.viewer-close svg,
.viewer-arrow svg {
  width: calc(16px * @ui-scale);
  height: calc(16px * @ui-scale);
  stroke: currentColor;
  stroke-width: 2.4;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.viewer-arrow:disabled {
  opacity: 0.35;
  cursor: default;
}
</style>

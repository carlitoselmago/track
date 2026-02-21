<template>
  <BaseModal
    v-model="isOpen"
    :title="cardStore.activeCard?.title || 'Card details'"
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

        <TimerSection
          :card="cardStore.activeCard"
          @refresh-summary="cardStore.fetchTimeSummary()"
        />

        <LabelSelector
          :board-labels="boardStore.currentBoard?.labels || []"
          :selected-labels="cardStore.activeCard.labels || []"
          @toggle-label="cardStore.toggleLabel"
          @create-label="createLabel"
        />

        <ChecklistSection
          :card="cardStore.activeCard"
          @add-checklist="cardStore.addChecklist"
          @update-checklist="({ checklistId, patch }) => cardStore.updateChecklist(checklistId, patch)"
          @delete-checklist="cardStore.deleteChecklist"
          @add-item="({ checklistId, content }) => cardStore.addChecklistItem(checklistId, content)"
          @update-item="({ itemId, patch }) => cardStore.updateChecklistItem(itemId, patch)"
          @delete-item="cardStore.deleteChecklistItem"
        />

        <ImageUploadSection
          :card="cardStore.activeCard"
          @upload-image="cardStore.uploadImage"
          @set-cover="cardStore.setCover"
          @delete-image="cardStore.deleteImage"
        />
      </div>
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
import LabelSelector from "./LabelSelector.vue";
import ImageUploadSection from "./ImageUploadSection.vue";
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
const coverImageId = computed(() => cardStore.activeCard?.cover_image_id ?? null);
const coverImageUrl = computed(() =>
  coverImageId.value ? imageService.getImageContentUrl(coverImageId.value) : "",
);

const isOpen = computed({
  get: () => cardStore.isModalOpen,
  set: (value) => {
    if (!value) {
      cardStore.closeModal();
    }
  },
});

watch(
  () => cardStore.activeCard?.id,
  () => {
    draftTitle.value = cardStore.activeCard?.title || "";
    isTitleEditing.value = false;
  },
);

async function saveCard(payload) {
  await cardStore.saveCard(payload);
  await cardStore.fetchTimeSummary();
}

async function createLabel({ name, color_hex }) {
  await cardStore.createBoardLabel(name, color_hex);
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
  background-color: rgb(219, 219, 219);
}

.cover-preview span {
  font-size: 12px;
  color: var(--text-muted);
}
</style>

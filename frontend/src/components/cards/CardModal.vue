<template>
  <BaseModal
    v-model="isOpen"
    :title="cardStore.activeCard?.title || 'Card details'"
  >
    <div v-if="cardStore.isLoading" class="loading">
      <LoadingSpinner />
    </div>

    <template v-else-if="cardStore.activeCard">
      <div class="sections">
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

      <footer class="footer">
        <BaseButton variant="danger" @click="confirmOpen = true">Delete card</BaseButton>
      </footer>
    </template>
  </BaseModal>

  <ConfirmDeleteDialog
    v-model="confirmOpen"
    @confirm="deleteCard"
  />
</template>

<script setup>
import { computed, ref } from "vue";
import BaseModal from "@/components/common/BaseModal.vue";
import BaseButton from "@/components/common/BaseButton.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import CardEditor from "./CardEditor.vue";
import ChecklistSection from "./ChecklistSection.vue";
import LabelSelector from "./LabelSelector.vue";
import ImageUploadSection from "./ImageUploadSection.vue";
import TimerSection from "./TimerSection.vue";
import ConfirmDeleteDialog from "./ConfirmDeleteDialog.vue";
import { useCardStore } from "@/stores/cardStore";
import { useBoardStore } from "@/stores/boardStore";

const cardStore = useCardStore();
const boardStore = useBoardStore();

const confirmOpen = ref(false);

const isOpen = computed({
  get: () => cardStore.isModalOpen,
  set: (value) => {
    if (!value) {
      cardStore.closeModal();
    }
  },
});

async function saveCard(payload) {
  await cardStore.saveCard(payload);
}

async function createLabel({ name, color_hex }) {
  await cardStore.createBoardLabel(name, color_hex);
}

async function deleteCard() {
  await cardStore.deleteCard();
  confirmOpen.value = false;
}
</script>

<style scoped>
.loading {
  display: flex;
  justify-content: center;
  padding: var(--space-6);
}

.sections {
  display: grid;
  gap: var(--space-3);
}

.footer {
  margin-top: var(--space-3);
  display: flex;
  justify-content: flex-end;
}
</style>

<template>
  <section class="panel">
    <header>
      <h4>Checklist</h4>
    </header>

    <div class="progress-wrap">
      <div class="progress-label">
        <span>Progress</span>
        <strong>{{ completionPercent }}%</strong>
      </div>
      <div class="progress-track">
        <div class="progress-bar" :style="{ width: `${completionPercent}%` }" />
      </div>
    </div>

    <div v-if="props.showChecklistCreate" class="add-row">
      <input v-model="newChecklistTitle" class="input" placeholder="New checklist title" />
      <button type="button" class="btn" @click="addChecklist">Add</button>
    </div>

    <div v-for="checklist in card.checklists" :key="checklist.id" class="checklist">
      <div class="checklist-head">
        <input
          class="checklist-title-input"
          :value="checklist.title"
          @change="renameChecklist(checklist.id, checklist.title, $event.target.value)"
        />
        <button type="button" class="link " @click="removeChecklist(checklist.id)">
          Delete
        </button>
      </div>

      <div
        v-for="item in checklist.items || []"
        :key="item.id"
        class="item-row"
      >
        <input
          type="checkbox"
          :checked="item.is_done"
          @change="toggleItem(item.id, $event.target.checked)"
        />
        <input
          class="item-input"
          :value="item.content"
          @change="renameItem(item.id, $event.target.value)"
        />
        <button type="button" class="link" @click="removeItem(item.id)">
          <svg class="closebtn" width="12px" height="12px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M5.29289 5.29289C5.68342 4.90237 6.31658 4.90237 6.70711 5.29289L12 10.5858L17.2929 5.29289C17.6834 4.90237 18.3166 4.90237 18.7071 5.29289C19.0976 5.68342 19.0976 6.31658 18.7071 6.70711L13.4142 12L18.7071 17.2929C19.0976 17.6834 19.0976 18.3166 18.7071 18.7071C18.3166 19.0976 17.6834 19.0976 17.2929 18.7071L12 13.4142L6.70711 18.7071C6.31658 19.0976 5.68342 19.0976 5.29289 18.7071C4.90237 18.3166 4.90237 17.6834 5.29289 17.2929L10.5858 12L5.29289 6.70711C4.90237 6.31658 4.90237 5.68342 5.29289 5.29289Z" fill="#1b1b1b"/>
</svg>
</button>
      </div>

      <div class="add-row small">
        <input
          v-model="newItemByChecklist[checklist.id]"
          class="input"
          placeholder="Add checklist item"
          @keydown.enter.prevent="addItem(checklist.id)"
        />
        <button type="button" class="btn" @click="addItem(checklist.id)">Add</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, reactive, ref } from "vue";

const props = defineProps({
  card: {
    type: Object,
    required: true,
  },
  showChecklistCreate: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits([
  "add-checklist",
  "update-checklist",
  "delete-checklist",
  "add-item",
  "update-item",
  "delete-item",
]);

const newChecklistTitle = ref("");
const newItemByChecklist = reactive({});

const checklistStats = computed(() => {
  let total = 0;
  let done = 0;
  (props.card.checklists || []).forEach((checklist) => {
    (checklist.items || []).forEach((item) => {
      total += 1;
      if (item.is_done) {
        done += 1;
      }
    });
  });
  return { total, done };
});

const completionPercent = computed(() => {
  if (checklistStats.value.total === 0) {
    return 0;
  }
  return Math.round((checklistStats.value.done / checklistStats.value.total) * 100);
});

function addChecklist() {
  const title = newChecklistTitle.value.trim();
  if (!title) {
    return;
  }
  emit("add-checklist", title);
  newChecklistTitle.value = "";
}

function removeChecklist(checklistId) {
  emit("delete-checklist", checklistId);
}

function renameChecklist(checklistId, currentTitle, nextTitle) {
  const title = (nextTitle || "").trim();
  if (!title || title === currentTitle) {
    return;
  }
  emit("update-checklist", { checklistId, patch: { title } });
}

function addItem(checklistId) {
  const content = (newItemByChecklist[checklistId] || "").trim();
  if (!content) {
    return;
  }
  emit("add-item", { checklistId, content });
  newItemByChecklist[checklistId] = "";
}

function toggleItem(itemId, isDone) {
  emit("update-item", { itemId, patch: { is_done: isDone } });
}

function renameItem(itemId, content) {
  emit("update-item", { itemId, patch: { content: content.trim() } });
}

function removeItem(itemId) {
  emit("delete-item", itemId);
}
</script>

<style scoped lang="less">
.panel {
  display: grid;
  gap: @space-1;
  border: calc(1px * @ui-scale) solid @border;
  border-radius: @radius;
  padding: @space-3;
  @media (prefers-color-scheme: dark) {
    border-color: @surface-muted-dark;
  }
}

header h4 {
  margin: 0;
}

.progress-wrap {
  display: grid;
  gap: calc(6px * @ui-scale);
}

.progress-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: calc(12px * @ui-scale);
  color: @text-muted;
}

.progress-track {
  height: calc(8px * @ui-scale);
  border-radius: calc(999px * @ui-scale);
  background: #e5e7eb;
  overflow: hidden;
  margin-bottom: @space-2;
}

.progress-bar {
  height: 100%;
  background: @primary;
  transition: width 160ms ease;
}

.checklist {
  display: grid;
  gap: @space-1;
  background: #f8fafc;
  border-radius: calc(10px * @ui-scale);
  padding: @space-2;
  @media (prefers-color-scheme: dark) {
    background-color: @surface-muted-dark;
    color:@text-dark;
  }
}

.checklist-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: @space-2;
}

.checklist-title-input {
  flex: 1;
  min-width: 0;
  border: 0;
  border-radius: calc(8px * @ui-scale);
  padding: calc(5px * @ui-scale) calc(8px * @ui-scale);
  font-weight: 700;
  background: transparent;
}

.checklist-title-input:focus {
  outline: calc(1px * @ui-scale) solid @border;
  background: #fff;
}

.item-row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: @space-2;
}

.item-input,
.input {
  border: 0;
  border-radius: calc(8px * @ui-scale);
  padding: calc(1px * @ui-scale) calc(8px * @ui-scale);
  background-color: transparent;
}

.add-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: @space-2;
}

.add-row.small {
  margin-top: @space-1;
}

.btn {
  border: 0;
  border-radius: calc(8px * @ui-scale);
  padding: calc(8px * @ui-scale) calc(10px * @ui-scale);

  cursor: pointer;
}

.link {
  border: 0;
  background: transparent;
 
  cursor: pointer;
}

.danger {
  color: @danger;
}
</style>




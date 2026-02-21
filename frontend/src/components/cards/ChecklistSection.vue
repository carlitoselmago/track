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
        <button type="button" class="link danger" @click="removeChecklist(checklist.id)">
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
        <button type="button" class="link danger" @click="removeItem(item.id)">x</button>
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
  gap: var(--space-3);
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-3);
}

header h4 {
  margin: 0;
}

.progress-wrap {
  display: grid;
  gap: calc(6px * var(--ui-scale));
}

.progress-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: calc(12px * var(--ui-scale));
  color: var(--text-muted);
}

.progress-track {
  height: calc(8px * var(--ui-scale));
  border-radius: calc(999px * var(--ui-scale));
  background: #e5e7eb;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--primary);
  transition: width 160ms ease;
}

.checklist {
  display: grid;
  gap: var(--space-2);
  background: #f8fafc;
  border-radius: calc(10px * var(--ui-scale));
  padding: var(--space-2);
}

.checklist-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.checklist-title-input {
  flex: 1;
  min-width: 0;
  border: 0;
  border-radius: calc(8px * var(--ui-scale));
  padding: calc(5px * var(--ui-scale)) calc(8px * var(--ui-scale));
  font-weight: 700;
  background: transparent;
}

.checklist-title-input:focus {
  outline: calc(1px * var(--ui-scale)) solid var(--border);
  background: #fff;
}

.item-row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: var(--space-2);
}

.item-input,
.input {
  border: 0;
  border-radius: calc(8px * var(--ui-scale));
  padding: calc(7px * var(--ui-scale)) calc(8px * var(--ui-scale));
  background-color: transparent;
}

.add-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: var(--space-2);
}

.add-row.small {
  margin-top: var(--space-1);
}

.btn {
  border: 0;
  border-radius: calc(8px * var(--ui-scale));
  padding: calc(8px * var(--ui-scale)) calc(10px * var(--ui-scale));
  background: var(--surface-muted);
  cursor: pointer;
}

.link {
  border: 0;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
}

.danger {
  color: var(--danger);
}
</style>



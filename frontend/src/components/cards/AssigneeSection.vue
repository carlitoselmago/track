<template>
  <section class="panel">
    <header>
      <h4>Assignees</h4>
    </header>

    <div class="assigned">
      <span v-if="!selectedAssignees.length" class="muted">No assignees</span>
      <span
        v-for="user in selectedAssignees"
        :key="user.id"
        class="pill"
      >
        {{ displayName(user) }}
        <button type="button" class="remove" @click="$emit('unassign-user', user.id)">x</button>
      </span>
    </div>

    <div class="assign-row">
      <select v-model="selectedUserId" class="select">
        <option value="">Select board user...</option>
        <option v-for="option in assignableUsers" :key="option.id" :value="String(option.id)">
          {{ displayName(option) }}
        </option>
      </select>
      <button type="button" class="btn" :disabled="!selectedUserId" @click="assign">
        Assign
      </button>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from "vue";

const props = defineProps({
  boardMembers: {
    type: Array,
    default: () => [],
  },
  selectedAssignees: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["assign-user", "unassign-user"]);

const selectedUserId = ref("");

const normalizedBoardUsers = computed(() =>
  (props.boardMembers || []).map((entry) => entry.user || entry),
);

const selectedIds = computed(() => new Set((props.selectedAssignees || []).map((user) => user.id)));

const assignableUsers = computed(() =>
  normalizedBoardUsers.value.filter((user) => !selectedIds.value.has(user.id)),
);

function displayName(user) {
  return user?.full_name || user?.name || user?.email || "User";
}

function assign() {
  if (!selectedUserId.value) {
    return;
  }
  emit("assign-user", Number(selectedUserId.value));
  selectedUserId.value = "";
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

.assigned {
  display: flex;
  flex-wrap: wrap;
  gap: calc(8px * var(--ui-scale));
}

.pill {
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: calc(999px * var(--ui-scale));
  background: #fff;
  padding: calc(4px * var(--ui-scale)) calc(8px * var(--ui-scale));
  display: inline-flex;
  align-items: center;
  gap: calc(6px * var(--ui-scale));
  font-size: calc(12px * var(--ui-scale));
}

.remove {
  border: 0;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
}

.assign-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: var(--space-2);
}

.select {
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: calc(8px * var(--ui-scale));
  padding: calc(7px * var(--ui-scale)) calc(8px * var(--ui-scale));
  background: #fff;
}

.btn {
  border: 0;
  border-radius: calc(8px * var(--ui-scale));
  padding: calc(7px * var(--ui-scale)) calc(10px * var(--ui-scale));
  background: var(--surface-muted);
  cursor: pointer;
}

.muted {
  color: var(--text-muted);
  font-size: calc(12px * var(--ui-scale));
}
</style>


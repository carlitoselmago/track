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
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-3);
}

header h4 {
  margin: 0;
}

.assigned {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pill {
  border: 1px solid var(--border);
  border-radius: 999px;
  background: #fff;
  padding: 4px 8px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
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
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 8px;
  background: #fff;
}

.btn {
  border: 0;
  border-radius: 8px;
  padding: 7px 10px;
  background: var(--surface-muted);
  cursor: pointer;
}

.muted {
  color: var(--text-muted);
  font-size: 12px;
}
</style>

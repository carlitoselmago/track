<template>
  <section class="panel">
    <header>
      <h4>Timer</h4>
      <span class="time">{{ formatDuration(displaySeconds) }}</span>
    </header>

    <div class="controls">
      <BaseButton
        :disabled="timerStore.hasActiveTimer && !isCurrentCardRunning"
        @click="start"
      >
        Start
      </BaseButton>
      <BaseButton
        variant="subtle"
        :disabled="!isCurrentCardRunning"
        @click="stop"
      >
        Stop
      </BaseButton>
    </div>

    <p class="info">
      <template v-if="isCurrentCardRunning">
        Running since {{ activeStartAt }} (UTC)
      </template>
      <template v-else>
        Total tracked {{ formatDuration(totalTrackedSeconds) }}
      </template>
    </p>

    <button type="button" class="chunks-toggle" @click="chunksOpen = !chunksOpen">
      <span>Time chunks</span>
      <span class="toggle-meta">
        {{ sessions.length }}
        <span class="caret" :class="{ open: chunksOpen }">v</span>
      </span>
    </button>

    <div v-if="chunksOpen" class="chunks-panel">
      <p v-if="isLoadingChunks" class="muted">Loading chunks...</p>
      <p v-else-if="sessions.length === 0" class="muted">No chunks yet.</p>

      <ul v-else class="chunks-list">
        <li v-for="row in sessions" :key="row.id" class="chunk-row">
          <div class="chunk-main">
            <div class="duration-wrap">
              <template v-if="editingSessionId === row.id">
                <div class="duration-editor">
                  <label class="time-chip active editable">
                    <input v-model="draftHours" type="number" min="0" step="1" />
                    <span>h</span>
                  </label>

                  <label class="time-chip active editable">
                    <input v-model="draftMinutes" type="number" min="0" step="1" />
                    <span>m</span>
                  </label>

                  <label class="time-chip active editable">
                    <input v-model="draftSeconds" type="number" min="0" step="1" />
                    <span>s</span>
                  </label>

                  <button type="button" class="mini-link save" @click="saveEdit(row)">Save</button>
                  <button type="button" class="mini-link" @click="cancelEdit">Cancel</button>
                </div>
              </template>

              <template v-else>
                <button
                  type="button"
                  class="time-chip"
                  :disabled="!row.ended_at"
                  @click="startEdit(row)"
                >
                  {{ toHms(row.liveDurationSeconds).hours }}h
                </button>
                <button
                  type="button"
                  class="time-chip"
                  :disabled="!row.ended_at"
                  @click="startEdit(row)"
                >
                  {{ toHms(row.liveDurationSeconds).minutes }}m
                </button>
                <button
                  type="button"
                  class="time-chip"
                  :disabled="!row.ended_at"
                  @click="startEdit(row)"
                >
                  {{ toHms(row.liveDurationSeconds).seconds }}s
                </button>
              </template>
            </div>

            <div class="meta">
              <span>{{ formatDateTime(row.started_at) }}</span>
              <span v-if="row.ended_at">to {{ formatDateTime(row.ended_at) }}</span>
              <span v-else class="running-tag">running</span>
            </div>
          </div>

          <div class="chunk-actions">
            <button
              type="button"
              class="mini-link danger"
              :disabled="!row.ended_at"
              @click="deleteChunk(row)"
            >
              Delete
            </button>
          </div>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import BaseButton from "@/components/common/BaseButton.vue";
import { useTimerStore } from "@/stores/timerStore";

const props = defineProps({
  card: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["refresh-summary"]);

const timerStore = useTimerStore();
const chunksOpen = ref(false);
const isLoadingChunks = ref(false);
const editingSessionId = ref(null);
const draftHours = ref("0");
const draftMinutes = ref("0");
const draftSeconds = ref("0");

const isCurrentCardRunning = computed(
  () => timerStore.activeCardId === props.card.id && timerStore.hasActiveTimer,
);

const totalTrackedSeconds = computed(() =>
  timerStore.totalSecondsForCard(
    props.card.id,
    props.card.total_tracked_seconds || 0,
  ),
);

const displaySeconds = computed(() => totalTrackedSeconds.value);

const activeStartAt = computed(() => {
  const startedAt = timerStore.activeSession?.started_at;
  return startedAt ? new Date(startedAt).toISOString() : "-";
});

const sessions = computed(() => {
  const rows = timerStore.sessionsByCard?.[props.card.id] || [];
  return rows.map((row) => ({
    ...row,
    liveDurationSeconds: resolveDurationSeconds(row),
  }));
});

watch(
  () => props.card.id,
  async () => {
    chunksOpen.value = false;
    editingSessionId.value = null;
    await loadSessions();
  },
  { immediate: true },
);

async function loadSessions() {
  isLoadingChunks.value = true;
  try {
    await timerStore.fetchTimeSessions(props.card.id);
  } finally {
    isLoadingChunks.value = false;
  }
}

async function start() {
  await timerStore.startTimer(props.card.id);
  await emit("refresh-summary");
  await loadSessions();
}

async function stop() {
  await timerStore.stopTimer();
  await emit("refresh-summary");
  await loadSessions();
}

function startEdit(row) {
  if (!row.ended_at) {
    return;
  }
  const { hours, minutes, seconds } = toHms(resolveDurationSeconds(row));
  draftHours.value = String(hours);
  draftMinutes.value = String(minutes);
  draftSeconds.value = String(seconds);
  editingSessionId.value = row.id;
}

function cancelEdit() {
  editingSessionId.value = null;
}

async function saveEdit(row) {
  const hours = Math.max(0, Number.parseInt(draftHours.value, 10) || 0);
  const minutes = Math.max(0, Number.parseInt(draftMinutes.value, 10) || 0);
  const seconds = Math.max(0, Number.parseInt(draftSeconds.value, 10) || 0);
  const durationSeconds = (hours * 3600) + (minutes * 60) + seconds;
  await timerStore.updateTimeSession(row.id, durationSeconds);
  await emit("refresh-summary");
  await loadSessions();
  editingSessionId.value = null;
}

async function deleteChunk(row) {
  if (!row.ended_at) {
    return;
  }
  const ok = window.confirm("Delete this time chunk?");
  if (!ok) {
    return;
  }
  await timerStore.deleteTimeSession(row.id);
  await emit("refresh-summary");
  await loadSessions();
}

function resolveDurationSeconds(row) {
  if (!row) {
    return 0;
  }
  if (!row.ended_at && timerStore.activeSession?.id === row.id) {
    return timerStore.liveElapsedSeconds;
  }
  if (row.duration_seconds != null) {
    return Math.max(0, Number(row.duration_seconds) || 0);
  }
  if (row.ended_at && row.started_at) {
    const endMs = new Date(row.ended_at).getTime();
    const startMs = new Date(row.started_at).getTime();
    if (Number.isNaN(endMs) || Number.isNaN(startMs)) {
      return 0;
    }
    return Math.max(0, Math.floor((endMs - startMs) / 1000));
  }
  return 0;
}

function toHms(secondsValue) {
  const value = Math.max(0, Math.floor(Number(secondsValue || 0)));
  const hours = Math.floor(value / 3600);
  const minutes = Math.floor((value % 3600) / 60);
  const seconds = value % 60;
  return { hours, minutes, seconds };
}

function formatDateTime(isoValue) {
  if (!isoValue) {
    return "-";
  }
  const value = new Date(isoValue);
  if (Number.isNaN(value.getTime())) {
    return "-";
  }
  return value.toLocaleString();
}

function formatDuration(totalSeconds) {
  const value = Math.max(0, Math.floor(Number(totalSeconds || 0)));
  const hours = Math.floor(value / 3600);
  const minutes = Math.floor((value % 3600) / 60);
  const seconds = value % 60;
  const parts = [hours, minutes, seconds].map((part) =>
    String(part).padStart(2, "0"),
  );
  return parts.join(":");
}
</script>

<style scoped lang="less">
.panel {
  display: grid;
  gap: var(--space-2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: var(--space-3);
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(4px);
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

header h4 {
  margin: 0;
}

.time {
  font-family: ui-monospace, Menlo, Consolas, monospace;
  font-weight: 700;
}

.controls {
  display: flex;
  gap: var(--space-2);
}

.info {
  margin: 0;
  color: var(--text-muted);
  font-size: 12px;
}

.chunks-toggle {
  border: 1px solid var(--border);
  border-radius: 10px;
  background: #fff;
  color: var(--text);
  padding: 9px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
}

.chunks-toggle:hover {
  background: var(--surface-muted);
}

.toggle-meta {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--text-muted);
}

.caret {
  transition: transform 140ms ease;
}

.caret.open {
  transform: rotate(180deg);
}

.chunks-panel {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: var(--space-2);
  background: #fff;
}

.chunks-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}

.chunk-row {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: var(--space-2);
  align-items: center;
}

.chunk-main {
  min-width: 0;
  display: grid;
  gap: 7px;
}

.duration-wrap {
  display: inline-flex;
  gap: 8px;
  align-items: center;
}

.time-chip {
  border: 1px solid var(--border);
  background: #f8fafc;
  color: var(--text);
  border-radius: 999px;
  padding: 4px 8px;
  min-width: 54px;
  height: 28px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.time-chip:hover:not(:disabled) {
  background: #eef2f7;
}

.time-chip:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.time-chip.active {
  background: #ecfdf3;
  border-color: color-mix(in srgb, var(--primary) 40%, var(--border));
}

.duration-editor {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.time-chip.editable {
  cursor: text;
  gap: 4px;
  justify-content: center;
}

.time-chip.editable input {
  width: 24px;
  border: 0;
  outline: none;
  background: transparent;
  font-size: 12px;
  font-weight: 700;
  color: var(--text);
  text-align: right;
}

.time-chip.editable input::-webkit-outer-spin-button,
.time-chip.editable input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.time-chip.editable input[type=number] {
  -moz-appearance: textfield;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.running-tag {
  color: var(--primary);
  font-weight: 700;
}

.chunk-actions {
  display: flex;
  align-items: center;
}

.mini-link {
  border: 0;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 12px;
}

.mini-link:hover {
  color: var(--text);
}

.mini-link:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.mini-link.save {
  color: var(--primary);
  font-weight: 700;
}

.mini-link.danger {
  color: var(--danger);
}

.muted {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
}
</style>

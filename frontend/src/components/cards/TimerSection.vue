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

    <button v-if="showChunksToggle" type="button" class="chunks-toggle" @click="chunksOpen = !chunksOpen">
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
  const value = parseApiDate(startedAt);
  return value ? value.toISOString() : "-";
});

const sessions = computed(() => {
  const rows = timerStore.sessionsByCard?.[props.card.id] || [];
  return rows.map((row) => ({
    ...row,
    liveDurationSeconds: resolveDurationSeconds(row),
  }));
});

const showChunksToggle = computed(
  () => isCurrentCardRunning.value || sessions.value.length > 0 || totalTrackedSeconds.value > 0,
);

watch(
  () => props.card.id,
  async () => {
    chunksOpen.value = false;
    editingSessionId.value = null;
    await loadSessions();
  },
  { immediate: true },
);

watch(showChunksToggle, (visible) => {
  if (!visible) {
    chunksOpen.value = false;
  }
});

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
    const endDate = parseApiDate(row.ended_at);
    const startDate = parseApiDate(row.started_at);
    if (!endDate || !startDate) {
      return 0;
    }
    const endMs = endDate.getTime();
    const startMs = startDate.getTime();
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
  const value = parseApiDate(isoValue);
  if (!value) {
    return "-";
  }
  return value.toLocaleString();
}

function parseApiDate(value) {
  if (!value) {
    return null;
  }
  const raw = String(value);
  const hasZone = /(?:Z|[+-]\d{2}:\d{2})$/.test(raw);
  const normalized = hasZone ? raw : `${raw}Z`;
  const parsed = new Date(normalized);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }
  return parsed;
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
  gap: @space-2;
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(12px * @ui-scale);
  padding: @space-3;

  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(calc(4px * @ui-scale));
  @media (prefers-color-scheme: dark) {
    background-color: @surface-muted-dark;
    border-color:@surface-muted-dark;
  }
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
  /*font-family: ui-monospace, Menlo, Consolas, monospace;*/
  font-weight: 100;
  font-size: 20px;
    position: absolute;
    right:@space-3;
}

.controls {
  display: flex;
  gap: @space-2;
}

.info {
  margin: 0;
  color: @text-muted;
  font-size: calc(12px * @ui-scale);
}

.chunks-toggle {
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(10px * @ui-scale);
  background: #fff;
  color: @text;
  padding: calc(9px * @ui-scale) calc(12px * @ui-scale);
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  @media (prefers-color-scheme: dark) {
    background-color: @bg-dark;
    color:@text-dark;
    border-color:@surface-muted-dark;
  }
}

.chunks-toggle:hover {
  background: @surface-muted;
  @media (prefers-color-scheme: dark) {
    background-color: @bg-dark;
  }
}

.toggle-meta {
  display: inline-flex;
  align-items: center;
  gap: calc(6px * @ui-scale);
  color: @text-muted;
}

.caret {
  transition: transform 140ms ease;
}

.caret.open {
  transform: rotate(180deg);
}

.chunks-panel {
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(12px * @ui-scale);
  padding: @space-2;
  background: #fff;
}

.chunks-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: calc(8px * @ui-scale);
}

.chunk-row {
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(10px * @ui-scale);
  padding: calc(10px * @ui-scale);
  display: grid;
  grid-template-columns: 1fr auto;
  gap: @space-2;
  align-items: center;
}

.chunk-main {
  min-width: 0;
  display: grid;
  gap: calc(7px * @ui-scale);
}

.duration-wrap {
  display: inline-flex;
  gap: calc(8px * @ui-scale);
  align-items: center;
}

.time-chip {
  border: calc(1px * @ui-scale) solid @border;
  background: #f8fafc;
  color: @text;
  border-radius: calc(999px * @ui-scale);
  padding: calc(4px * @ui-scale) calc(8px * @ui-scale);
  min-width: calc(54px * @ui-scale);
  height: calc(28px * @ui-scale);
  font-size: calc(12px * @ui-scale);
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
  border-color: color-mix(in srgb, @primary 40%, @border);
}

.duration-editor {
  display: inline-flex;
  align-items: center;
  gap: calc(8px * @ui-scale);
}

.time-chip.editable {
  cursor: text;
  gap: calc(4px * @ui-scale);
  justify-content: center;
}

.time-chip.editable input {
  width: calc(24px * @ui-scale);
  border: 0;
  outline: none;
  background: transparent;
  font-size: calc(12px * @ui-scale);
  font-weight: 700;
  color: @text;
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
  gap: calc(8px * @ui-scale);
  font-size: calc(12px * @ui-scale);
  color: @text-muted;
}

.running-tag {
  color: @primary;
  font-weight: 700;
}

.chunk-actions {
  display: flex;
  align-items: center;
}

.mini-link {
  border: 0;
  background: transparent;
  color: @text-muted;
  cursor: pointer;
  font-size: calc(12px * @ui-scale);
}

.mini-link:hover {
  color: @text;
}

.mini-link:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.mini-link.save {
  color: @primary;
  font-weight: 700;
}

.mini-link.danger {
  color: @danger;
}

.muted {
  margin: 0;
  font-size: calc(12px * @ui-scale);
  color: @text-muted;
}
</style>



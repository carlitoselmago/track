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
  </section>
</template>

<script setup>
import { computed } from "vue";
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

async function start() {
  await timerStore.startTimer(props.card.id);
  await emit("refresh-summary");
}

async function stop() {
  await timerStore.stopTimer();
  await emit("refresh-summary");
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
  border-radius: var(--radius);
  padding: var(--space-3);
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
</style>


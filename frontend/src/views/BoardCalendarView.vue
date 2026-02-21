<template>
  <section class="container section">
    <div v-if="loading" class="loading-row">
      <LoadingSpinner />
    </div>

    <template v-else-if="boardStore.currentBoard">
      <BoardHeader :board="boardStore.currentBoard" :board-id="props.boardId" />
      <div class="content">
      <div class="toolbar">
        <button type="button" class="month-btn" @click="shiftMonth(-1)">Prev</button>
        <input v-model="selectedMonth" type="month" class="month-input" />
        <button type="button" class="month-btn" @click="shiftMonth(1)">Next</button>
        <span class="tz">Timezone: {{ calendar.timezone || "UTC" }}</span>
      </div>

      <div class="layout">
        <aside class="sidebar">
          <h3>Cards In {{ selectedMonth }}</h3>
          <p class="total">
            Active cards total: <strong>{{ formatDuration(activeCardsTotalSeconds) }}</strong>
          </p>
          <p v-if="calendar.cards.length === 0" class="muted">
            No worked cards for this month.
          </p>
          <label v-for="card in calendar.cards" :key="card.id" class="card-filter">
            <input
              type="checkbox"
              :checked="activeCardIds.has(card.id)"
              @change="toggleCard(card.id)"
            />
            <span class="name">{{ card.title }}</span>
            <span class="value">{{ formatDuration(card.total_seconds) }}</span>
          </label>
        </aside>

        <div class="calendar">
          <div class="weekday" v-for="dayName in weekdays" :key="dayName">
            {{ dayName }}
          </div>
          <article
            v-for="cell in calendarCells"
            :key="cell.key"
            class="day-cell"
            :class="{ muted: !cell.inMonth }"
          >
            <template v-if="cell.inMonth">
              <header class="day-head">
                <span class="date">{{ cell.dayNumber }}</span>
                <span class="daily-total">{{ formatDuration(cell.totalSeconds) }}</span>
              </header>
              <ul class="entries">
                <li v-for="entry in cell.entries" :key="`${cell.key}-${entry.card_id}`">
                  <span class="entry-name">{{ entry.card_title }}</span>
                  <span class="entry-seconds">{{ formatDuration(entry.seconds) }}</span>
                </li>
              </ul>
            </template>
          </article>
        </div>
      </div>
    </div>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import BoardHeader from "@/components/kanban/BoardHeader.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import { boardService } from "@/services/boardService";
import { useBoardStore } from "@/stores/boardStore";

const weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const props = defineProps({
  boardId: {
    type: [String, Number],
    required: true,
  },
});

const boardStore = useBoardStore();
const loading = ref(false);
const selectedMonth = ref(toMonthValue(new Date()));
const activeCardIds = ref(new Set());
const calendar = reactive({
  month: "",
  month_start: "",
  month_end: "",
  timezone: "UTC",
  cards: [],
  days: {},
});

const activeCardsTotalSeconds = computed(() =>
  calendar.cards
    .filter((card) => activeCardIds.value.has(card.id))
    .reduce((sum, card) => sum + (card.total_seconds || 0), 0),
);

const calendarCells = computed(() => {
  const [yearStr, monthStr] = selectedMonth.value.split("-");
  const year = Number(yearStr);
  const month = Number(monthStr);
  if (!year || !month) {
    return [];
  }

  const first = new Date(year, month - 1, 1);
  const firstWeekday = first.getDay();
  const monthDays = new Date(year, month, 0).getDate();

  const cells = [];
  const prevMonthDays = new Date(year, month - 1, 0).getDate();
  for (let i = firstWeekday - 1; i >= 0; i -= 1) {
    const day = prevMonthDays - i;
    cells.push({
      key: `prev-${day}`,
      inMonth: false,
      dayNumber: day,
      entries: [],
      totalSeconds: 0,
    });
  }

  for (let day = 1; day <= monthDays; day += 1) {
    const key = `${yearStr}-${monthStr}-${String(day).padStart(2, "0")}`;
    const data = calendar.days[key] || { cards: [], total_seconds: 0 };
    const entries = (data.cards || []).filter((entry) =>
      activeCardIds.value.has(entry.card_id),
    );
    const totalSeconds = entries.reduce((sum, entry) => sum + (entry.seconds || 0), 0);
    cells.push({
      key,
      inMonth: true,
      dayNumber: day,
      entries,
      totalSeconds,
    });
  }

  const trailing = (7 - (cells.length % 7)) % 7;
  for (let i = 1; i <= trailing; i += 1) {
    cells.push({
      key: `next-${i}`,
      inMonth: false,
      dayNumber: i,
      entries: [],
      totalSeconds: 0,
    });
  }

  return cells;
});

function toMonthValue(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  return `${year}-${month}`;
}

async function loadCalendar() {
  loading.value = true;
  try {
    const payload = await boardService.getBoardCalendar(props.boardId, selectedMonth.value);
    calendar.month = payload.month;
    calendar.month_start = payload.month_start;
    calendar.month_end = payload.month_end;
    calendar.timezone = payload.timezone || "UTC";
    calendar.cards = payload.cards || [];
    calendar.days = payload.days || {};
    activeCardIds.value = new Set(calendar.cards.map((card) => card.id));
  } finally {
    loading.value = false;
  }
}

function shiftMonth(delta) {
  const [yearStr, monthStr] = selectedMonth.value.split("-");
  const year = Number(yearStr);
  const month = Number(monthStr);
  const next = new Date(year, month - 1 + delta, 1);
  selectedMonth.value = toMonthValue(next);
}

function toggleCard(cardId) {
  const nextSet = new Set(activeCardIds.value);
  if (nextSet.has(cardId)) {
    nextSet.delete(cardId);
  } else {
    nextSet.add(cardId);
  }
  activeCardIds.value = nextSet;
}

function formatDuration(seconds) {
  const total = Math.max(0, Math.floor(seconds || 0));
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  return `${hours}h ${minutes}m`;
}

watch(
  () => props.boardId,
  async () => {
    await boardStore.loadBoard(props.boardId);
    await loadCalendar();
  },
);
watch(selectedMonth, () => loadCalendar());

onMounted(async () => {
  await boardStore.loadBoard(props.boardId);
  await loadCalendar();
});
</script>

<style scoped lang="less">
.section {
  display: grid;
  gap: var(--space-4);
}

.loading-row {
  display: flex;
  justify-content: center;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  background: var(--surface);
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-3);
  margin-bottom: var(--space-3);
}

.month-btn {
  border: calc(1px * var(--ui-scale)) solid var(--border);
  background: #fff;
  border-radius: calc(8px * var(--ui-scale));
  padding: calc(7px * var(--ui-scale)) calc(10px * var(--ui-scale));
  cursor: pointer;
}

.month-input {
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: calc(8px * var(--ui-scale));
  padding: calc(7px * var(--ui-scale)) calc(10px * var(--ui-scale));
}

.tz {
  margin-left: auto;
  color: var(--text-muted);
  font-size: calc(12px * var(--ui-scale));
}

.layout {
  display: grid;
  grid-template-columns: calc(280px * var(--ui-scale)) 1fr;
  gap: var(--space-3);
}

.sidebar {
  background: var(--surface);
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
  align-content: start;
  max-height: calc(100vh - calc(230px * var(--ui-scale)));
  overflow: auto;
}

.sidebar h3 {
  margin: 0;
}

.total {
  margin: 0 0 var(--space-2);
  font-size: calc(13px * var(--ui-scale));
}

.muted {
  color: var(--text-muted);
  font-size: calc(13px * var(--ui-scale));
  margin: 0;
}

.card-filter {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: var(--space-2);
  font-size: calc(13px * var(--ui-scale));
}

.name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.value {
  color: var(--text-muted);
}

.calendar {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: calc(1px * var(--ui-scale));
  background: var(--border);
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.weekday {
  background: #f3f6fb;
  padding: calc(8px * var(--ui-scale));
  font-weight: 700;
  font-size: calc(12px * var(--ui-scale));
  text-transform: uppercase;
  color: var(--text-muted);
}

.day-cell {
  min-height: calc(150px * var(--ui-scale));
  background: var(--surface);
  padding: calc(8px * var(--ui-scale));
  display: grid;
  gap: calc(8px * var(--ui-scale));
  align-content: start;
}

.day-cell.muted {
  background: #f8fafc;
}

.day-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: calc(8px * var(--ui-scale));
}

.date {
  font-weight: 700;
}

.daily-total {
  font-size: calc(12px * var(--ui-scale));
  color: var(--primary);
  font-weight: 700;
}

.entries {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: calc(6px * var(--ui-scale));
}

.entries li {
  display: flex;
  justify-content: space-between;
  gap: calc(8px * var(--ui-scale));
  font-size: calc(12px * var(--ui-scale));
}

.entry-name {
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.entry-seconds {
  color: var(--text-muted);
  white-space: nowrap;
}

@media (max-width: 784px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    max-height: none;
  }
}
</style>



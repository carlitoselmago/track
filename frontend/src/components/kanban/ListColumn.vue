<template>
  <section class="column">
    <header class="header">
      <button
        type="button"
        class="list-drag-handle"
        aria-label="Drag list"
        title="Drag list"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M9 6h6M9 12h6M9 18h6" />
        </svg>
      </button>

      <input
        :value="list.title"
        class="title-input"
        @change="renameList($event.target.value)"
      />
      <ActionMenu
        :items="listActions"
        @select="onActionSelect"
      />
    </header>

    <draggable
      v-model="list.cards"
      item-key="id"
      group="cards"
      class="cards"
      :data-list-id="list.id"
      @start="$emit('card-drag-start')"
      @end="onCardDragEnd"
    >
      <template #item="{ element }">
        <CardItem
          :card="element"
          :is-active-timer="activeTimerCardId === element.id"
          @open="$emit('open-card', $event)"
        />
      </template>
    </draggable>

    <AddCardForm @create="(title) => $emit('add-card', { listId: list.id, title })" />
  </section>
</template>

<script setup>
import draggable from "vuedraggable";
import ActionMenu from "@/components/common/ActionMenu.vue";
import AddCardForm from "./AddCardForm.vue";
import CardItem from "./CardItem.vue";

const props = defineProps({
  list: {
    type: Object,
    required: true,
  },
  activeTimerCardId: {
    type: [Number, String],
    default: null,
  },
});

const emit = defineEmits([
  "add-card",
  "open-card",
  "delete-list",
  "rename-list",
  "card-drag-start",
  "card-drag-end",
]);

const listActions = [{ label: "Delete", value: "delete", variant: "danger" }];

function onCardDragEnd(evt) {
  const fromListId = Number(evt.from?.dataset?.listId || props.list.id);
  const toListId = Number(evt.to?.dataset?.listId || props.list.id);
  emit("card-drag-end", {
    fromListId,
    toListId,
    oldIndex: evt.oldIndex,
    newIndex: evt.newIndex,
  });
}

function renameList(nextTitle) {
  const title = (nextTitle || "").trim();
  if (!title || title === props.list.title) {
    return;
  }
  emit("rename-list", {
    listId: props.list.id,
    title,
  });
}

function onActionSelect(action) {
  if (action === "delete") {
    emit("delete-list", props.list.id);
  }
}
</script>

<style scoped lang="less">
.column {
  width: calc(300px * var(--ui-scale));
  min-width: calc(300px * var(--ui-scale));
  background: #ebebeb;
  
  border-radius: var(--radius);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
  align-content: start;
  max-height: calc(100vh - calc(220px * var(--ui-scale)));
  @media (max-width: 615px) {
    max-height: 100%;
  }
}

.header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin: 0;
}

.list-drag-handle {
  border: calc(1px * var(--ui-scale)) solid var(--border);
  width: calc(28px * var(--ui-scale));
  height: calc(28px * var(--ui-scale));
  border-radius: calc(8px * var(--ui-scale));
  background: #fff;
  color: var(--text-muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  flex-shrink: 0;
}

.list-drag-handle:active {
  cursor: grabbing;
}

.list-drag-handle svg {
  width: calc(14px * var(--ui-scale));
  height: calc(14px * var(--ui-scale));
  fill: none;
  stroke: currentColor;
  stroke-width: 2.1;
  stroke-linecap: round;
}

.title-input {
  flex: 1;
  border: 0;
  border-radius: calc(8px * var(--ui-scale));
  padding: 0 calc(10px * var(--ui-scale));
  font-weight: 700;
  background: transparent;
  &:focus{
    outline: none;
  }
}

.cards {
  display: grid;
  gap: var(--space-2);
  overflow: auto;
  min-height: 0;
}
</style>



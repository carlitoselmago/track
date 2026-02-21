<template>
  <section class="column">
    <header class="header">
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
  width: 300px;
  min-width: 300px;
  background: #ebebeb;
  
  border-radius: var(--radius);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-3);
  align-content: start;
  max-height: calc(100vh - 220px);
}

.header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin: 0px;
}

.title-input {
  flex: 1;
  border: 0px;
  border-radius: 8px;
  padding: 0px 10px;
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
  min-height: 20px;
}
</style>

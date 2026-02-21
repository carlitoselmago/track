<template>
  <section class="container section">
    <div class="content">
      <header class="header">
        <h1>Admin: Users</h1>
      </header>

      <form class="create-form" @submit.prevent="createUser">
        <BaseInput v-model="form.fullName" label="Full name" placeholder="Jane Doe" />
        <BaseInput v-model="form.email" label="Email" placeholder="jane@example.com" />
        <BaseInput v-model="form.password" label="Password" type="password" />
        <label class="checkbox-row">
          <input v-model="form.isSystemAdmin" type="checkbox" />
          <span>System admin</span>
        </label>

        <label class="field">
          <span>Assign boards</span>
          <select v-model="form.boardIds" multiple class="multiselect">
            <option v-for="board in boardStore.boards" :key="board.id" :value="board.id">
              {{ board.name }}
            </option>
          </select>
        </label>
        <BaseButton type="submit">Create user</BaseButton>
      </form>

      <div class="list">
        <article v-for="user in users" :key="user.id" class="user-row">
          <div>
            <strong>{{ user.full_name || user.name }}</strong>
            <p>{{ user.email }}</p>
          </div>
          <div class="assign-row">
            <select v-model="boardByUser[user.id]" class="select">
              <option value="">Assign to board...</option>
              <option v-for="board in boardStore.boards" :key="board.id" :value="String(board.id)">
                {{ board.name }}
              </option>
            </select>
            <button type="button" class="btn" @click="assignUserToBoard(user.id)">Assign</button>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import BaseInput from "@/components/common/BaseInput.vue";
import BaseButton from "@/components/common/BaseButton.vue";
import { userService } from "@/services/userService";
import { useBoardStore } from "@/stores/boardStore";

const boardStore = useBoardStore();
const users = ref([]);
const boardByUser = reactive({});
const form = reactive({
  fullName: "",
  email: "",
  password: "",
  isSystemAdmin: false,
  boardIds: [],
});

onMounted(async () => {
  await Promise.all([loadUsers(), boardStore.fetchBoards()]);
});

async function loadUsers() {
  users.value = await userService.listUsers();
}

async function createUser() {
  if (!form.fullName.trim() || !form.email.trim() || !form.password) {
    return;
  }
  await userService.createUser({
    full_name: form.fullName.trim(),
    email: form.email.trim(),
    password: form.password,
    is_system_admin: form.isSystemAdmin,
    board_ids: form.boardIds.map((value) => Number(value)),
  });
  form.fullName = "";
  form.email = "";
  form.password = "";
  form.isSystemAdmin = false;
  form.boardIds = [];
  await loadUsers();
}

async function assignUserToBoard(userId) {
  const boardId = Number(boardByUser[userId]);
  if (!boardId) {
    return;
  }
  await boardStore.addBoardMember(boardId, userId, "member");
  boardByUser[userId] = "";
}
</script>

<style scoped lang="less">
.section {
  display: grid;
  gap: var(--space-4);
}

.header h1 {
  margin: 0;
}

.create-form {
  display: grid;
  gap: var(--space-2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: #fff;
  padding: var(--space-3);
  margin-bottom: var(--space-3);
}

.checkbox-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.field {
  display: grid;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
}

.multiselect,
.select {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px;
  background: #fff;
}

.list {
  display: grid;
  gap: var(--space-2);
}

.user-row {
  border: 1px solid var(--border);
  border-radius: 10px;
  background: #fff;
  padding: var(--space-3);
  display: grid;
  grid-template-columns: 1fr auto;
  gap: var(--space-2);
  align-items: center;
}

.user-row p {
  margin: 4px 0 0;
  color: var(--text-muted);
  font-size: 13px;
}

.assign-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 10px;
  background: var(--surface-muted);
  cursor: pointer;
}
</style>

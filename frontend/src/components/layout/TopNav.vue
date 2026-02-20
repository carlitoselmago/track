<template>
  <nav class="topnav">
    <div class="container row">
      <RouterLink to="/boards" class="brand">Track</RouterLink>
      <div class="right">
        <span class="user">{{ authStore.user?.email || "Unknown user" }}</span>
        <BaseButton variant="subtle" @click="onLogout">Logout</BaseButton>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { RouterLink, useRouter } from "vue-router";
import BaseButton from "@/components/common/BaseButton.vue";
import { useAuthStore } from "@/stores/authStore";

const router = useRouter();
const authStore = useAuthStore();

async function onLogout() {
  await authStore.logout();
  router.push({ name: "login" });
}
</script>

<style scoped>
.topnav {
  position: sticky;
  top: 0;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
  z-index: 10;
}

.row {
  min-height: 62px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  font-weight: 800;
  font-size: 22px;
  color: var(--primary);
}

.right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.user {
  color: var(--text-muted);
  font-size: 13px;
}
</style>

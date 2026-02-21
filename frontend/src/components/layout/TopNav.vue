<template>
  <nav class="topnav">
    <div class="container row">
      <div class="left">
        <RouterLink to="/boards" class="brand">Track</RouterLink>
        <RouterLink
          v-if="authStore.user?.is_system_admin"
          to="/admin/users"
          class="admin-link"
        >
          Admin
        </RouterLink>
      </div>

      <div class="right">
        <div class="notification-wrap">
          <button
            type="button"
            class="bell"
            :class="{ active: notificationStore.hasUnread }"
            @click="toggleNotifications"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 3a5 5 0 00-5 5v3.8c0 .7-.2 1.3-.6 1.8L5 15.2c-.4.5 0 1.3.7 1.3h12.6c.7 0 1.1-.8.7-1.3l-1.4-1.6c-.4-.5-.6-1.1-.6-1.8V8a5 5 0 00-5-5zM10 19a2 2 0 004 0" />
            </svg>
          </button>

          <div v-if="isNotificationsOpen" class="notifications-panel">
            <header>
              <strong>Notifications</strong>
              <button type="button" class="mini-link" @click="clearAllNotifications">Clear all</button>
            </header>
            <p v-if="!notificationStore.items.length" class="muted">No notifications</p>
            <ul v-else>
              <li v-for="item in notificationStore.items" :key="item.id">
                <div class="item-main">
                  <strong>{{ item.title }}</strong>
                  <p>{{ item.message }}</p>
                  <small>{{ formatDate(item.created_at) }}</small>
                </div>
                <button type="button" class="mini-link danger" @click="removeNotification(item.id)">
                  Clear
                </button>
              </li>
            </ul>
          </div>
        </div>

        <span class="user">{{ authStore.user?.full_name || authStore.user?.email || "Unknown user" }}</span>
        <BaseButton variant="subtle" @click="isSettingsOpen = true">Settings</BaseButton>
        <BaseButton variant="subtle" @click="onLogout">Logout</BaseButton>
      </div>
    </div>
  </nav>

  <BaseModal v-model="isSettingsOpen" title="Account settings">
    <div class="settings-grid">
      <label class="toggle-row">
        <input
          v-model="emailNotificationsEnabled"
          type="checkbox"
        />
        <span>Email notifications</span>
      </label>
      <BaseButton variant="subtle" @click="saveEmailPreference">Save notification preference</BaseButton>

      <BaseInput
        v-model="newPassword"
        label="New password"
        type="password"
        placeholder="At least 8 characters"
      />
      <BaseButton variant="subtle" @click="changePassword">Change password</BaseButton>
    </div>
  </BaseModal>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";
import BaseButton from "@/components/common/BaseButton.vue";
import BaseInput from "@/components/common/BaseInput.vue";
import BaseModal from "@/components/common/BaseModal.vue";
import { useAuthStore } from "@/stores/authStore";
import { useNotificationStore } from "@/stores/notificationStore";
import { userService } from "@/services/userService";

const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const isNotificationsOpen = ref(false);
const isSettingsOpen = ref(false);
const emailNotificationsEnabled = ref(true);
const newPassword = ref("");

onMounted(async () => {
  if (authStore.isAuthenticated) {
    await notificationStore.fetchNotifications();
    const pref = await userService.getEmailPreference();
    emailNotificationsEnabled.value = Boolean(pref?.email_notifications_enabled);
  }
});

async function onLogout() {
  await authStore.logout();
  router.push({ name: "login" });
}

async function toggleNotifications() {
  isNotificationsOpen.value = !isNotificationsOpen.value;
  if (isNotificationsOpen.value) {
    await notificationStore.fetchNotifications();
    await notificationStore.markAllRead();
  }
}

async function removeNotification(notificationId) {
  await notificationStore.deleteNotification(notificationId);
}

async function clearAllNotifications() {
  await notificationStore.clearAll();
}

async function saveEmailPreference() {
  await userService.updateEmailPreference(emailNotificationsEnabled.value);
}

async function changePassword() {
  if (!newPassword.value || newPassword.value.length < 8) {
    return;
  }
  await userService.changePassword(newPassword.value);
  newPassword.value = "";
}

function formatDate(iso) {
  if (!iso) {
    return "-";
  }
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return "-";
  }
  return date.toLocaleString();
}
</script>

<style scoped lang="less">
.topnav {
  position: sticky;
  top: 0;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
  z-index: 30;
  padding: 0 var(--space-4);
}

.row {
  min-height: 62px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.brand {
  font-weight: 800;
  font-size: 22px;
  color: var(--primary);
}

.admin-link {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 5px 10px;
  font-size: 12px;
}

.right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.user {
  color: var(--text-muted);
  font-size: 13px;
}

.notification-wrap {
  position: relative;
}

.bell {
  border: 1px solid var(--border);
  background: #fff;
  color: #94a3b8;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.bell svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.bell.active {
  color: var(--primary);
  border-color: color-mix(in srgb, var(--primary) 40%, var(--border));
  background: #ecfdf3;
}

.notifications-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: min(420px, 88vw);
  border: 1px solid var(--border);
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.14);
  padding: var(--space-2);
  z-index: 40;
}

.notifications-panel header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px;
}

.notifications-panel ul {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 340px;
  overflow: auto;
  display: grid;
  gap: 6px;
}

.notifications-panel li {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 8px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
}

.item-main strong {
  display: block;
  font-size: 13px;
}

.item-main p {
  margin: 4px 0;
  font-size: 12px;
  color: var(--text-muted);
}

.item-main small {
  color: var(--text-muted);
  font-size: 11px;
}

.mini-link {
  border: 0;
  background: transparent;
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
}

.mini-link.danger {
  color: var(--danger);
}

.muted {
  margin: 6px;
  font-size: 12px;
  color: var(--text-muted);
}

.settings-grid {
  display: grid;
  gap: var(--space-3);
}

.toggle-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
</style>

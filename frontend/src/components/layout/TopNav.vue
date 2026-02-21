<template>
  <nav class="topnav">
    <div class=" row">
      <div class="left">
        <RouterLink to="/boards" class="brand" aria-label="Track home">
          <img src="/logo.svg" alt="Track" class="brand-logo" />
        </RouterLink>
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
  backdrop-filter: blur(calc(8px * @ui-scale));

  z-index: 30;
  padding: 0 @space-4;
  @media (prefers-color-scheme: dark) {
    background:@bg-dark;
  }
}

.row {
  min-height: calc(62px * @ui-scale);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.left {
  display: flex;
  align-items: center;
  gap: @space-3;
}

.brand {
  display: inline-flex;
  align-items: center;
}

.brand-logo {
  display: block;
  height: calc(24px * @ui-scale);
  width: auto;
}

.admin-link {
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(999px * @ui-scale);
  padding: calc(5px * @ui-scale) calc(10px * @ui-scale);
  font-size: calc(12px * @ui-scale);
}

.right {
  display: flex;
  align-items: center;
  gap: @space-2;
}

.user {
  color: @text-muted;
  font-size: calc(13px * @ui-scale);
}

.notification-wrap {
  position: relative;
}

.bell {
  border: calc(1px * @ui-scale) solid @border;
  background: #fff;
  color: #94a3b8;
  width: calc(34px * @ui-scale);
  height: calc(34px * @ui-scale);
  border-radius: calc(10px * @ui-scale);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.bell svg {
  width: calc(16px * @ui-scale);
  height: calc(16px * @ui-scale);
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.bell.active {
  color: @primary;
  border-color: color-mix(in srgb, @primary 40%, @border);
  background: #ecfdf3;
}

.notifications-panel {
  position: absolute;
  top: calc(100% + calc(8px * @ui-scale));
  right: 0;
  width: min(calc(420px * @ui-scale), 88vw);
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(12px * @ui-scale);
  background: #fff;
  box-shadow: 0 calc(12px * @ui-scale) calc(30px * @ui-scale) rgba(15, 23, 42, 0.14);
  padding: @space-2;
  z-index: 40;
}

.notifications-panel header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: calc(6px * @ui-scale);
}

.notifications-panel ul {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: calc(340px * @ui-scale);
  overflow: auto;
  display: grid;
  gap: calc(6px * @ui-scale);
}

.notifications-panel li {
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(10px * @ui-scale);
  padding: calc(8px * @ui-scale);
  display: grid;
  grid-template-columns: 1fr auto;
  gap: calc(8px * @ui-scale);
}

.item-main strong {
  display: block;
  font-size: calc(13px * @ui-scale);
}

.item-main p {
  margin: calc(4px * @ui-scale) 0;
  font-size: calc(12px * @ui-scale);
  color: @text-muted;
}

.item-main small {
  color: @text-muted;
  font-size: calc(11px * @ui-scale);
}

.mini-link {
  border: 0;
  background: transparent;
  color: @text-muted;
  font-size: calc(12px * @ui-scale);
  cursor: pointer;
}

.mini-link.danger {
  color: @danger;
}

.muted {
  margin: calc(6px * @ui-scale);
  font-size: calc(12px * @ui-scale);
  color: @text-muted;
}

.settings-grid {
  display: grid;
  gap: @space-3;
}

.toggle-row {
  display: inline-flex;
  align-items: center;
  gap: calc(8px * @ui-scale);
  font-size: calc(13px * @ui-scale);
}
</style>



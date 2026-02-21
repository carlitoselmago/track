import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { notificationService } from "@/services/notificationService";
import { normalizeApiError } from "@/services/axios";
import { useUiStore } from "./uiStore";

const extractPayload = (payload) => payload?.data || payload;

export const useNotificationStore = defineStore("notification", () => {
  const items = ref([]);
  const unreadCount = ref(0);
  const isLoading = ref(false);

  const hasUnread = computed(() => unreadCount.value > 0);

  async function fetchNotifications() {
    const uiStore = useUiStore();
    isLoading.value = true;
    try {
      const payload = extractPayload(await notificationService.list());
      items.value = payload.items || [];
      unreadCount.value = payload.unread_count || 0;
      return items.value;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    } finally {
      isLoading.value = false;
    }
  }

  async function markAllRead() {
    await notificationService.markAllRead();
    items.value = items.value.map((item) => ({ ...item, is_read: true }));
    unreadCount.value = 0;
  }

  async function deleteNotification(notificationId) {
    await notificationService.deleteOne(notificationId);
    const target = items.value.find((item) => item.id === notificationId);
    if (target && !target.is_read) {
      unreadCount.value = Math.max(0, unreadCount.value - 1);
    }
    items.value = items.value.filter((item) => item.id !== notificationId);
  }

  async function clearAll() {
    await notificationService.clearAll();
    items.value = [];
    unreadCount.value = 0;
  }

  function reset() {
    items.value = [];
    unreadCount.value = 0;
  }

  return {
    items,
    unreadCount,
    isLoading,
    hasUnread,
    fetchNotifications,
    markAllRead,
    deleteNotification,
    clearAll,
    reset,
  };
});

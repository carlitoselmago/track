import { useAuthStore } from "@/stores/authStore";

export function setupRouterGuards(router, pinia) {
  router.beforeEach(async (to) => {
    const authStore = useAuthStore(pinia);

    if (!authStore.isBootstrapped) {
      await authStore.bootstrapSession();
    }

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      return {
        name: "login",
        query: { redirect: to.fullPath },
      };
    }

    if (to.meta.guestOnly && authStore.isAuthenticated) {
      return { name: "boards" };
    }

    return true;
  });
}

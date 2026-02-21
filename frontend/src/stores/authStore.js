import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { authService } from "@/services/authService";
import { configureApiAuth, normalizeApiError } from "@/services/axios";
import { useUiStore } from "./uiStore";
import { useTimerStore } from "./timerStore";
import { useNotificationStore } from "./notificationStore";

const AUTH_META_KEY = "track_auth_meta_v1";
const AUTH_TOKEN_TTL_MS = 24 * 60 * 60 * 1000;

const parseJson = (value, fallback = null) => {
  try {
    return JSON.parse(value);
  } catch {
    return fallback;
  }
};

const extractToken = (payload) =>
  payload?.access_token ||
  payload?.accessToken ||
  payload?.token ||
  payload?.data?.access_token ||
  payload?.data?.accessToken ||
  null;

const extractUser = (payload) =>
  payload?.user || payload?.data?.user || payload?.data || null;

export const useAuthStore = defineStore("auth", () => {
  const storedMeta = parseJson(localStorage.getItem(AUTH_META_KEY), {});
  const user = ref(storedMeta?.user || null);
  const accessToken = ref(storedMeta?.accessToken || null);
  const tokenIssuedAt = ref(storedMeta?.tokenIssuedAt || null);
  const isBootstrapped = ref(false);
  const bootstrapPromise = ref(null);

  const isAuthenticated = computed(
    () => Boolean(user.value) && Boolean(accessToken.value) && !isTokenExpired(),
  );

  function isTokenExpired() {
    if (!tokenIssuedAt.value) {
      return true;
    }
    return Date.now() - Number(tokenIssuedAt.value) > AUTH_TOKEN_TTL_MS;
  }

  function persistMeta() {
    localStorage.setItem(
      AUTH_META_KEY,
      JSON.stringify({
        user: user.value,
        accessToken: accessToken.value,
        tokenIssuedAt: tokenIssuedAt.value,
      }),
    );
  }

  function clearAuthMeta() {
    localStorage.removeItem(AUTH_META_KEY);
  }

  function setAccessToken(token) {
    accessToken.value = token || null;
    tokenIssuedAt.value = token ? Date.now() : null;
    persistMeta();
  }

  async function configureAxiosAuth() {
    configureApiAuth({
      getAccessToken: () => accessToken.value,
      refreshAccessToken,
      onAuthFailure: forceLogout,
    });
  }

  async function login(credentials) {
    const uiStore = useUiStore();
    uiStore.clearError();

    try {
      const payload = await authService.login(credentials);
      const token = extractToken(payload);

      if (!token) {
        throw new Error("Login succeeded but no access token was returned.");
      }

      setAccessToken(token);
      user.value = extractUser(payload) || user.value;

      if (!user.value) {
        const mePayload = await authService.me();
        user.value = extractUser(mePayload);
      }

      persistMeta();
      return user.value;
    } catch (error) {
      const normalized = normalizeApiError(error);
      uiStore.setError(normalized.message);
      throw normalized;
    }
  }

  async function refreshAccessToken() {
    const payload = await authService.refresh();
    const token = extractToken(payload);

    if (!token) {
      throw new Error("No access token returned from refresh.");
    }

    setAccessToken(token);
    const refreshedUser = extractUser(payload);
    if (refreshedUser) {
      user.value = refreshedUser;
      persistMeta();
    }

    return token;
  }

  async function fetchMe() {
    const payload = await authService.me();
    user.value = extractUser(payload);
    persistMeta();
    return user.value;
  }

  async function bootstrapSession() {
    if (isBootstrapped.value) {
      return isAuthenticated.value;
    }

    if (bootstrapPromise.value) {
      return bootstrapPromise.value;
    }

    bootstrapPromise.value = (async () => {
      try {
        if (accessToken.value && user.value && !isTokenExpired()) {
          isBootstrapped.value = true;
          return true;
        }

        await refreshAccessToken();

        if (!user.value) {
          await fetchMe();
        }
      } catch {
        await forceLogout(false);
      } finally {
        isBootstrapped.value = true;
        bootstrapPromise.value = null;
      }
      return isAuthenticated.value;
    })();

    return bootstrapPromise.value;
  }

  async function logout() {
    try {
      await authService.logout();
    } catch {
      // Intentionally ignore network/logout endpoint errors.
    } finally {
      await forceLogout();
    }
  }

  async function forceLogout(resetBootstrap = true) {
    const timerStore = useTimerStore();
    const notificationStore = useNotificationStore();
    timerStore.clearActiveTimer();
    notificationStore.reset();

    setAccessToken(null);
    user.value = null;
    tokenIssuedAt.value = null;
    clearAuthMeta();
    if (resetBootstrap) {
      isBootstrapped.value = true;
    }
  }

  return {
    user,
    accessToken,
    isBootstrapped,
    isAuthenticated,
    configureAxiosAuth,
    login,
    refreshAccessToken,
    fetchMe,
    bootstrapSession,
    logout,
    forceLogout,
    setAccessToken,
  };
});

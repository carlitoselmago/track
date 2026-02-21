import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

let tokenGetter = () => null;
let refreshHandler = async () => null;
let authFailureHandler = async () => {};
let isRefreshing = false;
let pendingQueue = [];

const isAuthPath = (url = "") =>
  url.includes("/auth/login") ||
  url.includes("/auth/refresh") ||
  url.includes("/auth/logout");

const flushQueue = (error, token = null) => {
  pendingQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
      return;
    }
    resolve(token);
  });
  pendingQueue = [];
};

export function normalizeApiError(error) {
  const status = error?.response?.status;
  const payload = error?.response?.data || {};
  const message =
    payload.detail ||
    payload.message ||
    error.message ||
    "Something went wrong while talking to the API.";

  return {
    status,
    message,
    details: payload,
  };
}

export function configureApiAuth({
  getAccessToken,
  refreshAccessToken,
  onAuthFailure,
}) {
  tokenGetter = getAccessToken || tokenGetter;
  refreshHandler = refreshAccessToken || refreshHandler;
  authFailureHandler = onAuthFailure || authFailureHandler;
}

api.interceptors.request.use((config) => {
  const token = tokenGetter();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config || {};
    const status = error.response?.status;

    if (
      status !== 401 ||
      originalRequest._retry ||
      isAuthPath(originalRequest.url)
    ) {
      return Promise.reject(normalizeApiError(error));
    }

    originalRequest._retry = true;

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingQueue.push({ resolve, reject });
      })
        .then((newToken) => {
          if (newToken) {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
          }
          return api(originalRequest);
        })
        .catch((queueError) => Promise.reject(normalizeApiError(queueError)));
    }

    isRefreshing = true;

    try {
      const newToken = await refreshHandler();
      flushQueue(null, newToken);

      if (newToken) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
      }

      return api(originalRequest);
    } catch (refreshError) {
      flushQueue(refreshError);
      await authFailureHandler();
      return Promise.reject(normalizeApiError(refreshError));
    } finally {
      isRefreshing = false;
    }
  },
);

export { API_BASE_URL };

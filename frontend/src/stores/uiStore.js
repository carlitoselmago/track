import { defineStore } from "pinia";
import { ref } from "vue";

export const useUiStore = defineStore("ui", () => {
  const errorMessage = ref("");
  const globalLoading = ref(false);

  function setError(message) {
    errorMessage.value = message || "An unexpected error occurred.";
  }

  function clearError() {
    errorMessage.value = "";
  }

  function setLoading(value) {
    globalLoading.value = Boolean(value);
  }

  return {
    errorMessage,
    globalLoading,
    setError,
    clearError,
    setLoading,
  };
});

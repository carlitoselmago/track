import { beforeEach, describe, expect, it, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { useAuthStore } from "@/stores/authStore";
import { authService } from "@/services/authService";

vi.mock("@/services/authService", () => ({
  authService: {
    login: vi.fn(),
    refresh: vi.fn(),
    me: vi.fn(),
    logout: vi.fn(),
  },
}));

describe("authStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
    vi.clearAllMocks();
  });

  it("logs in and stores user/token", async () => {
    authService.login.mockResolvedValue({
      access_token: "token-1",
      user: { id: 1, email: "user@example.com" },
    });

    const store = useAuthStore();
    await store.login({ email: "user@example.com", password: "x" });

    expect(store.accessToken).toBe("token-1");
    expect(store.user.email).toBe("user@example.com");
    expect(store.isAuthenticated).toBe(true);
  });

  it("bootstraps from refresh + me", async () => {
    authService.refresh.mockResolvedValue({ access_token: "token-2" });
    authService.me.mockResolvedValue({ data: { id: 2, email: "boot@example.com" } });

    const store = useAuthStore();
    await store.bootstrapSession();

    expect(store.isBootstrapped).toBe(true);
    expect(store.accessToken).toBe("token-2");
    expect(store.user.email).toBe("boot@example.com");
  });
});

import { beforeEach, describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createRouter, createMemoryHistory } from "vue-router";
import LoginView from "@/views/LoginView.vue";
import { useAuthStore } from "@/stores/authStore";

vi.mock("@/services/authService", () => ({
  authService: {
    login: vi.fn().mockResolvedValue({
      access_token: "token-a",
      user: { id: 1, email: "a@test.com" },
    }),
    refresh: vi.fn(),
    me: vi.fn(),
    logout: vi.fn(),
  },
}));

describe("LoginView", () => {
  let pinia;

  beforeEach(() => {
    pinia = createPinia();
    setActivePinia(pinia);
    localStorage.clear();
    vi.clearAllMocks();
  });

  it("renders and submits login form", async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: "/login", component: LoginView },
        { path: "/boards", component: { template: "<div>Boards</div>" } },
      ],
    });
    router.push("/login");
    await router.isReady();

    const wrapper = mount(LoginView, {
      global: {
        plugins: [pinia, router],
      },
    });

    const authStore = useAuthStore();
    const spy = vi.spyOn(authStore, "login");

    const inputs = wrapper.findAll("input");
    await inputs[0].setValue("a@test.com");
    await inputs[1].setValue("pw");
    await wrapper.find("form").trigger("submit.prevent");

    expect(spy).toHaveBeenCalledOnce();
  });
});

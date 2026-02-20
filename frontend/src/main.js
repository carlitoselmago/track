import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import { setupRouterGuards } from "./router/guards";
import { useAuthStore } from "./stores/authStore";
import { useTimerStore } from "./stores/timerStore";
import "./styles/tokens.css";
import "./styles/base.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);

async function bootstrap() {
  const authStore = useAuthStore(pinia);
  authStore.configureAxiosAuth();
  await authStore.bootstrapSession();

  if (authStore.isAuthenticated) {
    const timerStore = useTimerStore(pinia);
    await timerStore.bootstrapActiveTimer();
  }

  setupRouterGuards(router, pinia);
  app.use(router);
  app.mount("#app");
}

bootstrap();

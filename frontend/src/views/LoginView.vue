<template>
  <section class="login-page">
    <div class="panel">
      <h1>Track</h1>
      <p>Sign in to continue.</p>
      <form class="form" @submit.prevent="submit">
        <BaseInput v-model="email" label="Email" type="email" placeholder="you@company.com" />
        <BaseInput
          v-model="password"
          label="Password"
          type="password"
          placeholder="Your password"
        />
        <BaseButton type="submit" block :loading="loading">Log in</BaseButton>
      </form>
    </div>
  </section>
</template>

<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import BaseInput from "@/components/common/BaseInput.vue";
import BaseButton from "@/components/common/BaseButton.vue";
import { useAuthStore } from "@/stores/authStore";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const email = ref("");
const password = ref("");
const loading = ref(false);

async function submit() {
  if (!email.value || !password.value) {
    return;
  }
  loading.value = true;
  try {
    await authStore.login({
      email: email.value.trim(),
      password: password.value,
    });
    await router.push(route.query.redirect || "/boards");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped lang="less">
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: var(--space-4);
}

.panel {
  width: min(calc(430px * var(--ui-scale)), 100%);
  background: var(--surface);
  border: calc(1px * var(--ui-scale)) solid var(--border);
  border-radius: calc(14px * var(--ui-scale));
  padding: var(--space-6);
  box-shadow: var(--shadow);
}

h1 {
  margin: 0;
  font-size: calc(30px * var(--ui-scale));
}

p {
  margin: calc(6px * var(--ui-scale)) 0 var(--space-4);
  color: var(--text-muted);
}

.form {
  display: grid;
  gap: var(--space-3);
}
</style>



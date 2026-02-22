<template>
  <section class="login-page">
    <div class="panel">
      <img src="/logo.svg" alt="Track" class="brand-logo" />
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
  padding: @space-4;
  .brand-logo{
    margin-top: 6px;
  }
 
}

.panel {
  width: min(calc(430px * @ui-scale), 100%);
  background: @surface;
  border: calc(1px * @ui-scale) solid @border;
  border-radius: calc(14px * @ui-scale);
  padding: @space-6;
  box-shadow: @shadow;
}

h1 {
  margin: 0;
  font-size: calc(30px * @ui-scale);
}

p {
  margin: calc(6px * @ui-scale) 0 @space-4;
  color: @text-muted;
}

.form {
  display: grid;
  gap: @space-3;
}
</style>




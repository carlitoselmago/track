<template>
  <ErrorBanner />
  <RouterView />
</template>

<script setup>
import { RouterView } from "vue-router";
import ErrorBanner from "./components/common/ErrorBanner.vue";
</script>


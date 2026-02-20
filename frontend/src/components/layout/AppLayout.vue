<template>
  <TopNav />
  <main class="page">
    <RouterView />
  </main>
</template>

<script setup>
import { RouterView } from "vue-router";
import TopNav from "./TopNav.vue";
</script>

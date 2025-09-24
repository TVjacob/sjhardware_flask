<!-- src/components/ReportCard.vue -->
<template>
    <RouterLink :to="link">
      <div class="bg-white p-4 rounded shadow hover:bg-blue-50 cursor-pointer transition">
        <h3 class="text-lg font-semibold">{{ title }}</h3>
      </div>
    </RouterLink>
  </template>
  
  <script setup>
  import { RouterLink } from 'vue-router';
  defineProps({
    title: String,
    link: String,
  });
  </script>
  
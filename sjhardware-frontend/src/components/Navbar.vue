<template>
    <div class="h-16 w-full bg-white shadow flex items-center justify-between px-6">
      <div class="font-bold text-lg">{{ pageTitle }}</div>
      <div class="flex items-center gap-4">
        <div class="text-gray-700">Jacob</div>
        <button class="bg-blue-500 text-white px-3 py-1 rounded">Profile</button>
      </div>
    </div>
  </template>
  
  <script>
  import { computed } from 'vue';
  import { useRoute } from 'vue-router';
  
  export default {
    setup() {
      const route = useRoute();
      const pageTitle = computed(() => {
        switch (route.path) {
          case '/': return 'Dashboard';
          case '/products': return 'Products';
          case '/sales': return 'Sales';
          case '/supplier': return 'Supplier';
          case '/purchases': return 'Purchases';
          case '/payments': return 'Payments';
          case '/expenses': return 'Expenses';
          default: return '';
        }
      });
  
      return { pageTitle };
    },
  };
  </script>
  
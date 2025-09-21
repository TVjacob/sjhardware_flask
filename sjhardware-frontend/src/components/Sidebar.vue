<template>
    <div :class="['h-screen bg-gray-800 text-white flex flex-col transition-all', collapsed ? 'w-20' : 'w-64']">
      <!-- Logo / Title -->
      <div class="p-6 font-bold text-xl border-b border-gray-700 flex justify-between items-center">
        <span v-if="!collapsed">SJ Hardware</span>
        <button @click="toggleSidebar" class="focus:outline-none">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>
  
      <!-- Menu -->
      <nav class="flex-1 mt-4">
        <ul>
          <li v-for="item in menuItems" :key="item.name">
            <router-link
              :to="item.path"
              class="flex items-center px-6 py-3 hover:bg-gray-700 rounded gap-2"
              :class="{ 'bg-gray-700': isActive(item.path) }"
            >
              <span>{{ collapsed ? item.icon : item.name }}</span>
            </router-link>
          </li>
        </ul>
      </nav>
  
      <!-- Logout -->
      <div class="p-6 border-t border-gray-700">
        <button class="w-full bg-red-500 hover:bg-red-600 px-4 py-2 rounded">
          Logout
        </button>
      </div>
    </div>
  </template>
  
  <script>
  import { useRoute } from 'vue-router';
  import { ref } from 'vue';
  
  export default {
    setup() {
      const route = useRoute();
      const collapsed = ref(false);
  
      const toggleSidebar = () => collapsed.value = !collapsed.value;
  
      const menuItems = [
        { name: 'Dashboard', path: '/', icon: '🏠' },
        { name: 'Products', path: '/products', icon: '📦' },
        { name: 'Customers', path: '/customers', icon: '🍮' },
        { name: 'Add Sales', path: '/sales', icon: '💰' },
        { name: 'Sales List', path: '/saleslist', icon: '🍮' },
        { name: 'Supplier', path: '/supplier', icon: '📉' },
        { name: 'Add Purchase', path: '/purchases', icon: '🛒' },
        { name: 'Purchase List', path: '/purchaselist', icon: '🍮' },
        { name: 'Payments', path: '/payments', icon: '💳' },
        { name: 'Expenses', path: '/expenses', icon: '📉' },
        { name: 'Users', path: '/users', icon: '🍮' },

        
      ];
  
      const isActive = (path) => route.path === path;
  
      return { menuItems, isActive, collapsed, toggleSidebar };
    },
  };
  </script>
  
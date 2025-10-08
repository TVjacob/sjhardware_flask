<template>
  <div class="relative">
    <!-- Overlay (visible only on mobile when sidebar is open) -->
    <div
      v-if="!collapsed && isMobile"
      class="fixed inset-0 bg-black bg-opacity-50 z-40"
      @click="toggleSidebar"
    ></div>

    <!-- Sidebar -->
    <div
      :class="[
        'fixed top-0 left-0 h-screen bg-gray-800 text-white flex flex-col transition-all duration-300 ease-in-out z-50',
        collapsed ? 'w-20' : 'w-64',
        isMobile ? (collapsed ? '-translate-x-full' : 'translate-x-0') : ''
      ]"
    >
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
      <nav class="flex-1 mt-4 overflow-y-auto">
        <ul>
          <li v-for="item in menuItems" :key="item.name">
            <router-link
              :to="item.path"
              class="flex items-center px-6 py-3 hover:bg-gray-700 rounded gap-3 transition-colors"
              :class="{ 'bg-gray-700': isActive(item.path) }"
              @click="isMobile ? toggleSidebar() : null"
            >
              <span class="text-xl">{{ item.icon }}</span>
              <span v-if="!collapsed" class="whitespace-nowrap">{{ item.name }}</span>
            </router-link>
          </li>
        </ul>
      </nav>

      <!-- Logout -->
      <div class="p-6 border-t border-gray-700">
        <button
          @click="logout"
          class="w-full bg-red-500 hover:bg-red-600 px-4 py-2 rounded text-sm md:text-base"
        >
          Logout
        </button>
      </div>
    </div>

    <!-- Mobile Toggle Button (visible only on small screens) -->
    <button
      v-if="isMobile"
      @click="toggleSidebar"
      class="fixed top-4 left-4 z-50 bg-gray-800 text-white p-2 rounded-lg shadow-md focus:outline-none"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>
  </div>
</template>

<script>
import { useRoute, useRouter } from 'vue-router';
import { ref, onMounted, onBeforeUnmount } from 'vue';
import api from '../api';

export default {
  setup() {
    const route = useRoute();
    const router = useRouter();
    const collapsed = ref(false);
    const isMobile = ref(false);

    const toggleSidebar = () => (collapsed.value = !collapsed.value);
    const isActive = (path) => route.path === path;

    const handleResize = () => {
      isMobile.value = window.innerWidth < 768;
      if (isMobile.value) collapsed.value = true;
    };

    onMounted(() => {
      handleResize();
      window.addEventListener('resize', handleResize);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize);
    });

    const logout = () => {
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      if (api.defaults.headers.common['Authorization']) {
        delete api.defaults.headers.common['Authorization'];
      }
      router.push('/login');
    };

    const menuItems = [
      { name: 'Dashboard', path: '/', icon: '🏠' },
      { name: 'Products', path: '/products', icon: '📦' },
      { name: 'Customers', path: '/customers', icon: '👥' },
      { name: 'Add Sales', path: '/sales', icon: '💰' },
      { name: 'Sales List', path: '/saleslist', icon: '📃' },
      { name: 'Supplier', path: '/supplier', icon: '🚚' },
      { name: 'Add Purchase', path: '/purchases', icon: '🛒' },
      { name: 'Purchase List', path: '/purchaselist', icon: '📋' },
      { name: 'Expenses', path: '/expenses', icon: '💸' },
      { name: 'Reports', path: '/reports', icon: '📊' },
      { name: 'Users', path: '/users', icon: '👤' },
    ];

    return { menuItems, collapsed, isActive, toggleSidebar, logout, isMobile };
  },
};
</script>

<style scoped>
/* Smooth transition */
.transition-all {
  transition: all 0.3s ease-in-out;
}

/* Scrollbar styling for long menus */
nav::-webkit-scrollbar {
  width: 6px;
}
nav::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}
</style>

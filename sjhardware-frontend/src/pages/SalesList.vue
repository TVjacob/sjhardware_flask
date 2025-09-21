<template>
    <div class="p-6 max-w-7xl mx-auto">
      <h1 class="text-2xl font-bold mb-4">Sales List</h1>
  
      <!-- Tabs -->
      <div class="flex space-x-4 mb-6">
        <button
          :class="currentTab === 'paid' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'"
          class="px-4 py-2 rounded"
          @click="currentTab = 'paid'"
        >
          Paid Sales
        </button>
        <button
          :class="currentTab === 'unpaid' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'"
          class="px-4 py-2 rounded"
          @click="currentTab = 'unpaid'"
        >
          Unpaid Sales
        </button>
      </div>
  
      <!-- Table -->
      <table class="min-w-full border">
        <thead>
          <tr class="bg-gray-100">
            <th class="p-2 border">Sale ID</th>
            <th class="p-2 border">Sale Number</th>
            <th class="p-2 border">Sale Date</th>
            <th class="p-2 border">Total Amount</th>
            <th class="p-2 border">Paid</th>
            <th class="p-2 border">Balance</th>
            <th class="p-2 border">Payment Status</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="sale in filteredSales"
            :key="sale.sale_id"
            class="hover:bg-gray-50 cursor-pointer"
          >
            <td class="p-2 border">{{ sale.sale_id }}</td>
            <td class="p-2 border">{{ sale.sale_number }}</td>
            <td class="p-2 border">{{ formatDate(sale.sale_date) }}</td>
            <td class="p-2 border">{{ sale.total_amount.toFixed(2) }}</td>
            <td class="p-2 border">{{ (sale.total_amount - sale.balance).toFixed(2) }}</td>
            <td class="p-2 border">{{ sale.balance.toFixed(2) }}</td>
            <td class="p-2 border">
              <span
                :class="sale.balance <= 0 ? 'text-green-600 font-bold' : 'text-red-600 font-bold'"
              >
                {{ sale.balance <= 0 ? 'Paid' : 'Unpaid' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  import api from '../api'; // Axios instance
  
  const currentTab = ref('unpaid'); // default tab
  const sales = ref([]);
  
  // Fetch sales from API
  const fetchSales = async () => {
    try {
      const res = await api.get('/sales/');
      // Compute balance for each sale
      sales.value = res.data.map(s => ({
        ...s,
        balance: s.total_amount - (s.total_paid || 0) // compute balance
      }));
    } catch (err) {
      console.error('Error fetching sales', err);
    }
  };
  
  // Filter sales based on tab
  const filteredSales = computed(() => {
    if (currentTab.value === 'paid') {
      return sales.value.filter(s => s.balance <= 0);
    } else {
      return sales.value.filter(s => s.balance > 0);
    }
  });
  
  // Format date nicely
  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString();
  };
  
  onMounted(() => {
    fetchSales();
  });
  </script>
  
  <style scoped>
  table th,
  table td {
    text-align: left;
  }
  </style>
  
<template>
    <div class="p-6 max-w-7xl mx-auto">
      <h1 class="text-2xl font-bold mb-4">Purchase Orders</h1>
  
      <!-- Tabs -->
      <div class="flex space-x-4 mb-6">
        <button
          :class="currentTab === 'paid' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'"
          class="px-4 py-2 rounded"
          @click="currentTab = 'paid'"
        >
          Paid Invoices
        </button>
        <button
          :class="currentTab === 'unpaid' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'"
          class="px-4 py-2 rounded"
          @click="currentTab = 'unpaid'"
        >
          Unpaid Invoices
        </button>
      </div>
  
      <!-- Table -->
      <table class="min-w-full border">
        <thead>
          <tr class="bg-gray-100">
            <th class="p-2 border">PO ID</th>
            <th class="p-2 border">Supplier</th>
            <th class="p-2 border">Invoice Number</th>
            <th class="p-2 border">Purchase Date</th>
            <th class="p-2 border">Total Amount</th>
            <th class="p-2 border">Paid</th>
            <th class="p-2 border">Balance</th>
            <th class="p-2 border">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="po in filteredPurchaseOrders"
            :key="po.id"
            class="hover:bg-gray-50 cursor-pointer"
          >
            <td class="p-2 border">{{ po.id }}</td>
            <td class="p-2 border">{{ po.supplier_name }}</td>
            <td class="p-2 border">{{ po.invoice_number }}</td>
            <td class="p-2 border">{{ formatDate(po.purchase_date) }}</td>
            <td class="p-2 border">{{ po.total_amount.toFixed(2) }}</td>
            <td class="p-2 border">{{ po.total_paid.toFixed(2) }}</td>
            <td class="p-2 border">{{ po.total_balance.toFixed(2) }}</td>
            <td class="p-2 border">
              <span
                :class="po.total_balance === 0 ? 'text-green-600 font-bold' : 'text-red-600 font-bold'"
              >
                {{ po.total_balance === 0 ? 'Paid' : 'Unpaid' }}
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
  const purchaseOrders = ref([]);
  
  // Fetch purchase orders from API
  const fetchPurchaseOrders = async () => {
    try {
      const res = await api.get('/suppliers/orders');
      purchaseOrders.value = res.data;
    } catch (err) {
      console.error('Error fetching purchase orders', err);
    }
  };
  
  // Filter purchase orders based on tab
  const filteredPurchaseOrders = computed(() => {
    if (currentTab.value === 'paid') {
      return purchaseOrders.value.filter(po => po.total_balance === 0);
    } else {
      return purchaseOrders.value.filter(po => po.total_balance > 0);
    }
  });
  
  // Format date nicely
  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString();
  };
  
  onMounted(() => {
    fetchPurchaseOrders();
  });
  </script>
  
  <style scoped>
  table th,
  table td {
    text-align: left;
  }
  </style>
  
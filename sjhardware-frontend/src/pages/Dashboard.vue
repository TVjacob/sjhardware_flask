<template>
  <div class="p-6 space-y-8 bg-gray-50 dark:bg-gray-950 min-h-screen">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 mb-6">
      <h1 class="text-3xl font-bold  tracking-tight">
        Dashboard Overview
      </h1>
      <button
        @click="fetchDashboard"
        :disabled="loading"
        class="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-lg shadow-md transition transform hover:scale-105 flex items-center gap-2 font-medium disabled:opacity-50"
      >
        <svg v-if="loading" class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span v-else>Refresh</span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-32">
      <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-indigo-500"></div>
      <span class="ml-4 text-xl text-gray-600 dark:text-gray-400">Loading dashboard data...</span>
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="error" class="text-center py-20 text-red-600 dark:text-red-400">
      <p class="text-xl font-semibold">Failed to load dashboard</p>
      <p class="mt-2">{{ error }}</p>
      <button @click="fetchDashboard" class="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
        Try Again
      </button>
    </div>

    <div v-else class="space-y-10">
      <!-- Primary Metrics -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6">
        <div
          v-for="card in primaryMetrics"
          :key="card.title"
          class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6 hover:shadow-xl transition-all duration-300"
        >
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium ">{{ card.title }}</p>
              <p class="text-3xl font-bold  mt-2">
                {{ card.value }}
              </p>
            </div>
            <div :class="card.iconClass" class="text-4xl opacity-80">
              {{ card.icon }}
            </div>
          </div>
          <p class="text-xs text-gray-400 dark:text-gray-500 mt-2">{{ card.subtitle }}</p>
        </div>
      </div>

      <!-- Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-bold  mb-4 flex items-center gap-2">
            <span>📈</span> Sales Last 7 Days
          </h2>
          <LineChart :chartData="salesChartData" />
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-bold  mb-4 flex items-center gap-2">
            <span>📉</span> Expenses Last 7 Days
          </h2>
          <LineChart :chartData="expensesChartData" />
        </div>
      </div>

      <!-- Best / Least Products -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-bold  mb-4">Top 5 Best Performing Products</h2>
          <ProductList :products="bestProducts" type="best" />
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-bold  mb-4">Top 5 Least Performing Products</h2>
          <ProductList :products="leastProducts" type="least" />
        </div>
      </div>

      <!-- Liabilities / Payables -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6">
          <h3 class="text-lg font-semibold  mb-2">Outstanding Sales</h3>
          <p class="text-3xl font-bold text-red-600 dark:text-red-400">
            UGX {{ formatNumber(outstandingSales) }}
          </p>
          <p class="text-sm  mt-1">Pending receivables</p>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6">
          <h3 class="text-lg font-semibold  mb-2">Outstanding POs</h3>
          <p class="text-3xl font-bold text-amber-600 dark:text-amber-400">
            UGX {{ formatNumber(outstandingPO) }}
          </p>
          <p class="text-sm  mt-1">Pending supplier payments</p>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6">
          <h3 class="text-lg font-semibold  mb-2">Total Purchase Orders</h3>
          <p class="text-3xl font-bold text-indigo-600 dark:text-indigo-400">
            {{ totalPurchaseOrders }}
          </p>
          <p class="text-sm  mt-1">All active POs</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import LineChart from '../components/LineChart.vue'
import api from '../api'

// Data
const loading = ref(false)
const error = ref(null)

const totalProducts = ref(0)
const totalSales = ref(0)
const totalExpenses = ref(0)
const totalCustomers = ref(0)
const totalSuppliers = ref(0)
const totalPurchaseOrders = ref(0)
const outstandingSales = ref(0)
const outstandingPO = ref(0)

const salesChartData = ref({ labels: [], datasets: [] })
const expensesChartData = ref({ labels: [], datasets: [] })

const bestProducts = ref([])
const leastProducts = ref([])

// Computed Metrics Cards
const primaryMetrics = computed(() => [
  { title: 'Products', value: totalProducts.value, subtitle: 'Active in inventory', icon: '📦', iconClass: 'text-indigo-500' },
  { title: 'Customers', value: totalCustomers.value, subtitle: 'Registered customers', icon: '👥', iconClass: 'text-cyan-500' },
  { title: 'Suppliers', value: totalSuppliers.value, subtitle: 'Active suppliers', icon: '🏪', iconClass: 'text-teal-500' },
  { title: 'Sales', value: `UGX ${formatNumber(totalSales.value)}`, subtitle: 'Total revenue', icon: '💰', iconClass: 'text-green-500' },
  { title: 'Expenses', value: `UGX ${formatNumber(totalExpenses.value)}`, subtitle: 'Total costs', icon: '📉', iconClass: 'text-red-500' },
  { title: 'Purchase Orders', value: totalPurchaseOrders.value, subtitle: 'All active POs', icon: '📋', iconClass: 'text-purple-500' },
  { title: 'Outstanding Sales', value: `UGX ${formatNumber(outstandingSales.value)}`, subtitle: 'Receivables', icon: '⏳', iconClass: 'text-amber-500' },
  { title: 'Outstanding POs', value: `UGX ${formatNumber(outstandingPO.value)}`, subtitle: 'Payables', icon: '⚠️', iconClass: 'text-orange-500' },
])

// Formatter
const formatNumber = (num) => Number(num || 0).toLocaleString('en-UG', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 0
})

// Fetch
async function fetchDashboard() {
  loading.value = true
  error.value = null

  try {
    const res = await api.get('/dashboard/metrics')
    const data = res.data

    totalProducts.value = data.totalProducts || 0
    totalSales.value = data.totalSales || 0
    totalExpenses.value = data.totalExpenses || 0
    totalCustomers.value = data.totalCustomers || 0
    totalSuppliers.value = data.totalSuppliers || 0
    totalPurchaseOrders.value = data.totalPurchaseOrders || 0
    outstandingSales.value = data.outstandingSales || 0
    outstandingPO.value = data.outstandingPO || 0

    salesChartData.value = {
      labels: data.salesLast7Days?.map(d => d.day) || [],
      datasets: [{
        label: 'Sales (UGX)',
        data: data.salesLast7Days?.map(d => d.amount) || [],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        tension: 0.3,
        fill: true
      }]
    }

    expensesChartData.value = {
      labels: data.expensesLast7Days?.map(d => d.day) || [],
      datasets: [{
        label: 'Expenses (UGX)',
        data: data.expensesLast7Days?.map(d => d.amount) || [],
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.2)',
        tension: 0.3,
        fill: true
      }]
    }

    bestProducts.value = data.bestPerformingProducts || []
    leastProducts.value = data.leastPerformingProducts || []

  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load dashboard data'
    console.error('Dashboard error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchDashboard)
</script>

<style scoped>
/* Card hover */
.hover\:shadow-xl:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
</style>

<template>
  <div class="p-6 space-y-8 bg-gray-50 dark:bg-gray-950 min-h-screen">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 mb-6">
      <h1 class="text-3xl font-bold tracking-tight">Dashboard Overview</h1>
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

    <!-- Error -->
    <div v-else-if="error" class="text-center py-20 text-red-600 dark:text-red-400">
      <p class="text-xl font-semibold">Failed to load dashboard</p>
      <p class="mt-2">{{ error }}</p>
      <button @click="fetchDashboard" class="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
        Try Again
      </button>
    </div>

    <div v-else class="space-y-10">
      <!-- Primary Metrics - Permission Controlled -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6">

        <div v-if="canView('view_inventory')" class="metric-card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Products</p>
              <p class="text-3xl font-bold mt-2">{{ totalProducts }}</p>
            </div>
            <span class="text-4xl">📦</span>
          </div>
          <p class="text-xs text-gray-400 mt-2">Active in inventory</p>
        </div>

        <div v-if="canView('view_customers')" class="metric-card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Customers</p>
              <p class="text-3xl font-bold mt-2">{{ totalCustomers }}</p>
            </div>
            <span class="text-4xl">👥</span>
          </div>
          <p class="text-xs text-gray-400 mt-2">Registered customers</p>
        </div>

        <div v-if="canView('view_suppliers')" class="metric-card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Suppliers</p>
              <p class="text-3xl font-bold mt-2">{{ totalSuppliers }}</p>
            </div>
            <span class="text-4xl">🏪</span>
          </div>
          <p class="text-xs text-gray-400 mt-2">Active suppliers</p>
        </div>

        <div v-if="canView('view_sales')" class="metric-card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Sales</p>
              <p class="text-3xl font-bold mt-2 text-green-600">UGX {{ formatNumber(totalSales) }}</p>
            </div>
            <span class="text-4xl">💰</span>
          </div>
          <p class="text-xs text-gray-400 mt-2">Total revenue</p>
        </div>

        <div v-if="canView('view_invoices')" class="metric-card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Outstanding Sales</p>
              <p class="text-3xl font-bold mt-2 text-red-600">UGX {{ formatNumber(outstandingSales) }}</p>
            </div>
            <span class="text-4xl">⏳</span>
          </div>
          <p class="text-xs text-gray-400 mt-2">Pending receivables</p>
        </div>

        <div v-if="canView('view_purchases')" class="metric-card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Purchase Orders</p>
              <p class="text-3xl font-bold mt-2">{{ totalPurchaseOrders }}</p>
            </div>
            <span class="text-4xl">📋</span>
          </div>
          <p class="text-xs text-gray-400 mt-2">All active POs</p>
        </div>
      </div>

      <!-- Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div v-if="canView('view_sales')" class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-bold mb-4 flex items-center gap-2">📈 Sales Last 7 Days</h2>
          <LineChart :chartData="salesChartData" />
        </div>

        <div v-if="canView('view_expenses')" class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-bold mb-4 flex items-center gap-2">📉 Expenses Last 7 Days</h2>
          <LineChart :chartData="expensesChartData" />
        </div>
      </div>

      <!-- Best / Least Products (Inline - No external component) -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Best Products -->
        <div v-if="canView('view_reports')" class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-bold mb-4">Top 5 Best Performing Products</h2>
          <div class="space-y-3">
            <div v-for="(product, i) in bestProducts" :key="i"
                 class="flex justify-between items-center bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
              <div>
                <span class="font-medium">{{ product.name }}</span>
                <span class="text-xs text-gray-500 ml-2">({{ product.category }})</span>
              </div>
              <div class="text-right">
                <span class="font-bold text-green-600">UGX {{ formatNumber(product.profit) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Least Products -->
        <div v-if="canView('view_reports')" class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-bold mb-4">Top 5 Least Performing Products</h2>
          <div class="space-y-3">
            <div v-for="(product, i) in leastProducts" :key="i"
                 class="flex justify-between items-center bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
              <div>
                <span class="font-medium">{{ product.name }}</span>
                <span class="text-xs text-gray-500 ml-2">({{ product.category }})</span>
              </div>
              <div class="text-right">
                <span class="font-bold text-red-600">UGX {{ formatNumber(product.profit) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Liabilities / Payables -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div v-if="canView('view_invoices')" class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6">
          <h3 class="text-lg font-semibold mb-2">Outstanding Sales</h3>
          <p class="text-3xl font-bold text-red-600 dark:text-red-400">UGX {{ formatNumber(outstandingSales) }}</p>
          <p class="text-sm text-gray-500 mt-1">Pending receivables</p>
        </div>

        <div v-if="canView('view_purchases')" class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6">
          <h3 class="text-lg font-semibold mb-2">Outstanding POs</h3>
          <p class="text-3xl font-bold text-amber-600 dark:text-amber-400">UGX {{ formatNumber(outstandingPO) }}</p>
          <p class="text-sm text-gray-500 mt-1">Pending supplier payments</p>
        </div>

        <div v-if="canView('view_purchases')" class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6">
          <h3 class="text-lg font-semibold mb-2">Total Purchase Orders</h3>
          <p class="text-3xl font-bold text-indigo-600 dark:text-indigo-400">{{ totalPurchaseOrders }}</p>
          <p class="text-sm text-gray-500 mt-1">All active POs</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import LineChart from '../components/LineChart.vue'
import api from '../api'

// ============== PERMISSION SYSTEM ==============
const user = computed(() => JSON.parse(localStorage.getItem('user')) || { permissions: [] })
const canView = (perm) => user.value.permissions.includes(perm)

// ============== DATA ==============
const loading = ref(false)
const error = ref(null)

const totalProducts = ref(0)
const totalSales = ref(0)
const totalCustomers = ref(0)
const totalSuppliers = ref(0)
const totalPurchaseOrders = ref(0)
const outstandingSales = ref(0)
const outstandingPO = ref(0)

const salesChartData = ref({ labels: [], datasets: [] })
const expensesChartData = ref({ labels: [], datasets: [] })

const bestProducts = ref([])
const leastProducts = ref([])

// Formatter
const formatNumber = (num) => Number(num || 0).toLocaleString('en-UG')

async function fetchDashboard() {
  loading.value = true
  error.value = null

  try {
    const res = await api.get('/dashboard/metrics')
    const data = res.data

    totalProducts.value = data.totalProducts || 0
    totalSales.value = data.totalSales || 0
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
.metric-card {
  @apply bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6 hover:shadow-xl transition-all duration-300;
}
</style>

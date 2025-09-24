<template>
  <div>
    <!-- Metrics Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white p-6 rounded shadow flex flex-col items-center">
        <div class="text-gray-500">Total Products</div>
        <div class="text-3xl font-bold">{{ totalProducts }}</div>
      </div>

      <div class="bg-white p-6 rounded shadow flex flex-col items-center">
        <div class="text-gray-500">Total Sales</div>
        <div class="text-3xl font-bold">UGX {{ totalSales.toLocaleString() }}</div>
      </div>

      <div class="bg-white p-6 rounded shadow flex flex-col items-center">
        <div class="text-gray-500">Total Expenses</div>
        <div class="text-3xl font-bold">UGX {{ totalExpenses.toLocaleString() }}</div>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
      <div class="bg-white p-6 rounded shadow">
        <h2 class="text-xl font-bold mb-4">Sales Last 7 Days</h2>
        <LineChart :chartData="salesChartData" />
      </div>

      <div class="bg-white p-6 rounded shadow">
        <h2 class="text-xl font-bold mb-4">Expenses Last 7 Days</h2>
        <LineChart :chartData="expensesChartData" />
      </div>
    </div>

    <!-- Best / Least Performing Products -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
      <div class="bg-white p-6 rounded shadow">
        <h2 class="text-xl font-bold mb-4">Best Performing Products (Revenue)</h2>
        <ul>
          <li v-for="product in bestProducts" :key="product.product_id">
            {{ product.product_name }} - UGX {{ product.total_revenue.toLocaleString() }}
          </li>
        </ul>
      </div>

      <div class="bg-white p-6 rounded shadow">
        <h2 class="text-xl font-bold mb-4">Least Performing Products (Revenue)</h2>
        <ul>
          <li v-for="product in leastProducts" :key="product.product_id">
            {{ product.product_name }} - UGX {{ product.total_revenue.toLocaleString() }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import LineChart from '../components/LineChart.vue';
import api from '../api';

export default {
  components: { LineChart },
  data() {
    return {
      totalProducts: 0,
      totalSales: 0,
      totalExpenses: 0,
      salesChartData: { labels: [], datasets: [] },
      expensesChartData: { labels: [], datasets: [] },
      bestProducts: [],
      leastProducts: [],
    };
  },
  methods: {
    async fetchMetrics() {
      try {
        const res = await api.get('/dashboard/metrics');
        const data = res.data;

        // Set total metrics
        this.totalProducts = data.totalProducts;
        this.totalSales = data.totalSales;
        this.totalExpenses = data.totalExpenses;

        // Prepare chart data
        this.salesChartData = {
          labels: data.salesLast7Days.map(d => d.day),
          datasets: [
            {
              label: 'Sales',
              data: data.salesLast7Days.map(d => d.amount),
              borderColor: '#3b82f6',
              backgroundColor: 'rgba(59, 130, 246, 0.2)',
            },
          ],
        };

        this.expensesChartData = {
          labels: data.expensesLast7Days.map(d => d.day),
          datasets: [
            {
              label: 'Expenses',
              data: data.expensesLast7Days.map(d => d.amount),
              borderColor: '#ef4444',
              backgroundColor: 'rgba(239, 68, 68, 0.2)',
            },
          ],
        };

        // Best / least performing products
        this.bestProducts = data.bestPerformingProducts || [];
        this.leastProducts = data.leastPerformingProducts || [];
      } catch (err) {
        console.error('Error fetching dashboard metrics:', err);
      }
    },
  },
  mounted() {
    this.fetchMetrics();
  },
};
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <div class="bg-white p-6 rounded shadow flex flex-col items-center">
      <div class="text-gray-500">Total Products</div>
      <div class="text-3xl font-bold">{{ totalProducts }}</div>
    </div>

    <div class="bg-white p-6 rounded shadow flex flex-col items-center">
      <div class="text-gray-500">Total Sales</div>
      <div class="text-3xl font-bold">${{ totalSales }}</div>
    </div>

    <div class="bg-white p-6 rounded shadow flex flex-col items-center">
      <div class="text-gray-500">Total Expenses</div>
      <div class="text-3xl font-bold">${{ totalExpenses }}</div>
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
</template>

<script>
import LineChart from '../components/LineChart.vue';

export default {
  components: { LineChart },
  data() {
    return {
      // Fixed data
      totalProducts: 120,
      totalSales: 3500,
      totalExpenses: 1450,

      salesChartData: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [
          { 
            label: 'Sales', 
            data: [500, 600, 450, 700, 550, 800, 900], 
            borderColor: '#3b82f6', 
            backgroundColor: 'rgba(59, 130, 246, 0.2)' 
          },
        ],
      },

      expensesChartData: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [
          { 
            label: 'Expenses', 
            data: [200, 250, 180, 300, 220, 350, 400], 
            borderColor: '#ef4444', 
            backgroundColor: 'rgba(239, 68, 68, 0.2)' 
          },
        ],
      },
    };
  },
};
</script>

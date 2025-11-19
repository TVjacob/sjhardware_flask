<template>
  <div class="p-6 max-w-7xl mx-auto">
    <h1 class="text-3xl font-bold mb-6 text-gray-800 animate-fadeIn">
      Sales Profit Report
    </h1>

    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg shadow mb-4 flex flex-col md:flex-row gap-4">
      <input
        v-model="search"
        @input="fetchData"
        placeholder="Search by product or invoice..."
        class="border p-2 rounded w-full md:w-1/3"
      />

      <input
        type="date"
        v-model="startDate"
        @change="fetchData"
        class="border p-2 rounded"
      />

      <input
        type="date"
        v-model="endDate"
        @change="fetchData"
        class="border p-2 rounded"
      />
    </div>

    <!-- Totals Summary -->
    <div class="grid md:grid-cols-3 gap-4 mb-6">
      <div class="p-4 rounded-lg shadow bg-white text-center">
        <h3 class="text-lg font-semibold text-gray-600">Total Sales</h3>
        <p class="text-2xl font-bold text-blue-600">
          {{ formatNumber(totals.sales) }}
        </p>
      </div>

      <div class="p-4 rounded-lg shadow bg-white text-center">
        <h3 class="text-lg font-semibold text-gray-600">Total Cost</h3>
        <p class="text-2xl font-bold text-red-600">
          {{ formatNumber(totals.cost) }}
        </p>
      </div>

      <div class="p-4 rounded-lg shadow bg-white text-center">
        <h3 class="text-lg font-semibold text-gray-600">Total Profit</h3>
        <p
          class="text-2xl font-bold"
          :class="totals.profit >= 0 ? 'text-green-600' : 'text-red-600'"
        >
          {{ formatNumber(totals.profit) }}
        </p>
      </div>
    </div>

    <!-- OPTIONAL Cash vs Credit Summary -->
    <div v-if="totals.cash !== undefined || totals.credit !== undefined"
         class="grid md:grid-cols-2 gap-4 mb-6">
      <div class="p-4 rounded-lg shadow bg-white text-center">
        <h3 class="text-lg font-semibold text-gray-600">Total Cash Sales</h3>
        <p class="text-2xl font-bold text-green-700">
          {{ totals.cash !== undefined ? formatNumber(totals.cash) : 'N/A' }}
        </p>
      </div>

      <div class="p-4 rounded-lg shadow bg-white text-center">
        <h3 class="text-lg font-semibold text-gray-600">Total Credit Sales</h3>
        <p class="text-2xl font-bold text-yellow-700">
          {{ totals.credit !== undefined ? formatNumber(totals.credit) : 'N/A' }}
        </p>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto border rounded-lg shadow bg-white">
      <table class="min-w-full border-collapse">
        <thead class="bg-gray-100 text-sm">
          <tr>
            <th class="p-3 border-b">Invoice</th>
            <th class="p-3 border-b text-left">Product</th>
            <th class="p-3 border-b text-left">Category</th>
            <th class="p-3 border-b text-left">Date</th>
            <th class="p-3 border-b text-right">Qty</th>
            <th class="p-3 border-b text-right">Sell Price</th>
            <th class="p-3 border-b text-right">Buy Price</th>
            <th class="p-3 border-b text-right">Sales</th>
            <th class="p-3 border-b text-right">Cost</th>
            <th class="p-3 border-b text-right">Profit</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in reportData"
            :key="row.sale_id"
            class="hover:bg-gray-50 transition"
          >
            <td class="p-3 border">{{ row.invoice_number }}</td>
            <td class="p-3 border">{{ row.product }}</td>
            <td class="p-3 border">{{ row.category }}</td>
            <td class="p-3 border">{{ formatDate(row.sale_date) }}</td>
            <td class="p-3 border text-right">{{ row.qty }}</td>
            <td class="p-3 border text-right">{{ formatNumber(row.selling_price) }}</td>
            <td class="p-3 border text-right">{{ formatNumber(row.purchase_price) }}</td>
            <td class="p-3 border text-right">{{ formatNumber(row.total_sales) }}</td>
            <td class="p-3 border text-right">{{ formatNumber(row.total_cost) }}</td>
            <td
              class="p-3 border text-right font-bold"
              :class="row.profit >= 0 ? 'text-green-600' : 'text-red-600'"
            >
              {{ formatNumber(row.profit) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div
      v-if="totalRecords > perPage"
      class="flex justify-between items-center mt-4 p-3 bg-white rounded shadow"
    >
      <button
        @click="prevPage"
        :disabled="page === 1"
        class="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50"
      >
        Prev
      </button>

      <span class="font-semibold">
        Page {{ page }}
      </span>

      <button
        @click="nextPage"
        :disabled="page >= Math.ceil(totalRecords / perPage)"
        class="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";

const reportData = ref([]);
const totals = ref({});
const page = ref(1);
const perPage = 100;
const totalRecords = ref(0);

const search = ref("");
const startDate = ref("");
const endDate = ref("");

const fetchData = async () => {
  try {
    const res = await api.get("/reports/sales-profit", {
      params: {
        page: page.value,
        search: search.value,
        start_date: startDate.value,
        end_date: endDate.value,
      },
    });

    reportData.value = res.data.data;
    totalRecords.value = res.data.total_records;
    totals.value = res.data.totals || {};

  } catch (err) {
    console.error(err);
  }
};

const nextPage = () => {
  page.value++;
  fetchData();
};

const prevPage = () => {
  page.value = Math.max(1, page.value - 1);
  fetchData();
};

const formatNumber = (num) =>
  Number(num || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

const formatDate = (d) => new Date(d).toLocaleDateString();

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
@keyframes fadeIn {
  0% { opacity: 0; transform: translateY(-10px);}
  100% { opacity: 1; transform: translateY(0);}
}
.animate-fadeIn {
  animation: fadeIn 0.4s ease-in-out forwards;
}
</style>

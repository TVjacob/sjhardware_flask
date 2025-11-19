<template>
  <div class="p-6 max-w-7xl mx-auto">
    <h1 class="text-3xl font-bold mb-6 text-gray-800 animate-fadeIn">
      Purchased Products Report
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

    <!-- Export Buttons -->
    <div class="flex space-x-2 mb-4">
      <button
        @click="exportCSV"
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded shadow transition transform hover:scale-105"
      >
        Export CSV
      </button>
      <button
        @click="exportPDF"
        class="px-4 py-2 bg-gray-700 hover:bg-gray-800 text-white rounded shadow transition transform hover:scale-105"
      >
        Export PDF
      </button>
    </div>
  <!-- Summary
  <div
      class="bg-white rounded-lg shadow mt-6 p-5 grid md:grid-cols-2 gap-4 border border-gray-200"
      v-if="totals"
    >
      <div class="p-4 rounded-lg bg-indigo-50 text-center">
        <p class="text-sm text-gray-600">Total Quantity Purchased</p>
        <h2 class="text-3xl font-bold text-indigo-700">
          {{ formatNumber(totals.total_quantity) }}
        </h2>
      </div>

      <div class="p-4 rounded-lg bg-green-50 text-center">
        <p class="text-sm text-gray-600">Total Amount Spent</p>
        <h2 class="text-3xl font-bold text-green-700">
          {{ formatCurrency(totals.total_amount) }}
        </h2>
      </div>
    </div>  -->
     <!-- Summary -->
    <div
      class="bg-white rounded-lg shadow mt-6 p-5 grid md:grid-cols-2 gap-4 border border-gray-200"
      v-if="totals"
    >
      <div class="p-4 rounded-lg bg-indigo-50 text-center">
        <p class="text-sm text-gray-600">Total Quantity Purchased</p>
        <h2 class="text-3xl font-bold text-indigo-700">
          {{ formatNumber(totals.total_quantity) }}
        </h2>
      </div>

      <div class="p-4 rounded-lg bg-green-50 text-center">
        <p class="text-sm text-gray-600">Total Amount Spent</p>
        <h2 class="text-3xl font-bold text-green-700">
          {{ formatCurrency(totals.total_amount) }}
        </h2>
      </div>
    </div>
    <!-- Table -->
    <div class="overflow-x-auto border rounded-lg shadow bg-white">
      <table class="min-w-full border-collapse">
        <thead class="bg-gray-100 text-sm">
          <tr>
            <th class="p-3 border-b text-left">PO ID</th>
            <th class="p-3 border-b text-left">Product</th>
            <th class="p-3 border-b text-left">Category</th>
            <th class="p-3 border-b text-left">Supplier</th>
            <th class="p-3 border-b text-left">Invoice</th>
            <th class="p-3 border-b text-left">Date</th>
            <th class="p-3 border-b text-right">Qty</th>
            <th class="p-3 border-b text-right">Unit Price</th>
            <th class="p-3 border-b text-right">Total</th>
            <th class="p-3 border-b text-center w-[150px]">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in reportData"
            :key="row.purchase_id"
            class="hover:bg-gray-50 transition"
          >
            <td class="p-3 border">{{ row.purchase_id }}</td>
            <td class="p-3 border">{{ row.product }}</td>
            <td class="p-3 border">{{ row.category }}</td>
            <td class="p-3 border">{{ row.supplier }}</td>
            <td class="p-3 border">{{ row.invoice_number }}</td>
            <td class="p-3 border">{{ formatDate(row.purchase_date) }}</td>
            <td class="p-3 border text-right">{{ formatNumber(row.qty) }}</td>
            <td class="p-3 border text-right">{{ formatCurrency(row.unit_price) }}</td>
            <td class="p-3 border text-right">{{ formatCurrency(row.total_price) }}</td>

            <td class="p-3 border text-center">
              <div class="flex gap-2 justify-center">

                <!-- View -->
                <router-link
                  :to="`/purchase-orders/${row.purchase_id}`"
                  class="action-btn bg-blue-500 hover:bg-blue-600"
                  title="View"
                >
                  🔍
                </router-link>

                <!-- Edit -->
                <router-link
                  :to="`/purchase-orders/${row.purchase_id}/edit`"
                  class="action-btn bg-yellow-500 hover:bg-yellow-600"
                  title="Edit"
                >
                  ✏️
                </router-link>

              </div>
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
const totals = ref(null);

const page = ref(1);
const perPage = ref(100);
const totalRecords = ref(0);

const search = ref("");
const startDate = ref("");
const endDate = ref("");

const fetchData = async () => {
  try {
    const res = await api.get("/reports/purchased-product", {
      params: {
        page: page.value,
        search: search.value,
        start_date: startDate.value,
        end_date: endDate.value
      }
    });

    reportData.value = res.data.data;
    totalRecords.value = res.data.total_records;
    totals.value = res.data.totals;

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

const formatDate = d => new Date(d).toLocaleDateString();

const formatNumber = num => {
  if (num == null) return "0";
  return Number(num).toLocaleString();
};

const formatCurrency = num => {
  if (num == null) return "0.00";
  return Number(num).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const exportCSV = () => alert("CSV export coming soon.");
const exportPDF = () => alert("PDF export coming soon.");

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
/* Header animation */
@keyframes fadeIn {
  0% { opacity: 0; transform: translateY(-10px);}
  100% { opacity: 1; transform: translateY(0);}
}
.animate-fadeIn {
  animation: fadeIn 0.4s ease-in-out forwards;
}

/* Unified button design */
.action-btn {
  width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  color: white;
  font-size: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  transition: all 0.2s ease-in-out;
}
.action-btn:hover {
  transform: scale(1.08);
}

/* Smooth hover for table */
tbody tr:hover {
  background-color: #f9fafb;
}
</style>

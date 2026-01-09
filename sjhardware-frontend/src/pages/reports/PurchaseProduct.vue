<template>
  <div class="p-6 max-w-7xl mx-auto space-y-6">

    <!-- Page Title -->
    <h1 class="text-3xl font-bold text-gray-800 animate-fadeIn">
      Purchased Products Report
    </h1>

    <!-- Filters -->
    <div class="bg-white p-4 rounded-xl shadow flex flex-col md:flex-row gap-4 items-end">
      <div class="w-full md:w-1/3">
        <label class="text-sm font-medium text-gray-600">Search</label>
        <input
          v-model="search"
          placeholder="Search by product, invoice, supplier..."
          class="input-field"
        />
      </div>

      <div>
        <label class="text-sm font-medium text-gray-600">Start Date</label>
        <input
          type="date"
          v-model="startDate"
          class="input-field"
        />
      </div>

      <div>
        <label class="text-sm font-medium text-gray-600">End Date</label>
        <input
          type="date"
          v-model="endDate"
          class="input-field"
        />
      </div>
    </div>

    <!-- Summary Totals -->
    <div
      v-if="totals"
      class="grid md:grid-cols-2 gap-4 bg-white p-5 rounded-xl shadow border border-gray-200"
    >
      <div class="summary-card bg-indigo-50">
        <p class="text-sm text-gray-600">Total Quantity Purchased</p>
        <h2 class="summary-value text-indigo-700">
          {{ formatNumber(totals.total_quantity) }}
        </h2>
      </div>

      <div class="summary-card bg-green-50">
        <p class="text-sm text-gray-600">Total Amount Spent</p>
        <h2 class="summary-value text-green-700">
          {{ formatCurrency(totals.total_amount) }}
        </h2>
      </div>
    </div>

    <!-- Report Table -->
    <div class="overflow-x-auto bg-white rounded-xl shadow border">
      <table class="min-w-full border-collapse">
        <thead class="bg-gray-100 text-sm uppercase tracking-wide">
          <tr>
            <th class="th-cell">PO ID</th>
            <th class="th-cell">Product</th>
            <th class="th-cell">Category</th>
            <th class="th-cell">Supplier</th>
            <th class="th-cell">Invoice</th>
            <th class="th-cell">Date</th>
            <th class="th-cell text-right">Qty</th>
            <th class="th-cell text-right">Unit Price</th>
            <th class="th-cell text-right">Total</th>
            <th class="th-cell text-center w-[150px]">Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="row in reportData"
            :key="row.purchase_id + page"
            class="hover:bg-gray-50 transition"
          >
            <td class="td-cell">{{ row.purchase_id }}</td>
            <td class="td-cell">{{ row.product }}</td>
            <td class="td-cell">{{ row.category }}</td>
            <td class="td-cell">{{ row.supplier }}</td>
            <td class="td-cell">{{ row.invoice_number }}</td>
            <td class="td-cell">{{ formatDate(row.purchase_date) }}</td>
            <td class="td-cell text-right">{{ formatNumber(row.qty) }}</td>
            <td class="td-cell text-right">{{ formatCurrency(row.unit_price) }}</td>
            <td class="td-cell text-right">{{ formatCurrency(row.total_price) }}</td>

            <td class="td-cell text-center">
              <div class="flex gap-2 justify-center">
                <router-link
                  :to="`/purchase-orders/${row.purchase_id}`"
                  class="action-btn bg-blue-600 hover:bg-blue-700"
                >
                  🔍
                </router-link>

                <router-link
                  :to="`/purchase-orders/${row.purchase_id}/edit`"
                  class="action-btn bg-yellow-500 hover:bg-yellow-600"
                >
                  ✏️
                </router-link>
              </div>
            </td>
          </tr>

          <tr v-if="!loading && reportData.length === 0">
            <td colspan="10" class="text-center py-10 text-gray-500">
              No records found
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div
      v-if="totalRecords > perPage"
      class="flex justify-between items-center p-3 bg-white rounded-xl shadow"
    >
      <button
        @click="prevPage"
        :disabled="page === 1"
        class="page-btn"
      >
        Prev
      </button>

      <span class="font-semibold">
        Page {{ page }}
      </span>

      <button
        @click="nextPage"
        :disabled="page >= Math.ceil(totalRecords / perPage)"
        class="page-btn"
      >
        Next
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import api from "@/api";

const reportData = ref([]);
const totals = ref(null);
const loading = ref(false);

const page = ref(1);
const perPage = 100;
const totalRecords = ref(0);

const search = ref("");
const startDate = ref("");
const endDate = ref("");

let debounceTimer = null;

/* ---------------- FETCH DATA ---------------- */
const fetchData = async () => {
  loading.value = true;

  try {
    const params = {
      page: page.value,
      per_page: perPage,
      search: search.value.trim(),
      start_date: startDate.value,
      end_date: endDate.value
    };

    const res = await api.get("/reports/purchased-product", { params });

    // Force reactivity
    reportData.value = [...(res.data.data || [])];
    totalRecords.value = Number(res.data.total_records || 0);
    totals.value = { ...(res.data.totals || {}) };

  } catch (err) {
    console.error("Fetch error:", err);
  } finally {
    loading.value = false;
  }
};

/* ---------------- DEBOUNCED FILTER WATCH ---------------- */
watch([search, startDate, endDate], () => {
  page.value = 1;

  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    fetchData();
  }, 400);
});

/* ---------------- PAGE WATCH ---------------- */
watch(page, () => {
  fetchData();
});

/* ---------------- PAGINATION ---------------- */
const nextPage = () => {
  if (page.value < Math.ceil(totalRecords.value / perPage)) {
    page.value++;
  }
};

const prevPage = () => {
  if (page.value > 1) {
    page.value--;
  }
};

/* ---------------- FORMATTERS ---------------- */
const formatDate = d => new Date(d).toLocaleDateString();

const formatNumber = num =>
  num == null ? "0" : Number(num).toLocaleString();

const formatCurrency = num =>
  num == null
    ? "0.00"
    : Number(num).toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });

/* ---------------- INIT ---------------- */
onMounted(fetchData);
</script>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fadeIn {
  animation: fadeIn 0.4s ease-in-out forwards;
}

.input-field {
  border: 1px solid #d1d5db;
  padding: 8px 10px;
  width: 100%;
  border-radius: 8px;
}
.input-field:focus {
  outline: none;
  border-color: #6366f1;
}

.th-cell {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
}
.td-cell {
  padding: 12px;
  border-bottom: 1px solid #f1f1f1;
}

.summary-card {
  padding: 20px;
  border-radius: 12px;
  text-align: center;
}
.summary-value {
  font-size: 2rem;
  font-weight: 800;
}

.action-btn {
  width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  color: white;
  font-size: 16px;
}

.page-btn {
  padding: 8px 16px;
  background: #e5e7eb;
  border-radius: 8px;
}
.page-btn:disabled {
  opacity: 0.4;
}
</style>

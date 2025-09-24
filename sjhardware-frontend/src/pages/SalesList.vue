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
          <th class="p-2 border text-center">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="sale in filteredSales"
          :key="sale.id"
          class="hover:bg-gray-50 cursor-pointer"
        >
          <td class="p-2 border">{{ sale.id }}</td>
          <td class="p-2 border">{{ sale.sale_number }}</td>
          <td class="p-2 border">{{ formatDate(sale.sale_date) }}</td>
          <td class="p-2 border">{{ sale.total_amount.toFixed(2) }}</td>
          <td class="p-2 border">{{ (sale.total_paid || 0).toFixed(2) }}</td>
          <td class="p-2 border">{{ sale.balance.toFixed(2) }}</td>
          <td class="p-2 border">
            <span
              :class="sale.balance === 0 ? 'text-green-600 font-bold' : 'text-red-600 font-bold'"
            >
              {{ sale.balance === 0 ? 'Paid' : 'Unpaid' }}
            </span>
          </td>
          <td class="p-2 border text-center">
            <button
              v-if="sale.balance > 0"
              @click="openPaymentModal(sale)"
              class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded"
            >
              Receive Payment
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Payment Modal -->
    <div
      v-if="showPaymentModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-96">
        <h2 class="text-lg font-bold mb-4">
          Receive Payment for Sale #{{ selectedSale?.sale_id }}
        </h2>

        <div class="mb-4">
          <label class="block text-sm font-medium">Amount</label>
          <input
            v-model.number="paymentForm.amount"
            type="number"
            step="0.01"
            class="w-full p-2 border rounded"
            :max="selectedSale?.balance"
          />
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium">Payment Type</label>
          <select v-model="paymentForm.payment_type" class="w-full p-2 border rounded">
            <option value="Cash">Cash</option>
            <option value="Bank">Bank</option>
            <option value="Mobile Money">Mobile Money</option>
          </select>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium">Payment Account</label>
          <select v-model="paymentForm.payment_account_id" class="w-full p-2 border rounded">
            <option v-for="account in accounts" :key="account.id" :value="account.id">
              {{ account.name }}
            </option>
          </select>
        </div>

        <!-- Transaction Date -->
        <div class="mb-4">
          <label class="block text-sm font-medium">Transaction Date</label>
          <input
            v-model="paymentForm.transaction_date"
            type="date"
            class="w-full p-2 border rounded"
          />
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium">Reference (Optional)</label>
          <input
            v-model="paymentForm.reference"
            type="text"
            class="w-full p-2 border rounded"
            placeholder="Enter reference"
          />
        </div>

        <div class="flex justify-end space-x-2">
          <button
            @click="closePaymentModal"
            class="bg-gray-300 hover:bg-gray-400 text-black px-3 py-1 rounded"
          >
            Cancel
          </button>
          <button
            @click="submitPayment"
            class="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded"
          >
            Save Payment
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../api'; // Your Axios instance

// State
const currentTab = ref('unpaid'); // default tab
const sales = ref([]);
const accounts = ref([]);

// Modal state
const showPaymentModal = ref(false);
const selectedSale = ref(null);

// Payment form
const paymentForm = ref({
  amount: '',
  payment_type: 'Cash',
  payment_account_id: '',
  transaction_date: new Date().toISOString().split('T')[0], // Default to today
  reference: ''
});

// Fetch sales from API
const fetchSales = async () => {
  try {
    const res = await api.get('/sales/');
    console.log('Fetched sales:', res.data);

    sales.value = res.data.map(s => ({
      ...s,
      balance: s.balance // calculate balance
    }));
  } catch (err) {
    console.error('Error fetching sales', err);
  }
};

// Fetch accounts
const fetchAccounts = async () => {
  try {
    const res = await api.get('/accounts');
    accounts.value = res.data;
  } catch (err) {
    console.error('Error fetching accounts', err);
  }
};

// Filter sales based on tab
const filteredSales = computed(() => {
  return currentTab.value === 'paid'
    ? sales.value.filter(s => s.balance <= 0)
    : sales.value.filter(s => s.balance > 0);
});

// Format date nicely
const formatDate = (dateStr) => {
  const d = new Date(dateStr);
  return d.toLocaleDateString();
};

// Open modal
const openPaymentModal = (sale) => {
  selectedSale.value = sale;
  paymentForm.value = {
    amount: sale.balance,
    payment_type: 'Cash',
    payment_account_id: '',
    transaction_date: new Date().toISOString().split('T')[0],
    reference: ''
  };
  console.log('Opening modal for sale:', sale); // Debugging
  showPaymentModal.value = true;
};

// Close modal
const closePaymentModal = () => {
  showPaymentModal.value = false;
  selectedSale.value = null;
};

// Submit payment
const submitPayment = async () => {
  const balance = selectedSale.value.balance;
  const amount = parseFloat(paymentForm.value.amount);

  if (amount > balance) {
    alert(`Amount cannot exceed balance. Max allowed: ${balance.toFixed(2)}`);
    paymentForm.value.amount = balance;
    return;
  }

  const payload = {
    amount,
    payment_type: paymentForm.value.payment_type,
    payment_account_id: paymentForm.value.payment_account_id,
    transaction_date: paymentForm.value.transaction_date,
    reference: paymentForm.value.reference,
    sale_id: selectedSale.value.sale_id // Use correct ID here
  };

  console.log('Submitting payload:', payload); // Debugging

  try {
    await api.post('/payments/', payload);
    closePaymentModal();
    fetchSales(); // Refresh the table
  } catch (err) {
    console.error('Error saving payment', err.response?.data || err.message);
  }
};

onMounted(() => {
  fetchSales();
  fetchAccounts();
});
</script>

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
          <th class="p-2 border text-center">Actions</th>
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
          <td class="p-2 border text-center">
            <button
              v-if="po.total_balance > 0"
              @click="openPaymentModal(po)"
              class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded"
            >
              Receive Payment
            </button>
            <router-link :to="`/purchase-orders/${po.id}`" class="text-indigo-600 underline">
              View
            </router-link>

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
        <h2 class="text-lg font-bold mb-4">Receive Payment for PO #{{ selectedPO?.id }}</h2>

        <div class="mb-4">
          <label class="block text-sm font-medium">Amount</label>
          <input
            v-model="paymentForm.amount"
            type="number"
            step="0.01"
            class="w-full p-2 border rounded"
            :max="selectedPO?.total_balance"
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
import api from '../api';

const currentTab = ref('unpaid');
const purchaseOrders = ref([]);
const accounts = ref([]);

// Modal state
const showPaymentModal = ref(false);
const selectedPO = ref(null);

// Payment form
const paymentForm = ref({
  amount: '',
  payment_type: 'Cash',
  payment_account_id: '',
  transaction_date: new Date().toISOString().split('T')[0], // Default to today
  reference: ''
});

// Fetch purchase orders
const fetchPurchaseOrders = async () => {
  try {
    const res = await api.get('/suppliers/orders');
    purchaseOrders.value = res.data;
  } catch (err) {
    console.error('Error fetching purchase orders', err);
  }
};

// Fetch accounts
const fetchAccounts = async () => {
  try {
    const res = await api.get('/accounts/');
    accounts.value = res.data;
  } catch (err) {
    console.error('Error fetching accounts', err);
  }
};

// Filter purchase orders
const filteredPurchaseOrders = computed(() => {
  return currentTab.value === 'paid'
    ? purchaseOrders.value.filter(po => po.total_balance === 0)
    : purchaseOrders.value.filter(po => po.total_balance > 0);
});

// Format date
const formatDate = (dateStr) => {
  const d = new Date(dateStr);
  return d.toLocaleDateString();
};

// Open modal
const openPaymentModal = (po) => {
  selectedPO.value = po;
  paymentForm.value = {
    amount: po.total_balance,
    payment_type: 'Cash',
    payment_account_id: '',
    transaction_date: new Date().toISOString().split('T')[0],
    reference: ''
  };
  showPaymentModal.value = true;
};

// Close modal
const closePaymentModal = () => {
  showPaymentModal.value = false;
  selectedPO.value = null;
};

// Submit payment
const submitPayment = async () => {
  try {
    const payload = {
      amount: parseFloat(paymentForm.value.amount),
      payment_type: paymentForm.value.payment_type,
      payment_account_id: paymentForm.value.payment_account_id,
      transaction_date: paymentForm.value.transaction_date,
      reference: paymentForm.value.reference
    };

    await api.post(`/suppliers/orders/${selectedPO.value.id}/pay`, payload);

    closePaymentModal();
    fetchPurchaseOrders();
  } catch (err) {
    console.error('Error saving payment', err.response?.data || err.message);
  }
};

onMounted(() => {
  fetchPurchaseOrders();
  fetchAccounts();
});
</script>

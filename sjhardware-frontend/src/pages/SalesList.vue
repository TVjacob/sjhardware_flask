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
          <td class="p-2 border">{{ sale.sale_id }}</td>
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
          <td class="p-2 border text-center space-x-2">
            <!-- Receive Payment -->
            <button
              v-if="sale.balance > 0"
              @click="openPaymentModal(sale)"
              class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded"
            >
              Receive Payment
            </button>

            <!-- View Report -->
            <button
              @click="previewPaymentReport(sale.sale_id)"
              class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded"
            >
              View Report
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

    <!-- Full Report Modal -->
    <div
      v-if="showReportModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"
    >
      <div class="bg-white rounded-lg shadow-lg p-6 w-4/5 max-w-5xl relative">
        <h2 class="text-xl font-bold mb-4">
          {{ paymentReport.document_type }} - Sale #{{ paymentReport.sale_number }}
        </h2>

        <!-- Close Button -->
        <button
          @click="closeReportModal"
          class="absolute top-4 right-4 text-gray-500 hover:text-gray-800"
        >
          ✖
        </button>

        <!-- Customer Info -->
        <div class="mb-4">
          <h3 class="font-bold">Customer Information</h3>
          <p><strong>Name:</strong> {{ paymentReport.customer.name }}</p>
          <p><strong>Phone:</strong> {{ paymentReport.customer.phone }}</p>
          <p><strong>Email:</strong> {{ paymentReport.customer.email }}</p>
          <p><strong>Address:</strong> {{ paymentReport.customer.address }}</p>
        </div>

        <!-- Items Table -->
        <h3 class="font-bold mt-4">Items Sold</h3>
        <table class="min-w-full border mt-2">
          <thead>
            <tr class="bg-gray-100">
              <th class="p-2 border">Product</th>
              <th class="p-2 border">Quantity</th>
              <th class="p-2 border">Unit Price</th>
              <th class="p-2 border">Total Price</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in paymentReport.items" :key="item.product_name">
              <td class="p-2 border">{{ item.product_name }}</td>
              <td class="p-2 border">{{ item.quantity }}</td>
              <td class="p-2 border">{{ item.unit_price.toFixed(2) }}</td>
              <td class="p-2 border">{{ item.total_price.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>

        <!-- Payment History -->
        <h3 class="font-bold mt-6">Payment History</h3>
        <table class="min-w-full border mt-2">
          <thead>
            <tr class="bg-gray-100">
              <th class="p-2 border">Date</th>
              <th class="p-2 border">Amount</th>
              <th class="p-2 border">Type</th>
              <th class="p-2 border">Reference</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="payment in paymentReport.payments" :key="payment.date">
              <td class="p-2 border">{{ payment.date }}</td>
              <td class="p-2 border">{{ payment.amount.toFixed(2) }}</td>
              <td class="p-2 border">{{ payment.type }}</td>
              <td class="p-2 border">{{ payment.reference || '-' }}</td>
            </tr>
          </tbody>
        </table>

        <!-- Totals -->
        <div class="mt-6 text-right space-y-1">
          <p><strong>Grand Total:</strong> {{ paymentReport.totals.grand_total.toFixed(2) }}</p>
          <p><strong>Amount Paid:</strong> {{ paymentReport.totals.amount_paid.toFixed(2) }}</p>
          <p><strong>Balance:</strong> {{ paymentReport.totals.balance.toFixed(2) }}</p>
          <p><strong>Change:</strong> {{ paymentReport.totals.change.toFixed(2) }}</p>
        </div>

        <!-- Actions -->
        <div class="flex justify-end space-x-4 mt-6">
          <button
            @click="printReport"
            class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded"
          >
            Print
          </button>
          <button
            @click="closeReportModal"
            class="bg-gray-300 hover:bg-gray-400 text-black px-4 py-2 rounded"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../api'; // Axios instance

// State
const currentTab = ref('unpaid');
const sales = ref([]);
const accounts = ref([]);

// Payment Modal
const showPaymentModal = ref(false);
const selectedSale = ref(null);

// Report Modal
const showReportModal = ref(false);
const paymentReport = ref(null);

// Payment Form
const paymentForm = ref({
  amount: '',
  payment_type: 'Cash',
  payment_account_id: '',
  transaction_date: new Date().toISOString().split('T')[0],
  reference: ''
});

// Fetch sales
const fetchSales = async () => {
  try {
    const res = await api.get('/sales/');
    sales.value = res.data.map(s => ({
      ...s,
      balance: s.balance
    }));
  } catch (err) {
    console.error('Error fetching sales', err);
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

// Filter sales
const filteredSales = computed(() => {
  return currentTab.value === 'paid'
    ? sales.value.filter(s => s.balance <= 0)
    : sales.value.filter(s => s.balance > 0);
});

// Date formatter
const formatDate = (dateStr) => {
  const d = new Date(dateStr);
  return d.toLocaleDateString();
};

// Open Payment Modal
const openPaymentModal = (sale) => {
  selectedSale.value = sale;
  paymentForm.value = {
    amount: sale.balance,
    payment_type: 'Cash',
    payment_account_id: '',
    transaction_date: new Date().toISOString().split('T')[0],
    reference: ''
  };
  showPaymentModal.value = true;
};

// Close Payment Modal
const closePaymentModal = () => {
  showPaymentModal.value = false;
  selectedSale.value = null;
};

// Submit Payment
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
    sale_id: selectedSale.value.sale_id
  };

  try {
    await api.post('/payments/', payload);
    closePaymentModal();
    fetchSales();
  } catch (err) {
    console.error('Error saving payment', err.response?.data || err.message);
  }
};

// Preview Report
const previewPaymentReport = async (saleId) => {
  try {
    const res = await api.get(`/payments/details?sale_id=${saleId}&type=invoice`);
    paymentReport.value = res.data;
    showReportModal.value = true;
  } catch (err) {
    console.error('Error fetching report details', err);
  }
};

// Close Report Modal
const closeReportModal = () => {
  showReportModal.value = false;
  paymentReport.value = null;
};

// Print Report
const printReport = () => {
  const printContents = document.querySelector('.bg-white.rounded-lg.shadow-lg.p-6').innerHTML;
  const printWindow = window.open('', '', 'width=800,height=600');
  printWindow.document.write('<html><head><title>Payment Report</title></head><body>');
  printWindow.document.write(printContents);
  printWindow.document.write('</body></html>');
  printWindow.document.close();
  printWindow.print();
};

onMounted(() => {
  fetchSales();
  fetchAccounts();
});
</script>

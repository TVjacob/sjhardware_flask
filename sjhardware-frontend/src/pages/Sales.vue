<template>
  <div class="p-6 max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-6 text-gray-800">Sales Dashboard</h1>

    <!-- --------- Sale Header --------- -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">

      <!-- Sale Date -->
      <div>
        <label class="block font-semibold mb-1">Sale Date</label>
        <input
          type="date"
          v-model="saleHeader.sale_date"
          class="border p-2 rounded w-full focus:ring-2 focus:ring-indigo-400 transition"
        />
      </div>

      <!-- Customer Typeahead -->
      <div class="relative">
        <label class="block font-semibold mb-1">Customer</label>
        <input
          type="text"
          v-model="saleHeader.customer_name"
          @input="debouncedSearchCustomer"
          placeholder="Search or type customer"
          class="border p-2 rounded w-full focus:ring-2 focus:ring-indigo-400 transition"
        />
        <ul
          v-if="customerResults.length"
          class="absolute z-50 bg-white border rounded shadow-lg w-full max-h-40 overflow-auto mt-1"
        >
          <li
            v-for="cust in customerResults"
            :key="cust.id"
            @click="selectCustomer(cust)"
            class="p-2 hover:bg-indigo-100 cursor-pointer transition"
          >
            {{ cust.name }}
          </li>
        </ul>
      </div>

      <!-- Amount Paid -->
      <div>
        <label class="block font-semibold mb-1">Amount Paid</label>
        <input
          type="number"
          v-model.number="saleHeader.amount_paid"
          min="0"
          class="border p-2 rounded w-full focus:ring-2 focus:ring-indigo-400 transition"
        />
      </div>

      <!-- Memo -->
      <div>
        <label class="block font-semibold mb-1">Memo / Details</label>
        <input
          type="text"
          v-model="saleHeader.memo"
          placeholder="Optional"
          class="border p-2 rounded w-full focus:ring-2 focus:ring-indigo-400 transition"
        />
      </div>

      <!-- Payment Account Typeahead -->
      <div class="relative">
        <label class="block font-semibold mb-1">Payment Account</label>
        <input
          type="text"
          v-model="saleHeader.payment_account_name"
          @input="debouncedSearchPaymentAccount"
          placeholder="Search or type account"
          class="border p-2 rounded w-full focus:ring-2 focus:ring-indigo-400 transition"
        />
        <ul
          v-if="paymentResults.length"
          class="absolute z-50 bg-white border rounded shadow-lg w-full max-h-40 overflow-auto mt-1"
        >
          <li
            v-for="acc in paymentResults"
            :key="acc.id"
            @click="selectPaymentAccount(acc)"
            class="p-2 hover:bg-indigo-100 cursor-pointer transition"
          >
            {{ acc.name }}
          </li>
        </ul>
      </div>
    </div>

    <!-- --------- Sale Items Table --------- -->
    <table class="min-w-full border mb-4 rounded overflow-visible shadow-sm">
      <thead class="bg-gray-100">
        <tr>
          <th class="p-2 border">Product</th>
          <th class="p-2 border">Stock Qty</th>
          <th class="p-2 border">Unit</th>
          <th class="p-2 border">Unit Price</th>
          <th class="p-2 border">Quantity</th>
          <th class="p-2 border">Total Price</th>
          <th class="p-2 border">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(item, idx) in saleItems"
          :key="idx"
          class="hover:bg-gray-50 transition"
        >
          <td class="p-2 border relative">
            <input
              type="text"
              v-model="item.product_name"
              @input="debouncedSearchProduct(item)"
              placeholder="Search product..."
              class="border p-1 rounded w-full focus:ring-2 focus:ring-indigo-400 transition"
            />
            <ul
              v-if="item.searchResults.length"
              class="absolute z-50 bg-white border rounded shadow-lg w-full max-h-32 overflow-auto mt-1"
            >
              <li
                v-for="product in item.searchResults"
                :key="product.id"
                @click="selectProduct(item, product)"
                class="p-1 hover:bg-indigo-100 cursor-pointer transition"
              >
                {{ product.name }} (Stock: {{ product.quantity }})
              </li>
            </ul>
          </td>
          <td class="p-2 border">{{ item.stock_qty || 0 }}</td>
          <td class="p-2 border">{{ item.unit || '' }}</td>
          <td class="p-2 border">
            <input
              type="number"
              v-model.number="item.unit_price"
              min="0"
              class="border p-1 rounded w-full focus:ring-2 focus:ring-indigo-400 transition"
              :disabled="!item.product_id"
              @input="calculateTotal(item)"
            />
          </td>
          <td class="p-2 border">
            <input
              type="number"
              v-model.number="item.quantity"
              min="0"
              class="border p-1 rounded w-full focus:ring-2 focus:ring-indigo-400 transition"
              :disabled="!item.product_id"
              @input="validateQuantity(item)"
            />
            <p v-if="item.error" class="text-red-500 text-xs mt-1">{{ item.error }}</p>
          </td>
          <td class="p-2 border">{{ item.total_price.toFixed(2) }}</td>
          <td class="p-2 border">
            <button
              @click="removeRow(idx)"
              class="bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded transition transform hover:scale-105"
            >
              Remove
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <button
      @click="addRow"
      class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded transition transform hover:scale-105 mb-4"
    >
      Add Item
    </button>

    <!-- --------- Grand Total --------- -->
    <div class="text-right text-xl font-bold mb-6">
      Grand Total: {{ grandTotal.toFixed(2) }}
    </div>

    <!-- --------- Save Button --------- -->
    <button
      @click="saveSale"
      class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded w-full md:w-auto transition transform hover:scale-105"
    >
      Save Sale
    </button>

    <!-- --------- Report Modal --------- -->
    <ReportModal
      v-if="showReportModal"
      :report="invoiceData"
      v-model:show="showReportModal"
    />
  </div>
</template>

<script>
import api from '../api';
import debounce from 'lodash.debounce';
import ReportModal from './ReportModal.vue';
import { watch } from 'vue';

export default {
  data() {
    return {
      saleHeader: {
        sale_date: new Date().toISOString().substr(0, 10),
        amount_paid: 0,
        memo: '',
        payment_account: '',
        payment_account_name: '',
        customer_id: '',
        customer_name: ''
      },
      paymentAccounts: [],
      customers: [],
      customerResults: [],
      paymentResults: [],
      saleItems: [],
      showReportModal: false,
      invoiceData: null,
    };
  },
  computed: {
    grandTotal() {
      return this.saleItems.reduce((sum, item) => sum + item.total_price, 0);
    }
  },
  methods: {
    async fetchPaymentAccounts() {
      const res = await api.get('/accounts/?type=asset');
      this.paymentAccounts = res.data;
    },
    async fetchCustomers() {
      const res = await api.get('/customer/');
      this.customers = res.data;
    },
    searchCustomer() {
      const q = this.saleHeader.customer_name.toLowerCase();
      this.customerResults = q ? this.customers.filter(c => c.name.toLowerCase().includes(q)) : [];
    },
    selectCustomer(cust) {
      this.saleHeader.customer_id = cust.id;
      this.saleHeader.customer_name = cust.name;
      this.customerResults = [];
    },
    searchPaymentAccount() {
      const q = this.saleHeader.payment_account_name.toLowerCase();
      this.paymentResults = q ? this.paymentAccounts.filter(a => a.name.toLowerCase().includes(q)) : [];
    },
    selectPaymentAccount(acc) {
      this.saleHeader.payment_account = acc.id;
      this.saleHeader.payment_account_name = acc.name;
      this.paymentResults = [];
    },
    async searchProduct(item) {
      if (!item.product_name || item.product_name.length < 2) {
        item.searchResults = [];
        return;
      }
      try {
        const res = await api.get(`/inventory/products/search?name=${item.product_name}`);
        item.searchResults = res.data.map(p => ({
          id: p.id,
          name: p.name,
          quantity: p.quantity || 0,
          unit: p.unit || '',
          price: p.price || 0
        }));
      } catch (err) {
        console.error(err);
        item.searchResults = [];
      }
    },
    selectProduct(item, product) {
      item.product_id = product.id;
      item.product_name = product.name;
      item.stock_qty = product.quantity;
      item.unit = product.unit;
      item.unit_price = product.price;
      item.quantity = 0;
      item.total_price = 0;
      item.searchResults = [];
      item.error = '';
    },
    addRow() {
      this.saleItems.push({
        product_id: null,
        product_name: '',
        stock_qty: 0,
        unit: '',
        unit_price: 0,
        quantity: 0,
        total_price: 0,
        searchResults: [],
        error: ''
      });
    },
    removeRow(idx) {
      this.saleItems.splice(idx, 1);
    },
    validateQuantity(item) {
      if (item.quantity > item.stock_qty) item.quantity = item.stock_qty;
      if (item.quantity < 0) item.quantity = 0;
      this.calculateTotal(item);
    },
    calculateTotal(item) {
      item.total_price = (item.quantity || 0) * (item.unit_price || 0);
    },
    async saveSale() {
      if (!this.saleHeader.sale_date) return alert("Please select a sale date.");
      if (!this.saleHeader.customer_id) return alert("Please select a customer.");
      if (!this.saleItems.length) return alert("Please add at least one sale item.");
      if (this.amount_paid > 0 && !this.saleHeader.payment_account) {
        return alert("Please select a payment account for the amount paid.");
      }
      // if()

      for (const [idx, item] of this.saleItems.entries()) {
        if (!item.product_id) return alert(`Item ${idx + 1}: Please select a product.`);
        if (!item.quantity || item.quantity <= 0) return alert(`Item ${idx + 1}: Quantity must be greater than 0.`);
      }

      const payload = {
        sale_date: this.saleHeader.sale_date,
        customer_id: this.saleHeader.customer_id,
        payment_account_id: this.saleHeader.payment_account,
        amount_paid: this.saleHeader.amount_paid || 0,
        memo: this.saleHeader.memo || '',
        items: this.saleItems.map(item => ({
          product_id: item.product_id,
          unit_price: item.unit_price,
          quantity: item.quantity,
          total_price: item.total_price
        }))
      };

      try {
        const res = await api.post('/sales/', payload);
        alert("Sale saved successfully!");
        // Fetch invoice data
        const invoiceRes = await api.get(`/payments/details?sale_id=${res.data.sale_id}&type=invoice`);
        this.invoiceData = invoiceRes.data;
        this.showReportModal = true;
      } catch (err) {
        console.error("Error saving sale:", err);
        let message = "Failed to save sale. Check console.";
        if (err.response && err.response.data && err.response.data.error) {
          message = err.response.data.error;
        } else if (err.message) {
          message = err.message;
        }
        alert(message);
      }
    },
    resetForm() {
      this.saleHeader = {
        sale_date: new Date().toISOString().substr(0, 10),
        amount_paid: 0,
        memo: '',
        payment_account: '',
        payment_account_name: '',
        customer_id: '',
        customer_name: ''
      };
      this.saleItems = [];
      this.customerResults = [];
      this.paymentResults = [];
      this.addRow();
    },
    debouncedSearchProduct: debounce(function(item) { this.searchProduct(item); }, 300),
    debouncedSearchCustomer: debounce(function() { this.searchCustomer(); }, 300),
    debouncedSearchPaymentAccount: debounce(function() { this.searchPaymentAccount(); }, 300)
  },
  mounted() {
    this.fetchPaymentAccounts();
    this.fetchCustomers();
    this.addRow();
  },
  watch: {
    showReportModal(val) {
      if (!val) this.resetForm();
    }
  },
  components: { ReportModal }
};
</script>

<style scoped>
input[type="text"],
input[type="number"],
input[type="date"],
select {
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  transition: all 0.2s ease-in-out;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
input:focus,
select:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.2);
}
button {
  transition: all 0.2s ease-in-out;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
table {
  border-collapse: separate;
  border-spacing: 0;
  width: 100%;
  border-radius: 0.5rem;
}
thead tr { background-color: #f3f4f6; }
th, td { padding: 0.75rem 0.5rem; border-bottom: 1px solid #e5e7eb; }
tbody tr:hover { background-color: #f9fafb; transition: background-color 0.2s ease-in-out; }
ul { width: 100%; border-radius: 0.5rem; max-height: 10rem; overflow-y: auto; z-index: 50; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
ul li { padding: 0.5rem 0.75rem; cursor: pointer; transition: all 0.2s ease; }
ul li:hover { background-color: #e0e7ff; }
.text-red-500 { color: #dc2626; font-size: 0.75rem; }
</style>

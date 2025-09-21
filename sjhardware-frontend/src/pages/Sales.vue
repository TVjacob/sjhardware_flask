<template>
  <div class="p-6 max-w-6xl mx-auto">
    <h1 class="text-2xl font-bold mb-4">Sales Dashboard</h1>

    <!-- --------- Sale Header --------- -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
      <div>
        <label class="block font-semibold mb-1">Sale Date</label>
        <input type="date" v-model="saleHeader.sale_date" class="border p-2 rounded w-full" />
      </div>
      <div>
        <label class="block font-semibold mb-1">Customer</label>
        <select v-model="saleHeader.customer_id" class="border p-2 rounded w-full">
          <option value="" disabled>Select customer</option>
          <option v-for="customer in customers" :key="customer.id" :value="customer.id">
            {{ customer.name }}
          </option>
        </select>
      </div>
      <div>
        <label class="block font-semibold mb-1">Amount Paid</label>
        <input type="number" v-model.number="saleHeader.amount_paid" class="border p-2 rounded w-full" />
      </div>
      <div>
        <label class="block font-semibold mb-1">Memo / Details</label>
        <input type="text" v-model="saleHeader.memo" class="border p-2 rounded w-full" />
      </div>
      <div>
        <label class="block font-semibold mb-1">Payment Account</label>
        <select v-model="saleHeader.payment_account" class="border p-2 rounded w-full">
          <option v-for="account in paymentAccounts" :key="account.id" :value="account.id">{{ account.name }}</option>
        </select>
      </div>
    </div>

    <!-- --------- Sale Items --------- -->
    <table class="min-w-full border mb-4">
      <thead>
        <tr class="bg-gray-100">
          <th class="p-2 border">Product</th>
          <th class="p-2 border">Stock Qty</th>
          <th class="p-2 border">Unit Price</th>
          <th class="p-2 border">Quantity</th>
          <th class="p-2 border">Total Price</th>
          <th class="p-2 border">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, idx) in saleItems" :key="idx">
          <td class="p-2 border">
            <input
              type="text"
              v-model="item.product_name"
              @input="searchProduct(item, idx)"
              class="border p-1 rounded w-full"
              placeholder="Search product..."
            />
            <ul v-if="item.searchResults.length" class="bg-white border mt-1 max-h-32 overflow-auto absolute z-10">
              <li
                v-for="product in item.searchResults"
                :key="product.id"
                @click="selectProduct(item, product)"
                class="p-1 hover:bg-gray-200 cursor-pointer"
              >
                {{ product.name }} (Stock: {{ product.quantity }})
              </li>
            </ul>
          </td>
          <td class="p-2 border">{{ item.stock_qty || 0 }}</td>
          <td class="p-2 border">
            <input type="number" v-model.number="item.unit_price" class="border p-1 rounded w-full" @input="calculateTotal(item)" />
          </td>
          <td class="p-2 border">
            <input type="number" v-model.number="item.quantity" class="border p-1 rounded w-full" @input="calculateTotal(item)" />
          </td>
          <td class="p-2 border">{{ item.total_price.toFixed(2) }}</td>
          <td class="p-2 border">
            <button @click="removeRow(idx)" class="bg-red-500 text-white px-2 py-1 rounded">Remove</button>
          </td>
        </tr>
      </tbody>
    </table>

    <button @click="addRow" class="bg-green-500 text-white px-4 py-2 rounded mb-4">Add Item</button>

    <!-- --------- Grand Total --------- -->
    <div class="text-right text-xl font-bold mb-6">
      Grand Total: {{ grandTotal.toFixed(2) }}
    </div>

    <!-- --------- Save Button --------- -->
    <button @click="saveSale" class="bg-indigo-600 text-white px-6 py-3 rounded w-full md:w-auto">Save Sale</button>
  </div>
</template>

<script>
import api from '../api'; // Axios instance

export default {
  data() {
    return {
      saleHeader: {
        sale_date: new Date().toISOString().substr(0, 10),
        amount_paid: 0,
        memo: '',
        payment_account: '',
        customer_id: ''
      },
      paymentAccounts: [], // Fetch from API or define asset cash accounts
      customers: [],       // New array for customer selection
      saleItems: [],
      products: []         // All products fetched for search
    };
  },
  computed: {
    grandTotal() {
      return this.saleItems.reduce((sum, item) => sum + item.total_price, 0);
    }
  },
  methods: {
    async fetchProducts() {
      const res = await api.get('/products'); // API endpoint to get products
      this.products = res.data;
    },
    async fetchPaymentAccounts() {
      const res = await api.get('/accounts?type=asset'); // Example
      this.paymentAccounts = res.data;
    },
    async fetchCustomers() {
      const res = await api.get('/customers'); // API endpoint to get customers
      this.customers = res.data;
    },
    addRow() {
      this.saleItems.push({
        product_id: null,
        product_name: '',
        stock_qty: 0,
        unit_price: 0,
        quantity: 1,
        total_price: 0,
        searchResults: []
      });
    },
    removeRow(idx) {
      this.saleItems.splice(idx, 1);
    },
    searchProduct(item, idx) {
      if (!item.product_name) {
        item.searchResults = [];
        return;
      }
      const query = item.product_name.toLowerCase();
      item.searchResults = this.products.filter(p => p.name.toLowerCase().includes(query));
    },
    selectProduct(item, product) {
      item.product_id = product.id;
      item.product_name = product.name;
      item.stock_qty = product.quantity;
      item.unit_price = product.price;
      item.quantity = 1;
      this.calculateTotal(item);
      item.searchResults = [];
    },
    calculateTotal(item) {
      item.total_price = (item.quantity || 0) * (item.unit_price || 0);
    },
    async saveSale() {
      if (!this.saleHeader.payment_account) {
        alert('Select a payment account');
        return;
      }
      if (!this.saleHeader.customer_id) {
        alert('Select a customer');
        return;
      }
      if (!this.saleItems.length) {
        alert('Add at least one item');
        return;
      }

      const payload = {
        sale_number: `SAL-${Date.now()}`,
        sale_date: this.saleHeader.sale_date,
        amount_paid: this.saleHeader.amount_paid,
        memo: this.saleHeader.memo,
        payment_account: this.saleHeader.payment_account,
        customer_id: this.saleHeader.customer_id,
        items: this.saleItems.map(i => ({
          product_id: i.product_id,
          quantity: i.quantity
        }))
      };

      try {
        const res = await api.post('/sales/', payload);
        alert('Sale saved successfully! ID: ' + res.data.sale_id);

        // Reset form
        this.saleHeader = { sale_date: new Date().toISOString().substr(0, 10), amount_paid: 0, memo: '', payment_account: '', customer_id: '' };
        this.saleItems = [];
        this.addRow();
      } catch (err) {
        alert('Error saving sale: ' + err.response.data.error);
      }
    }
  },
  mounted() {
    this.fetchProducts();
    this.fetchPaymentAccounts();
    this.fetchCustomers();
    this.addRow(); // Start with one row
  }
};
</script>

<style scoped>
/* Position search results dropdown */
ul {
  width: 100%;
}
</style>

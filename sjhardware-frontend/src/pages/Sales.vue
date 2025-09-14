<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Sales & Invoices</h1>

    <!-- Tabs -->
    <div class="flex mb-4">
      <button 
        :class="activeTab === 'sales' ? 'bg-blue-500 text-white' : 'bg-gray-200'" 
        class="px-4 py-2 rounded-l"
        @click="activeTab = 'sales'"
      >
        Sales
      </button>
      <button 
        :class="activeTab === 'invoices' ? 'bg-blue-500 text-white' : 'bg-gray-200'" 
        class="px-4 py-2 rounded-r"
        @click="activeTab = 'invoices'"
      >
        Invoices
      </button>
    </div>

    <!-- Create Sale Form -->
    <div v-if="activeTab === 'sales'" class="mb-6 border p-4 rounded bg-gray-50">
      <h2 class="text-xl mb-2">Create Sale</h2>
      <form @submit.prevent="createSale" class="flex flex-wrap gap-2">
        <input 
          v-model="saleForm.sale_number" 
          placeholder="Sale Number" 
          class="border p-2 rounded w-48"
          required
        />

        <!-- Products Section -->
        <div class="flex flex-col w-full">
          <h3 class="font-semibold mt-2">Products</h3>
          <div v-for="(item, index) in saleForm.items" :key="index" class="flex gap-2 mb-2">
            <select 
              v-model="item.product_id" 
              class="border p-2 rounded w-48"
              @change="setProductPrice(item)"
            >
              <option value="">Select Product</option>
              <option v-for="p in products" :key="p.id" :value="p.id">
                {{ p.name }}
              </option>
            </select>
            <input 
              v-model.number="item.quantity" 
              type="number" 
              placeholder="Qty" 
              class="border p-2 rounded w-20"
              min="1"
              @input="calculateTotal"
            />
            <input 
              v-model="item.unit_price" 
              type="number" 
              placeholder="Unit Price" 
              class="border p-2 rounded w-28"
              readonly
            />
            <button @click="removeItem(index)" type="button" class="bg-red-500 text-white px-2 rounded">X</button>
          </div>
          <button @click="addItem" type="button" class="bg-green-500 text-white px-4 py-1 rounded">+ Add Product</button>
        </div>

        <div class="mt-4 w-full flex justify-between items-center">
          <p class="font-bold">Total: {{ totalAmount }}</p>
          <button class="bg-blue-600 text-white px-4 py-2 rounded">Save Sale</button>
        </div>
      </form>
    </div>

    <!-- Sales Table -->
    <div v-if="activeTab === 'sales'" class="mt-4">
      <h2 class="text-lg font-semibold mb-2">All Sales</h2>
      <table class="min-w-full bg-white border">
        <thead>
          <tr>
            <th class="p-2 border">Sale #</th>
            <th class="p-2 border">Total Amount</th>
            <th class="p-2 border">Status</th>
            <th class="p-2 border">Date</th>
            <th class="p-2 border">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="sale in sales" :key="sale.sale_id">
            <td class="p-2 border">{{ sale.sale_number }}</td>
            <td class="p-2 border">{{ sale.total_amount }}</td>
            <td class="p-2 border">{{ sale.payment_status }}</td>
            <td class="p-2 border">{{ formatDate(sale.sale_date) }}</td>
            <td class="p-2 border">
              <button @click="deleteSale(sale.sale_id)" class="bg-red-500 text-white px-2 py-1 rounded">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Invoices Table -->
    <div v-if="activeTab === 'invoices'" class="mt-4">
      <h2 class="text-lg font-semibold mb-2">All Invoices</h2>
      <table class="min-w-full bg-white border">
        <thead>
          <tr>
            <th class="p-2 border">Invoice #</th>
            <th class="p-2 border">Sale #</th>
            <th class="p-2 border">Amount</th>
            <th class="p-2 border">Created</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="inv in invoices" :key="inv.invoice_id">
            <td class="p-2 border">{{ inv.invoice_number }}</td>
            <td class="p-2 border">{{ inv.sale_id }}</td>
            <td class="p-2 border">{{ inv.total_amount }}</td>
            <td class="p-2 border">{{ formatDate(inv.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from '../api';

export default {
  data() {
    return {
      activeTab: 'sales',
      sales: [],
      invoices: [],
      products: [],
      saleForm: {
        sale_number: '',
        items: [
          { product_id: '', quantity: 1, unit_price: 0 },
        ],
      },
    };
  },
  computed: {
    totalAmount() {
      return this.saleForm.items.reduce((sum, i) => sum + (i.quantity * i.unit_price), 0);
    },
  },
  methods: {
    async fetchData() {
      const [salesRes, invoicesRes, productsRes] = await Promise.all([
        api.get('/sales/'),
        api.get('/sales/invoices'),
        api.get('/inventory/products'),
      ]);
      this.sales = salesRes.data;
      this.invoices = invoicesRes.data;
      this.products = productsRes.data;
    },
    addItem() {
      this.saleForm.items.push({ product_id: '', quantity: 1, unit_price: 0 });
    },
    removeItem(index) {
      this.saleForm.items.splice(index, 1);
    },
    setProductPrice(item) {
      const product = this.products.find(p => p.id === item.product_id);
      if (product) {
        item.unit_price = product.price;
      }
    },
    calculateTotal() {
      // Auto computed by totalAmount
    },
    async createSale() {
      await api.post('/sales/', this.saleForm);
      this.saleForm = { sale_number: '', items: [{ product_id: '', quantity: 1, unit_price: 0 }] };
      this.fetchData();
    },
    async deleteSale(saleId) {
      if (confirm('Delete this sale?')) {
        await api.delete(`/sales/${saleId}`);
        this.fetchData();
      }
    },
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleDateString();
    },
  },
  mounted() {
    this.fetchData();
  },
};
</script>

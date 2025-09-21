<template>
  <div class="p-6 max-w-6xl mx-auto">
    <h1 class="text-2xl font-bold mb-4">Purchase Order Dashboard</h1>

    <!-- --------- Purchase Order Header --------- -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div>
        <label class="block font-semibold mb-1">Supplier</label>
        <select v-model="poHeader.supplier_id" class="border p-2 rounded w-full">
          <option value="" disabled>Select Supplier</option>
          <option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">
            {{ supplier.name }}
          </option>
        </select>
      </div>
      <div>
        <label class="block font-semibold mb-1">Invoice Number</label>
        <input type="text" v-model="poHeader.invoice_number" class="border p-2 rounded w-full" />
      </div>
      <div>
        <label class="block font-semibold mb-1">Memo / Details</label>
        <input type="text" v-model="poHeader.memo" class="border p-2 rounded w-full" />
      </div>
      <div>
        <label class="block font-semibold mb-1">Purchase Date</label>
        <input type="date" v-model="poHeader.purchase_date" class="border p-2 rounded w-full" />
      </div>
    </div>

    <!-- --------- Purchase Order Items --------- -->
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
        <tr v-for="(item, idx) in poItems" :key="idx">
          <td class="p-2 border relative">
            <input
              type="text"
              v-model="item.product_name"
              @input="searchProduct(item, idx)"
              placeholder="Search product..."
              class="border p-1 rounded w-full"
            />
            <ul v-if="item.searchResults.length" class="absolute bg-white border mt-1 max-h-32 overflow-auto z-10 w-full">
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
    <button @click="savePurchaseOrder" class="bg-indigo-600 text-white px-6 py-3 rounded w-full md:w-auto">Save Purchase Order</button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../api'; // Axios instance

// --------- Purchase Order Header ---------
const poHeader = ref({
  supplier_id: '',
  invoice_number: '',
  memo: '',
  purchase_date: new Date().toISOString().substr(0, 10)
});

// --------- Purchase Order Items ---------
const poItems = ref([]);

// --------- Suppliers ---------
const suppliers = ref([]);

// --------- Products for search ---------
const products = ref([]);

// --------- Computed grand total ---------
const grandTotal = computed(() => {
  return poItems.value.reduce((sum, item) => sum + item.total_price, 0);
});

// --------- Methods ---------
const fetchSuppliers = async () => {
  const res = await api.get('/suppliers/');
  suppliers.value = res.data;
};

const fetchProducts = async () => {
  const res = await api.get('/products/');
  products.value = res.data;
};

const addRow = () => {
  poItems.value.push({
    product_id: null,
    product_name: '',
    stock_qty: 0,
    unit_price: 0,
    quantity: 1,
    total_price: 0,
    searchResults: []
  });
};

const removeRow = (idx) => {
  poItems.value.splice(idx, 1);
};

const searchProduct = (item, idx) => {
  if (!item.product_name) {
    item.searchResults = [];
    return;
  }
  const query = item.product_name.toLowerCase();
  item.searchResults = products.value.filter(p => p.name.toLowerCase().includes(query));
};

const selectProduct = (item, product) => {
  item.product_id = product.id;
  item.product_name = product.name;
  item.stock_qty = product.quantity;
  item.unit_price = product.price || 0;
  item.quantity = 1;
  calculateTotal(item);
  item.searchResults = [];
};

const calculateTotal = (item) => {
  item.total_price = (item.quantity || 0) * (item.unit_price || 0);
};

const savePurchaseOrder = async () => {
  if (!poHeader.value.supplier_id) {
    alert('Please select a supplier');
    return;
  }
  if (poItems.value.length === 0) {
    alert('Add at least one item');
    return;
  }

  const payload = {
    supplier_id: poHeader.value.supplier_id,
    invoice_number: poHeader.value.invoice_number,
    memo: poHeader.value.memo,
    purchase_date: poHeader.value.purchase_date,
    items: poItems.value.map(i => ({
      product_id: i.product_id,
      quantity: i.quantity,
      unit_price: i.unit_price
    }))
  };

  try {
    const res = await api.post('/suppliers/orders', payload);
    alert(`Purchase Order saved successfully! PO ID: ${res.data.po_id}`);
    // Reset form
    poHeader.value = { supplier_id: '', invoice_number: '', memo: '', purchase_date: new Date().toISOString().substr(0,10) };
    poItems.value = [];
    addRow();
  } catch (err) {
    alert('Error saving purchase order: ' + err.response.data.error);
  }
};

// --------- On mounted ---------
onMounted(() => {
  fetchSuppliers();
  fetchProducts();
  addRow(); // start with one row
});
</script>

<style scoped>
ul {
  width: 100%;
}
</style>

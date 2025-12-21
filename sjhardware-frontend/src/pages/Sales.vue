<template>
  <div class="p-6 max-w-7xl mx-auto bg-gray-50 min-h-screen">
    <h1 class="text-4xl font-bold mb-8 text-gray-800">💰 Sales Dashboard</h1>

    <!-- Sale Header -->
    <div class="bg-white rounded-2xl shadow-lg p-6 mb-8">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-6">
        <!-- Sale Date -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">Sale Date</label>
          <input
            type="date"
            v-model="saleHeader.sale_date"
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          />
        </div>

        <!-- Customer -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">Customer</label>
          <v-autocomplete
            v-model="saleHeader.customer_id"
            :items="customers"
            item-title="name"
            item-value="id"
            placeholder="Select or search customer"
            variant="outlined"
            density="comfortable"
            clearable
            :loading="loadingCustomers"
          ></v-autocomplete>
        </div>

        <!-- Amount Paid -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">Amount Paid</label>
          <input
            type="number"
            v-model.number="saleHeader.amount_paid"
            min="0"
            step="100"
            placeholder="0"
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none text-right"
          />
        </div>

        <!-- Memo -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">Memo / Note</label>
          <input
            type="text"
            v-model="saleHeader.memo"
            placeholder="Optional note..."
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          />
        </div>

        <!-- Payment Account -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">Payment Account</label>
          <v-autocomplete
            v-model="saleHeader.payment_account_id"
            :items="paymentAccounts"
            item-title="name"
            item-value="id"
            placeholder="Cash / Bank / Mobile"
            variant="outlined"
            density="comfortable"
            clearable
            :loading="loadingAccounts"
          ></v-autocomplete>
        </div>
      </div>
    </div>

    <!-- Items Table -->
    <div class="bg-white rounded-2xl shadow-lg overflow-hidden">
      <table class="w-full">
        <thead class="bg-gradient-to-r from-indigo-100 to-purple-100 text-gray-700">
          <tr>
            <th class="p-4 text-left">Product</th>
            <th class="p-4 text-center">Available Stock</th>
            <th class="p-4 text-center">Unit</th>
            <th class="p-4 text-center">Unit Price (UGX)</th>
            <th class="p-4 text-center">Quantity</th>
            <th class="p-4 text-center">Total (UGX)</th>
            <th class="p-4 text-center">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in saleItems" :key="index" class="border-b hover:bg-indigo-50 transition">
            <!-- Product Search + Selected Product Label -->
            <td class="p-4">
              <div class="space-y-2">
                <!-- Autocomplete -->
                <v-autocomplete
                  v-model="item.selectedProductObj"
                  :items="item.productSearchResults"
                  item-title="display_text"
                  item-value="id"
                  placeholder="Search product..."
                  variant="outlined"
                  density="comfortable"
                  clearable
                  hide-details
                  :loading="item.loadingProduct"
                  @update:search="query => searchProduct(query, index)"
                  @update:model-value="id => selectProduct(id, index)"
                >
                  <!-- Dropdown items -->
                  <template v-slot:item="{ props, item }">
                    <v-list-item v-bind="props">
                      <template v-slot:title>
                        <span class="font-medium">{{ item.raw.id }} - {{ item.raw.name }}</span>
                      </template>
                      <template v-slot:subtitle>
                        Stock: {{ item.raw.quantity.toFixed(2) }} base units
                      </template>
                    </v-list-item>
                  </template>

                  <!-- Selected shows ID - Name -->
                  <template v-slot:selection="{ item }">
                    <span class="font-medium text-indigo-700">
                      {{ item.raw.id }} - {{ item.raw.name }}
                    </span>
                  </template>
                </v-autocomplete>

                <!-- Selected Product Name Label -->
                <div v-if="item.product_name" class="text-sm font-semibold text-gray-800 bg-indigo-50 px-3 py-1 rounded-lg">
                  Selected: {{ item.product_name }}
                </div>
              </div>
            </td>

            <!-- Stock in Selected Unit -->
            <td class="p-4 text-center font-medium">
              {{ item.available_in_unit ? item.available_in_unit.toFixed(3) : '0.000' }}
            </td>

            <!-- Unit Select -->
            <td class="p-4">
              <v-select
                v-model="item.unit_id"
                :items="item.units"
                item-title="unit_name"
                item-value="id"
                placeholder="Select unit"
                variant="outlined"
                density="comfortable"
                hide-details
                :disabled="!item.product_id"
                @update:model-value="() => updateUnitPriceAndStock(index)"
              ></v-select>
            </td>

            <!-- Unit Price -->
            <td class="p-4 text-right font-semibold text-green-700">
              {{ formatPrice(item.unit_price) }}
            </td>

            <!-- Quantity -->
            <td class="p-4">
              <input
                type="number"
                v-model.number="item.quantity"
                @input="calculateLineTotal(index)"
                min="0"
                :max="item.available_in_unit"
                step="0.01"
                placeholder="0"
                class="w-full text-center border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
              />
            </td>

            <!-- Line Total -->
            <td class="p-4 text-right font-bold text-indigo-700 text-lg">
              {{ formatPrice(item.line_total) }}
            </td>

            <!-- Remove -->
            <td class="p-4 text-center">
              <button
                @click="removeItem(index)"
                class="w-10 h-10 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center transition shadow"
              >
                ✕
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Add Row & Totals -->
      <div class="p-6 bg-gradient-to-r from-indigo-50 to-purple-50 flex justify-between items-center">
        <button
          @click="addItemRow"
          class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl shadow-lg transition transform hover:scale-105"
        >
          + Add Item
        </button>

        <div class="text-right">
          <div class="text-2xl font-bold text-gray-800">
            Grand Total: <span class="text-indigo-700">{{ formatPrice(grandTotal) }}</span>
          </div>
          <div class="text-lg text-gray-600 mt-2">
            Amount Paid: <span class="font-bold">{{ formatPrice(saleHeader.amount_paid) }}</span>
          </div>
          <div class="text-xl font-bold text-orange-600 mt-1">
            Balance: {{ formatPrice(grandTotal - saleHeader.amount_paid) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Save Button -->
    <div class="mt-8 text-right">
      <button
        @click="saveSale"
        :disabled="saving || saleItems.length === 0"
        class="px-10 py-4 bg-green-600 hover:bg-green-700 text-white text-xl font-bold rounded-2xl shadow-2xl transition transform hover:scale-105 disabled:opacity-50"
      >
        {{ saving ? 'Saving Sale...' : 'Complete Sale' }}
      </button>
    </div>

    <!-- Notification -->
    <div v-if="notification" class="fixed bottom-8 right-8 bg-gray-900 text-white px-8 py-4 rounded-2xl shadow-2xl text-lg z-50 animate-pulse">
      {{ notification }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import debounce from 'lodash.debounce'
import api from '../api'

// Header
const saleHeader = ref({
  sale_date: new Date().toISOString().slice(0, 10),
  customer_id: 1,
  amount_paid: 0,
  memo: '',
  payment_account_id: null
})

// Items
const saleItems = ref([])

// Data
const customers = ref([])
const paymentAccounts = ref([])
const loadingCustomers = ref(false)
const loadingAccounts = ref(false)
const saving = ref(false)
const notification = ref('')

// Grand Total
const grandTotal = computed(() => {
  return saleItems.value.reduce((sum, item) => sum + (item.line_total || 0), 0)
})

// Format Price
const formatPrice = (val) => {
  const value = Number(val) || 0
  return new Intl.NumberFormat('en-UG', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

// Fetch Customers
const fetchCustomers = async () => {
  loadingCustomers.value = true
  try {
    const res = await api.get('/customer/')
    customers.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loadingCustomers.value = false
  }
}

// Fetch Payment Accounts
const fetchPaymentAccounts = async () => {
  loadingAccounts.value = true
  try {
    const res = await api.get('/accounts/?type=ASSET')
    paymentAccounts.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loadingAccounts.value = false
  }
}

// Product Search
const searchProduct = debounce(async (query, index) => {
  const item = saleItems.value[index]
  if (!query || query.trim().length < 2) {
    item.productSearchResults = []
    return
  }
  item.loadingProduct = true
  try {
    const res = await api.get('/inventory/products/search', { params: { name: query } })
    item.productSearchResults = res.data.map(p => ({
      ...p,
      display_text: `${p.id} - ${p.name}`
    }))
  } catch (err) {
    console.error(err)
  } finally {
    item.loadingProduct = false
  }
}, 300)

// Select Product
const selectProduct = (productId, index) => {
  const item = saleItems.value[index]
  const product = item.productSearchResults.find(p => p.id === productId)
  if (!product) return

  item.product_id = product.id
  item.selectedProductObj = product
  // selectedProductObj: null,

  item.product_name = product.name
  item.units = product.units || []
  item.unit_id = null
  item.unit_price = 0
  item.available_in_unit = product.quantity || 0
  item.quantity =  0
  item.line_total = 0
  item.stock_base = product.quantity

  item.productSearchResults = []
}

// Update unit price and stock
const updateUnitPriceAndStock = (index) => {
  const item = saleItems.value[index]
  const selectedUnit = item.units.find(u => u.id === item.unit_id)
  if (selectedUnit) {
    item.unit_price = selectedUnit.retail_price || 0
    item.available_in_unit = item.stock_base / selectedUnit.conversion_quantity
    calculateLineTotal(index)
  }
}

// Calculate line total
const calculateLineTotal = (index) => {
  const item = saleItems.value[index]
  item.line_total = (item.quantity || 0) * (item.unit_price || 0)
}

// Add row
const addItemRow = () => {
  saleItems.value.push({
    product_id: null,
    product_name: '',
    units: [],
    unit_id: null,
    unit_price: 0,
    quantity: 0,
    line_total: 0,
    stock_base: 0,
    available_in_unit: 0,
    productSearchResults: [],
    selectedProductObj: null,
    loadingProduct: false
  })
}

// Remove row
const removeItem = (index) => {
  saleItems.value.splice(index, 1)
}

// Save Sale
const saveSale = async () => {
  if (!saleHeader.value.customer_id) return alert('Please select a customer')
  if (saleItems.value.length === 0) return alert('Add at least one item')
  if (saleHeader.value.amount_paid > 0 && !saleHeader.value.payment_account_id) {
    return alert('Select payment account when amount paid')
  }

  for (let i = 0; i < saleItems.value.length; i++) {
    const item = saleItems.value[i]
    if (!item.product_id) return alert(`Row ${i + 1}: Select a product`)
    if (!item.unit_id) return alert(`Row ${i + 1}: Select a unit`)
    if (!item.quantity || item.quantity <= 0) return alert(`Row ${i + 1}: Enter quantity > 0`)
    if (item.quantity > item.available_in_unit) return alert(`Row ${i + 1}: Not enough stock`)
  }

  const payload = {
    sale_date: saleHeader.value.sale_date,
    customer_id: saleHeader.value.customer_id,
    amount_paid: saleHeader.value.amount_paid || 0,
    payment_account_id: saleHeader.value.payment_account_id || null,
    memo: saleHeader.value.memo || '',
    items: saleItems.value.map(item => ({
      product_id: item.product_id,
      unit_id: item.unit_id,
      quantity: item.quantity
    }))
  }

  saving.value = true
  try {
    const res = await api.post('/sales/', payload)
    notification.value = `Sale #${res.data.sale_id} saved successfully!`
    resetForm()
  } catch (err) {
    console.error(err)
    notification.value = err.response?.data?.error || 'Failed to save sale'
  } finally {
    saving.value = false
    setTimeout(() => notification.value = '', 5000)
  }
}

// Reset form
const resetForm = () => {
  saleHeader.value = {
    sale_date: new Date().toISOString().slice(0, 10),
    customer_id: 1,
    amount_paid: 0,
    memo: '',
    payment_account_id: null
  }
  saleItems.value = []
  addItemRow()
}

// Init
onMounted(() => {
  fetchCustomers()
  fetchPaymentAccounts()
  addItemRow()
})
</script>

<style scoped>
/* Your custom styles */
</style>
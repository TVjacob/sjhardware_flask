<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Inventory Management</h1>

    <!-- Tabs -->
    <div class="mb-6 flex gap-4">
      <button @click="activeTab='products'" :class="tabClass('products')">Products</button>
      <button @click="activeTab='categories'" :class="tabClass('categories')">Categories</button>
    </div>

    <!-- ---------------- Products Tab ---------------- -->
    <div v-if="activeTab==='products'">
      <!-- Add/Edit Product Form -->
      <form @submit.prevent="submitProduct" class="mb-4 flex flex-wrap gap-2">
        <input v-model="productForm.name" placeholder="Product Name" class="border p-2 rounded" required />
        <input v-model="productForm.sku" placeholder="SKU" class="border p-2 rounded" required />
        <input v-model.number="productForm.price" type="number" placeholder="Price" class="border p-2 rounded" />
        <select v-model="productForm.category_id" class="border p-2 rounded">
          <option value="">Select Category</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
        <button class="bg-blue-500 text-white px-4 py-2 rounded">
          {{ editingProduct ? 'Update' : 'Add' }} Product
        </button>
        <button v-if="editingProduct" type="button" @click="cancelProductEdit" class="bg-gray-500 text-white px-4 py-2 rounded">Cancel</button>
      </form>

      <!-- Search Product -->
      <div class="mb-4 flex gap-2 flex-wrap">
        <input v-model="searchQuery" placeholder="Search by name or SKU" class="border p-2 rounded" />
        <button @click="searchProducts" class="bg-green-500 text-white px-4 py-2 rounded">Search</button>
        <button @click="fetchProducts" class="bg-gray-300 px-4 py-2 rounded">Reset</button>
        <button @click="exportExcel" class="bg-yellow-500 text-white px-4 py-2 rounded">Export Excel</button>
        <button @click="exportPDF" class="bg-red-500 text-white px-4 py-2 rounded">Export PDF</button>
      </div>

      <!-- Products Table -->
      <table class="min-w-full bg-white border">
        <thead>
          <tr>
            <th class="p-2 border">ID</th>
            <th class="p-2 border">Name</th>
            <th class="p-2 border">SKU</th>
            <th class="p-2 border">Price</th>
            <th class="p-2 border">Category</th>
            <th class="p-2 border">Stock Qty</th>
            <th class="p-2 border">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.id">
            <td class="p-2 border">{{ product.id }}</td>
            <td class="p-2 border">{{ product.name }}</td>
            <td class="p-2 border">{{ product.sku }}</td>
            <td class="p-2 border">{{ product.price }}</td>
            
            <td class="p-2 border">{{ getCategoryName(product.category_id) }}</td>
            <td class="p-2 border">{{ product.quantity }}</td>

            <td class="p-2 border flex gap-2">
              <button @click="editProduct(product)" class="bg-blue-400 text-white px-2 py-1 rounded">Edit</button>
              <button @click="deleteProduct(product.id)" class="bg-red-500 text-white px-2 py-1 rounded">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ---------------- Categories Tab ---------------- -->
    <div v-if="activeTab==='categories'">
      <!-- Add/Edit Category Form -->
      <form @submit.prevent="submitCategory" class="flex gap-2 flex-wrap mb-4">
        <input v-model="categoryForm.name" placeholder="Category Name" class="border p-2 rounded" required />
        <button class="bg-indigo-500 text-white px-4 py-2 rounded">
          {{ editingCategory ? 'Update' : 'Add' }} Category
        </button>
        <button v-if="editingCategory" type="button" @click="cancelCategoryEdit" class="bg-gray-500 text-white px-4 py-2 rounded">Cancel</button>
      </form>

      <!-- Categories Table -->
      <table class="min-w-full bg-white border">
        <thead>
          <tr>
            <th class="p-2 border">ID</th>
            <th class="p-2 border">Name</th>
            <th class="p-2 border">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cat in categories" :key="cat.id">
            <td class="p-2 border">{{ cat.id }}</td>
            <td class="p-2 border">{{ cat.name }}</td>
            <td class="p-2 border flex gap-2">
              <button @click="editCategory(cat)" class="bg-blue-400 text-white px-2 py-1 rounded">Edit</button>
              <button @click="deleteCategory(cat.id)" class="bg-red-500 text-white px-2 py-1 rounded">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from '../api';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

export default {
  data() {
    return {
      activeTab: 'products', // default tab
      products: [],
      categories: [],
      productForm: { id: null, name: '', sku: '', price: 0, category_id: '' }, // removed quantity
      editingProduct: false,
      categoryForm: { id: null, name: '' },
      editingCategory: false,
      searchQuery: '',
    };
  },
  methods: {
    // Tab styling
    tabClass(tab) {
      return `px-4 py-2 rounded ${this.activeTab===tab?'bg-blue-500 text-white':'bg-gray-200'}`;
    },

    // --- Categories ---
    async fetchCategories() {
      const res = await api.get('/inventory/categories');
      this.categories = res.data;
    },
    async submitCategory() {
      if (this.editingCategory) {
        await api.put(`/inventory/categories/${this.categoryForm.id}`, this.categoryForm);
      } else {
        await api.post('/inventory/categories', this.categoryForm);
      }
      this.categoryForm = { id: null, name: '' };
      this.editingCategory = false;
      this.fetchCategories();
    },
    editCategory(cat) {
      this.categoryForm = { ...cat };
      this.editingCategory = true;
    },
    cancelCategoryEdit() {
      this.categoryForm = { id: null, name: '' };
      this.editingCategory = false;
    },
    async deleteCategory(id) {
      if (confirm('Are you sure you want to delete this category?')) {
        await api.delete(`/inventory/categories/${id}`);
        this.fetchCategories();
      }
    },

    // --- Products ---
    async fetchProducts() {
      const res = await api.get('/inventory/products');
      this.products = res.data;
    },
    async submitProduct() {
      if (this.editingProduct) {
        await api.put(`/inventory/products/${this.productForm.id}`, this.productForm);
      } else {
        await api.post('/inventory/products', this.productForm);
      }
      this.productForm = { id: null, name: '', sku: '', price: 0, category_id: '' };
      this.editingProduct = false;
      this.fetchProducts();
    },
    editProduct(product) {
      this.productForm = { ...product };
      this.editingProduct = true;
    },
    cancelProductEdit() {
      this.productForm = { id: null, name: '', sku: '', price: 0, category_id: '' };
      this.editingProduct = false;
    },
    async deleteProduct(id) {
      if (confirm('Are you sure you want to delete this product?')) {
        await api.delete(`/inventory/products/${id}`);
        this.fetchProducts();
      }
    },

    // --- Search ---
    async searchProducts() {
      const res = await api.get('/inventory/products/search', { params: { name: this.searchQuery, sku: this.searchQuery } });
      this.products = res.data;
    },

    // --- Excel / PDF ---
    exportExcel() {
      const ws = XLSX.utils.json_to_sheet(this.products);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Products');
      XLSX.writeFile(wb, 'products.xlsx');
    },
    exportPDF() {
      const doc = new jsPDF();
      doc.autoTable({
        head: [['ID', 'Name', 'SKU', 'Price', 'Category' ,'Stock qty']],
        body: this.products.map(p => [p.id, p.name, p.sku, p.price, this.getCategoryName(p.category_id),p.quantity]),
      });
      doc.save('products.pdf');
    },

    getCategoryName(catId) {
      const cat = this.categories.find(c => c.id === catId);
      return cat ? cat.name : '';
    },
  },
  mounted() {
    this.fetchCategories();
    this.fetchProducts();
  },
};
</script>

<template>
    <div class="p-6">
      <h1 class="text-2xl font-bold mb-4">Customer Management</h1>
  
      <!-- Add/Edit Customer Form -->
      <div class="mb-6">
        <h2 class="font-bold mb-2">Add / Edit Customer</h2>
        <form @submit.prevent="submitCustomer" class="flex gap-2 flex-wrap mb-4">
          <input v-model="customerForm.name" placeholder="Customer Name" class="border p-2 rounded" required />
          <input v-model="customerForm.phone" placeholder="Phone" class="border p-2 rounded" />
          <input v-model="customerForm.email" type="email" placeholder="Email" class="border p-2 rounded" />
          <input v-model="customerForm.address" placeholder="Address" class="border p-2 rounded" />
          <button class="bg-indigo-500 text-white px-4 py-2 rounded">
            {{ editingCustomer ? 'Update' : 'Add' }} Customer
          </button>
          <button v-if="editingCustomer" type="button" @click="cancelEdit" class="bg-gray-500 text-white px-4 py-2 rounded">Cancel</button>
        </form>
      </div>
  
      <!-- Search Customers -->
      <div class="mb-4 flex gap-2 flex-wrap">
        <input v-model="searchQuery" placeholder="Search by name, phone, or email" class="border p-2 rounded" />
        <button @click="searchCustomers" class="bg-green-500 text-white px-4 py-2 rounded">Search</button>
        <button @click="fetchCustomers" class="bg-gray-300 px-4 py-2 rounded">Reset</button>
        <button @click="exportExcel" class="bg-yellow-500 text-white px-4 py-2 rounded">Export Excel</button>
        <button @click="exportPDF" class="bg-red-500 text-white px-4 py-2 rounded">Export PDF</button>
      </div>
  
      <!-- Customers Table -->
      <table class="min-w-full bg-white border">
        <thead>
          <tr>
            <th class="p-2 border">ID</th>
            <th class="p-2 border">Name</th>
            <th class="p-2 border">Phone</th>
            <th class="p-2 border">Email</th>
            <th class="p-2 border">Address</th>
            <th class="p-2 border">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="customer in customers" :key="customer.id">
            <td class="p-2 border">{{ customer.id }}</td>
            <td class="p-2 border">{{ customer.name }}</td>
            <td class="p-2 border">{{ customer.phone }}</td>
            <td class="p-2 border">{{ customer.email }}</td>
            <td class="p-2 border">{{ customer.address }}</td>
            <td class="p-2 border flex gap-2">
              <button @click="editCustomer(customer)" class="bg-blue-400 text-white px-2 py-1 rounded">Edit</button>
              <button @click="deleteCustomer(customer.id)" class="bg-red-500 text-white px-2 py-1 rounded">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
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
        customers: [],
        customerForm: { id: null, name: '', phone: '', email: '', address: '' },
        editingCustomer: false,
        searchQuery: ''
      };
    },
    methods: {
      async fetchCustomers() {
        const res = await api.get('/customer/');
        this.customers = res.data;
      },
      async submitCustomer() {
        if (this.editingCustomer) {
          await api.put(`/customer/${this.customerForm.id}`, this.customerForm);
        } else {
          await api.post('/customer/', this.customerForm);
        }
        this.customerForm = { id: null, name: '', phone: '', email: '', address: '' };
        this.editingCustomer = false;
        this.fetchCustomers();
      },
      editCustomer(customer) {
        this.customerForm = { ...customer };
        this.editingCustomer = true;
      },
      cancelEdit() {
        this.customerForm = { id: null, name: '', phone: '', email: '', address: '' };
        this.editingCustomer = false;
      },
      async deleteCustomer(id) {
        if (confirm('Are you sure you want to delete this customer?')) {
          await api.delete(`/customer/${id}`);
          this.fetchCustomers();
        }
      },
      async searchCustomers() {
        const res = await api.get('/customer/search', { params: { name: this.searchQuery, phone: this.searchQuery, email: this.searchQuery } });
        this.customers = res.data;
      },
      exportExcel() {
        const ws = XLSX.utils.json_to_sheet(this.customers);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'Customers');
        XLSX.writeFile(wb, 'customers.xlsx');
      },
      exportPDF() {
        const doc = new jsPDF();
        doc.autoTable({
          head: [['ID', 'Name', 'Phone', 'Email', 'Address']],
          body: this.customers.map(c => [c.id, c.name, c.phone, c.email, c.address]),
        });
        doc.save('customers.pdf');
      }
    },
    mounted() {
      this.fetchCustomers();
    }
  };
  </script>
  
<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Expenses Management</h1>

    <!-- Add/Edit Expense Form -->
    <div class="mb-6">
      <h2 class="font-bold mb-2">{{ editingExpense ? 'Edit Expense' : 'Add Expense' }}</h2>
      <form @submit.prevent="submitExpense" class="flex gap-2 flex-wrap mb-4">
        <input v-model="expenseForm.description" placeholder="Description" class="border p-2 rounded w-full md:w-auto" required />
        <input v-model.number="expenseForm.amount" type="number" placeholder="Amount" class="border p-2 rounded" required />
        <input v-model="expenseForm.category" placeholder="Category" class="border p-2 rounded" />
        <input v-model="expenseForm.expense_date" type="date" class="border p-2 rounded" />
        <button class="bg-indigo-500 text-white px-4 py-2 rounded">
          {{ editingExpense ? 'Update' : 'Add' }}
        </button>
        <button v-if="editingExpense" type="button" @click="cancelEdit" class="bg-gray-500 text-white px-4 py-2 rounded">Cancel</button>
      </form>
    </div>

    <!-- Search & Export -->
    <div class="mb-4 flex gap-2 flex-wrap">
      <input v-model="searchQuery" placeholder="Search description or category" class="border p-2 rounded" />
      <button @click="searchExpenses" class="bg-green-500 text-white px-4 py-2 rounded">Search</button>
      <button @click="fetchExpenses" class="bg-gray-300 px-4 py-2 rounded">Reset</button>
      <button @click="exportExcel" class="bg-yellow-500 text-white px-4 py-2 rounded">Export Excel</button>
      <button @click="exportPDF" class="bg-red-500 text-white px-4 py-2 rounded">Export PDF</button>
    </div>

    <!-- Expenses Table -->
    <table class="min-w-full bg-white border">
      <thead>
        <tr>
          <th class="p-2 border">ID</th>
          <th class="p-2 border">Description</th>
          <th class="p-2 border">Amount</th>
          <th class="p-2 border">Category</th>
          <th class="p-2 border">Expense Date</th>
          <th class="p-2 border">Transaction No</th>
          <th class="p-2 border">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="expense in expenses" :key="expense.id">
          <td class="p-2 border">{{ expense.id }}</td>
          <td class="p-2 border">{{ expense.description }}</td>
          <td class="p-2 border">{{ expense.amount.toFixed(2) }}</td>
          <td class="p-2 border">{{ expense.category }}</td>
          <td class="p-2 border">{{ formatDate(expense.expense_date) }}</td>
          <td class="p-2 border">{{ expense.transaction_no }}</td>
          <td class="p-2 border flex gap-2">
            <button @click="editExpense(expense)" class="bg-blue-400 text-white px-2 py-1 rounded">Edit</button>
            <button @click="deleteExpense(expense.id)" class="bg-red-500 text-white px-2 py-1 rounded">Delete</button>
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
      expenses: [],
      expenseForm: {
        id: null,
        description: '',
        amount: 0,
        category: '',
        expense_date: ''
      },
      editingExpense: false,
      searchQuery: ''
    };
  },
  methods: {
    async fetchExpenses() {
      const res = await api.get('/expenses/');
      this.expenses = res.data;
    },
    async submitExpense() {
      if (this.editingExpense) {
        await api.put(`/expenses/${this.expenseForm.id}`, this.expenseForm);
      } else {
        await api.post('/expenses/', this.expenseForm);
      }
      this.resetForm();
      this.fetchExpenses();
    },
    editExpense(expense) {
      this.expenseForm = { ...expense, expense_date: expense.expense_date.split('T')[0] };
      this.editingExpense = true;
    },
    cancelEdit() {
      this.resetForm();
    },
    resetForm() {
      this.expenseForm = { id: null, description: '', amount: 0, category: '', expense_date: '' };
      this.editingExpense = false;
    },
    async deleteExpense(id) {
      if (confirm('Are you sure you want to delete this expense?')) {
        await api.delete(`/expenses/${id}`);
        this.fetchExpenses();
      }
    },
    async searchExpenses() {
      const res = await api.get('/expenses/');
      this.expenses = res.data.filter(e =>
        e.description.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        (e.category && e.category.toLowerCase().includes(this.searchQuery.toLowerCase()))
      );
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      const d = new Date(dateStr);
      return d.toLocaleDateString();
    },
    exportExcel() {
      const ws = XLSX.utils.json_to_sheet(this.expenses);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Expenses');
      XLSX.writeFile(wb, 'expenses.xlsx');
    },
    exportPDF() {
      const doc = new jsPDF();
      doc.autoTable({
        head: [['ID', 'Description', 'Amount', 'Category', 'Expense Date', 'Transaction No']],
        body: this.expenses.map(e => [e.id, e.description, e.amount, e.category, this.formatDate(e.expense_date), e.transaction_no])
      });
      doc.save('expenses.pdf');
    }
  },
  mounted() {
    this.fetchExpenses();
  }
};
</script>

<style scoped>
/* Optional: make table scrollable on smaller screens */
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  text-align: left;
}
</style>

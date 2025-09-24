<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Expenses Management</h1>

    <!-- Button to open modal -->
    <button
      @click="showModal = true"
      class="bg-indigo-500 text-white px-4 py-2 rounded mb-4"
    >
      + Add Expense
    </button>

    <!-- Grand Total -->
    <div class="mb-4 p-4 bg-gray-100 rounded shadow">
      <h2 class="text-lg font-bold">
        Grand Total Paid:
        <span class="text-green-600">{{ grandTotal.toFixed(2) }}</span>
      </h2>
    </div>

    <!-- Search & Export -->
    <div class="mb-4 flex gap-2 flex-wrap">
      <input
        v-model="searchQuery"
        placeholder="Search description or reference"
        class="border p-2 rounded"
      />
      <button @click="searchExpenses" class="bg-green-500 text-white px-4 py-2 rounded">Search</button>
      <button @click="fetchExpenses" class="bg-gray-300 px-4 py-2 rounded">Reset</button>
      <button @click="exportExcel" class="bg-yellow-500 text-white px-4 py-2 rounded">Export Excel</button>
      <button @click="exportPDF" class="bg-red-500 text-white px-4 py-2 rounded">Export PDF</button>
    </div>

    <!-- Expenses Table -->
    <table class="min-w-full bg-white border">
      <thead>
        <tr>
          <th class="p-2 border"></th>
          <th class="p-2 border">ID</th>
          <th class="p-2 border">Description</th>
          <th class="p-2 border">Total Amount</th>
          <th class="p-2 border">Reference</th>
          <th class="p-2 border">Expense Date</th>
          <th class="p-2 border">Transaction No</th>
          <th class="p-2 border">Actions</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="expense in expenses" :key="expense.id">
          <!-- Main Expense Row -->
          <tr>
            <td class="p-2 border text-center">
              <button
                @click="toggleExpand(expense.id)"
                class="text-blue-600 font-bold"
              >
                {{ expandedRows.includes(expense.id) ? '-' : '+' }}
              </button>
            </td>
            <td class="p-2 border">{{ expense.id }}</td>
            <td class="p-2 border">{{ expense.description }}</td>
            <td class="p-2 border">{{ expense.total_amount.toFixed(2) }}</td>
            <td class="p-2 border">{{ expense.reference }}</td>
            <td class="p-2 border">{{ formatDate(expense.expense_date) }}</td>
            <td class="p-2 border">{{ expense.transaction_no }}</td>
            <td class="p-2 border flex gap-2">
              <button @click="editExpense(expense)" class="bg-blue-400 text-white px-2 py-1 rounded">Edit</button>
              <button @click="deleteExpense(expense.id)" class="bg-red-500 text-white px-2 py-1 rounded">Delete</button>
            </td>
          </tr>

          <!-- Expanded Details Row -->
          <tr v-if="expandedRows.includes(expense.id)">
            <td colspan="8" class="p-4 bg-gray-50 border">
              <h3 class="font-semibold mb-2">Expense Items</h3>
              <table class="w-full border text-sm">
                <thead>
                  <tr>
                    <th class="p-2 border">Account</th>
                    <th class="p-2 border">Item Name</th>
                    <th class="p-2 border">Description</th>
                    <th class="p-2 border">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in expense.items" :key="item.id">
                    <td class="p-2 border">{{ getAccountName(item.account_id) }}</td>
                    <td class="p-2 border">{{ item.item_name }}</td>
                    <td class="p-2 border">{{ item.description }}</td>
                    <td class="p-2 border">{{ item.amount.toFixed(2) }}</td>
                  </tr>
                </tbody>
              </table>
            </td>
          </tr>
        </template>
      </tbody>
    </table>

    <!-- Popup Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl relative">
        <h2 class="text-xl font-bold mb-4">
          {{ editingExpense ? 'Edit Expense' : 'Add Expense' }}
        </h2>

        <!-- Close Button -->
        <button
          @click="closeModal"
          class="absolute top-2 right-2 text-gray-600 hover:text-gray-800"
        >
          ✖
        </button>

        <!-- Expense Header -->
        <div class="grid grid-cols-2 gap-4 mb-4">
          <input
            v-model="expenseForm.description"
            placeholder="Expense Description"
            class="border p-2 rounded"
            required
          />
          <input
            v-model="expenseForm.reference"
            placeholder="Reference"
            class="border p-2 rounded"
          />
          <select
            v-model="expenseForm.payment_account_id"
            class="border p-2 rounded"
            required
          >
            <option value="" disabled>Select Payment Account</option>
            <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
              {{ acc.name }}
            </option>
          </select>
          <input
            v-model="expenseForm.expense_date"
            type="date"
            class="border p-2 rounded"
          />
        </div>

        <!-- Expense Items Section -->
        <h3 class="font-bold mb-2">Expense Items</h3>
        <div v-for="(item, index) in expenseForm.items" :key="index" class="grid grid-cols-5 gap-2 mb-2">
          <select
            v-model="item.account_id"
            class="border p-2 rounded"
            required
          >
            <option value="" disabled>Select Expense Account</option>
            <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
              {{ acc.name }}
            </option>
          </select>
          <input
            v-model="item.item_name"
            placeholder="Item Name"
            class="border p-2 rounded"
            required
          />
          <input
            v-model="item.description"
            placeholder="Item Description"
            class="border p-2 rounded"
          />
          <input
            v-model.number="item.amount"
            type="number"
            placeholder="Amount"
            class="border p-2 rounded"
            required
          />
          <button
            type="button"
            @click="removeItem(index)"
            class="bg-red-500 text-white px-2 py-1 rounded"
          >
            ✖
          </button>
        </div>

        <button
          type="button"
          @click="addItem"
          class="bg-gray-300 px-4 py-2 rounded mb-4"
        >
          + Add Item
        </button>

        <!-- Amount Paid (Auto-calculated total of expense items) -->
        <div class="mb-4">
          <label class="block text-sm font-bold mb-1">Amount Paid</label>
          <input
            type="number"
            :value="amountPaid.toFixed(2)"
            class="border p-2 rounded w-full bg-gray-100"
            disabled
          />
        </div>

        <!-- Submit Button -->
        <div class="flex justify-end">
          <button
            @click="submitExpense"
            class="bg-indigo-500 text-white px-6 py-2 rounded"
          >
            {{ editingExpense ? 'Update Expense' : 'Create Expense' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../api";
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";

export default {
  data() {
    return {
      expenses: [],
      accounts: [],
      searchQuery: "",
      showModal: false,
      editingExpense: false,
      expandedRows: [],
      expenseForm: {
        id: null,
        description: "",
        payment_account_id: "",
        expense_date: "",
        reference: "",
        items: [{ account_id: "", item_name: "", description: "", amount: 0 }],
      },
    };
  },
  computed: {
    // Calculate grand total of all expenses
    grandTotal() {
      return this.expenses.reduce((sum, expense) => sum + (expense.total_amount || 0), 0);
    },
    // Calculate total of items in the current expense form
    amountPaid() {
      return this.expenseForm.items.reduce((total, item) => total + (item.amount || 0), 0);
    },
  },
  methods: {
    async fetchExpenses() {
      const res = await api.get("/expenses/");
      this.expenses = res.data;
    },
    async fetchAccounts() {
      const res = await api.get("/accounts/");
      this.accounts = res.data;
    },
    addItem() {
      this.expenseForm.items.push({ account_id: "", item_name: "", description: "", amount: 0 });
    },
    removeItem(index) {
      this.expenseForm.items.splice(index, 1);
    },
    async submitExpense() {
      try {
        if (this.editingExpense) {
          await api.put(`/expenses/${this.expenseForm.id}`, this.expenseForm);
        } else {
          await api.post("/expenses/", this.expenseForm);
        }
        this.closeModal();
        this.fetchExpenses();
      } catch (err) {
        alert("Error submitting expense: " + (err.response?.data?.error || err.message));
      }
    },
    editExpense(expense) {
      this.expenseForm = {
        id: expense.id,
        description: expense.description,
        payment_account_id: expense.payment_account_id,
        expense_date: expense.expense_date.split("T")[0],
        reference: expense.reference,
        items: expense.items || [],
      };
      this.editingExpense = true;
      this.showModal = true;
    },
    closeModal() {
      this.resetForm();
      this.showModal = false;
    },
    resetForm() {
      this.expenseForm = {
        id: null,
        description: "",
        payment_account_id: "",
        expense_date: "",
        reference: "",
        items: [{ account_id: "", item_name: "", description: "", amount: 0 }],
      };
      this.editingExpense = false;
    },
    async deleteExpense(id) {
      if (confirm("Are you sure you want to delete this expense?")) {
        await api.delete(`/expenses/${id}`);
        this.fetchExpenses();
      }
    },
    async searchExpenses() {
      const res = await api.get("/expenses/");
      this.expenses = res.data.filter((e) =>
        e.description.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        (e.reference && e.reference.toLowerCase().includes(this.searchQuery.toLowerCase()))
      );
    },
    formatDate(dateStr) {
      if (!dateStr) return "";
      const d = new Date(dateStr);
      return d.toLocaleDateString();
    },
    toggleExpand(id) {
      if (this.expandedRows.includes(id)) {
        this.expandedRows = this.expandedRows.filter(rowId => rowId !== id);
      } else {
        this.expandedRows.push(id);
      }
    },
    getAccountName(account_id) {
      const account = this.accounts.find(a => a.id === account_id);
      return account ? account.name : "Unknown";
    },
    exportExcel() {
      const ws = XLSX.utils.json_to_sheet(this.expenses);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "Expenses");
      XLSX.writeFile(wb, "expenses.xlsx");
    },
    exportPDF() {
      const doc = new jsPDF();
      doc.autoTable({
        head: [["ID", "Description", "Total Amount", "Reference", "Expense Date", "Transaction No"]],
        body: this.expenses.map((e) => [
          e.id,
          e.description,
          e.total_amount,
          e.reference,
          this.formatDate(e.expense_date),
          e.transaction_no,
        ]),
      });
      doc.save("expenses.pdf");
    },
  },
  mounted() {
    this.fetchExpenses();
    this.fetchAccounts();
  },
};
</script>

<style scoped>
/* Smooth popup animation */
.fixed {
  animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Suppliers</h1>

    <!-- Add/Edit Supplier Form -->
    <form @submit.prevent="submitSupplier" class="mb-4 flex flex-wrap gap-2">
      <input
        v-model="supplierForm.name"
        placeholder="Supplier Name"
        class="border p-2 rounded"
        required
      />
      <input
        v-model="supplierForm.contact"
        placeholder="Contact"
        class="border p-2 rounded"
      />
      <input
        v-model="supplierForm.email"
        placeholder="Email"
        class="border p-2 rounded"
      />
      <button class="bg-blue-500 text-white px-4 py-2 rounded">
        {{ editing ? 'Update' : 'Add' }} Supplier
      </button>
      <button
        v-if="editing"
        type="button"
        @click="cancelEdit"
        class="bg-gray-500 text-white px-4 py-2 rounded"
      >
        Cancel
      </button>
    </form>

    <!-- Search Supplier -->
    <div class="mb-4 flex gap-2">
      <input
        v-model="searchQuery"
        placeholder="Search by name or contact"
        class="border p-2 rounded"
      />
      <button
        @click="searchSuppliers"
        class="bg-green-500 text-white px-4 py-2 rounded"
      >
        Search
      </button>
      <button @click="fetchSuppliers" class="bg-gray-300 px-4 py-2 rounded">
        Reset
      </button>
    </div>

    <!-- Suppliers Table -->
    <table class="min-w-full bg-white border">
      <thead>
        <tr>
          <th class="p-2 border">ID</th>
          <th class="p-2 border">Name</th>
          <th class="p-2 border">Contact</th>
          <th class="p-2 border">Email</th>
          <th class="p-2 border">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="supplier in suppliers" :key="supplier.id">
          <td class="p-2 border">{{ supplier.id }}</td>
          <td class="p-2 border">{{ supplier.name }}</td>
          <td class="p-2 border">{{ supplier.contact }}</td>
          <td class="p-2 border">{{ supplier.email }}</td>
          <td class="p-2 border flex gap-2">
            <button
              @click="editSupplier(supplier)"
              class="bg-blue-400 text-white px-2 py-1 rounded"
            >
              Edit
            </button>
            <button
              @click="deleteSupplier(supplier.id)"
              class="bg-red-500 text-white px-2 py-1 rounded"
            >
              Delete
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import api from "../api";

export default {
  data() {
    return {
      suppliers: [],
      supplierForm: { id: null, name: "", contact: "", email: "" },
      editing: false,
      searchQuery: "",
    };
  },
  methods: {
    async fetchSuppliers() {
      try {
        const res = await api.get("/suppliers/");
        this.suppliers = res.data;
      } catch (err) {
        console.error("❌ Error fetching suppliers:", err);
        alert("Failed to fetch suppliers. Please check your connection or try again.");
      }
    },

    async submitSupplier() {
      try {
        if (this.editing) {
          await api.put(`/suppliers/${this.supplierForm.id}`, this.supplierForm);
          alert("✅ Supplier updated successfully!");
        } else {
          await api.post("/suppliers/", this.supplierForm);
          alert("✅ Supplier added successfully!");
        }
        this.supplierForm = { id: null, name: "", contact: "", email: "" };
        this.editing = false;
        this.fetchSuppliers();
      } catch (err) {
        console.error("❌ Error submitting supplier:", err);
        alert("Failed to save supplier. Please verify inputs or try again.");
      }
    },

    editSupplier(supplier) {
      this.supplierForm = { ...supplier };
      this.editing = true;
    },

    cancelEdit() {
      this.supplierForm = { id: null, name: "", contact: "", email: "" };
      this.editing = false;
    },

    async deleteSupplier(id) {
      if (confirm("Are you sure you want to delete this supplier?")) {
        try {
          await api.delete(`/suppliers/${id}`);
          alert("🗑️ Supplier deleted successfully!");
          this.fetchSuppliers();
        } catch (err) {
          console.error("❌ Error deleting supplier:", err);
          alert("Failed to delete supplier. Please try again later.");
        }
      }
    },

    async searchSuppliers() {
      try {
        const res = await api.get("/suppliers");
        this.suppliers = res.data.filter(
          (s) =>
            s.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
            (s.contact && s.contact.includes(this.searchQuery))
        );
      } catch (err) {
        console.error("❌ Error searching suppliers:", err);
        alert("Search failed. Please try again.");
      }
    },
  },

  mounted() {
    this.fetchSuppliers();
  },
};
</script>

<style scoped>
button {
  transition: background 0.3s;
}
button:hover {
  opacity: 0.9;
}
</style>

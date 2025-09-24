<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6">{{ reportTitle }}</h1>

    <!-- Buttons -->
    <div class="mb-4 flex justify-between items-center">
      <div>
        <button @click="goBack" class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded mr-2">
          Back
        </button>
      </div>
      <div>
        <button @click="exportExcel" class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded mr-2">
          Export Excel
        </button>
        <button @click="exportPDF" class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded">
          Export PDF
        </button>
      </div>
    </div>

    <!-- Cashflow Summary Table -->
    <table class="min-w-full border border-gray-200 rounded shadow">
      <thead class="bg-gray-100">
        <tr>
          <th class="p-2 border-b text-left">Description</th>
          <th class="p-2 border-b text-left">Amount (UGX)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="p-2 border-b">Cash Inflow</td>
          <td class="p-2 border-b">{{ reportData.cash_inflow.toFixed(2) }}</td>
        </tr>
        <tr>
          <td class="p-2 border-b">Cash Outflow</td>
          <td class="p-2 border-b">{{ reportData.cash_outflow.toFixed(2) }}</td>
        </tr>
        <tr>
          <td class="p-2 border-b font-bold">Net Cash Flow</td>
          <td class="p-2 border-b font-bold">{{ reportData.net_cash_flow.toFixed(2) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/api'; // Axios instance
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

const reportData = ref({
  cash_inflow: 0,
  cash_outflow: 0,
  net_cash_flow: 0
});
const reportTitle = ref('Cashflows Summary');
const endpoint = ref('/reports/cash-flow');

// Fetch summary data
const fetchReport = async () => {
  try {
    const res = await api.get(endpoint.value);
    reportData.value = res.data;
  } catch (err) {
    console.error(`Error fetching ${reportTitle.value}:`, err);
  }
};

// Back button
const goBack = () => window.history.back();

// Export to Excel
const exportExcel = () => {
  const ws = XLSX.utils.json_to_sheet([
    { Description: 'Cash Inflow', Amount: reportData.value.cash_inflow },
    { Description: 'Cash Outflow', Amount: reportData.value.cash_outflow },
    { Description: 'Net Cash Flow', Amount: reportData.value.net_cash_flow }
  ]);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Cashflows');
  XLSX.writeFile(wb, 'Cashflows_Summary.xlsx');
};

// Export to PDF
const exportPDF = () => {
  const doc = new jsPDF();
  doc.text(reportTitle.value, 14, 20);
  const rows = [
    ['Cash Inflow', reportData.value.cash_inflow.toFixed(2)],
    ['Cash Outflow', reportData.value.cash_outflow.toFixed(2)],
    ['Net Cash Flow', reportData.value.net_cash_flow.toFixed(2)]
  ];
  doc.autoTable({
    startY: 30,
    head: [['Description', 'Amount (UGX)']],
    body: rows
  });
  doc.save('Cashflows_Summary.pdf');
};

onMounted(fetchReport);
</script>

<style scoped>
table {
  border-collapse: collapse;
}
th, td {
  text-align: left;
}
</style>

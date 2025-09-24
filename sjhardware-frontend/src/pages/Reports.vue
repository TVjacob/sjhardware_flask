<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6">Reports Dashboard</h1>

    <!-- Stock & Inventory -->
    <h2 class="text-xl font-semibold mb-2">Stock & Inventory</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <ReportCard title="Out of Stock" link="/reports/out-of-stock" />
      <ReportCard title="Stock List" link="/reports/stock-list" />
      <ReportCard title="Consumption List" link="/reports/consumption-list" />
      <ReportCard title="Performance List" link="/reports/performance-list" />
    </div>

    <!-- Sales & Purchases -->
    <h2 class="text-xl font-semibold mb-2">Sales & Purchases</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <ReportCard title="Sales List" link="/reports/sales-list" />
      <ReportCard title="Purchases List" link="/reports/purchases-list" />
    </div>

    <!-- Accounting -->
    <h2 class="text-xl font-semibold mb-2">Accounting</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <ReportCard title="General Ledger" link="/reports/general-ledger" />
      <ReportCard title="Chart of Accounts" link="/reports/chart-of-accounts" />
      <ReportCard title="Profit & Loss" link="/reports/profit-loss" />
      <ReportCard title="Trial Balance" link="/reports/trial-balance" />
      <ReportCard title="Cash Flow Statement" link="/reports/cash-flow" />
      <ReportCard title="Debtors Report" link="/reports/debtors-report" />
      <ReportCard title="Creditors Report" link="/reports/creditors-report" />
      <ReportCard title="Expenses Report" link="/reports/expenses-report" />
    </div>
  </div>
</template>

<script setup>
import ReportCard from '@/components/ReportCard.vue';
</script>

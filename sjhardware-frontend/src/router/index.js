import { createRouter, createWebHistory } from 'vue-router';
import MainLayout from '../layouts/MainLayout.vue';
import Dashboard from '../pages/Dashboard.vue';
import Products from '../pages/Products.vue';
import Sales from '../pages/Sales.vue';
import Purchases from '../pages/Purchases.vue';
import Report from '../pages/Reports.vue';
import Expenses from '../pages/Expenses.vue';
import Supplier from '../pages/Supplier.vue';
import Customer from '../pages/Customer.vue';
import User from '../pages/User.vue';
import Purchaselist from '@/pages/PurchaseList.vue';
import SalesList from '../pages/SalesList.vue';

// Reports
import OutOfStock from '@/pages/reports/OutOfStock.vue';
import StockList from '@/pages/reports/StockList.vue';
import Consumption from '@/pages/reports/ConsumptionList.vue';
import Performance from '@/pages/reports/Performance.vue';
import PurchaseReport from '@/pages/reports/PurchaseReport.vue';
import ExpenseReport from '@/pages/reports/ExpenseReport.vue';
import Creditor from '@/pages/reports/CreditorList.vue';
import Debtor from '@/pages/reports/DebtorList.vue';
import CashFlow from '@/pages/reports/Cashflow.vue';
import TrialBalance from '@/pages/reports/Trialbalance.vue';
import ProfitAndLoss from '@/pages/reports/Profitandloss.vue';
import GeneralLedger from '@/pages/reports/Generalledger.vue';

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', component: Dashboard, meta: { showGreeting: true, pageName: 'Dashboard' } },
      { path: 'products', component: Products, meta: { showGreeting: true, pageName: 'Products' } },
      { path: 'customers', component: Customer, meta: { showGreeting: false, pageName: 'Customers' } },
      { path: 'sales', component: Sales, meta: { showGreeting: false, pageName: 'Sales' } },
      { path: 'purchases', component: Purchases, meta: { showGreeting: true, pageName: 'Purchases' } },
      { path: 'expenses', component: Expenses, meta: { showGreeting: false, pageName: 'Expenses' } },
      { path: 'supplier', component: Supplier, meta: { showGreeting: false, pageName: 'Supplier' } },
      { path: 'users', component: User, meta: { showGreeting: false, pageName: 'Users' } },
      { path: 'purchaselist', component: Purchaselist, meta: { showGreeting: false, pageName: 'Purchase List' } },
      { path: 'saleslist', component: SalesList, meta: { showGreeting: false, pageName: 'Sales List' } },

      // Reports Dashboard
      { path: 'reports', component: Report, meta: { showGreeting: false, pageName: 'Reports' } },

      // Individual Reports
      { path: 'reports/general-ledger', component: GeneralLedger, meta: { showGreeting: false, pageName: 'General Ledger' } },
      { path: 'reports/profit-loss', component: ProfitAndLoss, meta: { showGreeting: false, pageName: 'Profit & Loss' } },
      { path: 'reports/trial-balance', component: TrialBalance, meta: { showGreeting: false, pageName: 'Trial Balance' } },
      { path: 'reports/cash-flow', component: CashFlow, meta: { showGreeting: false, pageName: 'Cash Flow' } },
      { path: 'reports/debtors-report', component: Debtor, meta: { showGreeting: false, pageName: 'Debtors Report' } },
      { path: 'reports/creditors-report', component: Creditor, meta: { showGreeting: false, pageName: 'Creditors Report' } },
      { path: 'reports/expenses-report', component: ExpenseReport, meta: { showGreeting: false, pageName: 'Expenses Report' } },
      { path: 'reports/purchases-list', component: PurchaseReport, meta: { showGreeting: false, pageName: 'Purchases Report' } },
      { path: 'reports/sales-list', component: SalesList, meta: { showGreeting: false, pageName: 'Sales Report' } },
      { path: 'reports/performance-list', component: Performance, meta: { showGreeting: false, pageName: 'Performance Report' } },
      { path: 'reports/consumption-list', component: Consumption, meta: { showGreeting: false, pageName: 'Consumption Report' } },
      { path: 'reports/stock-list', component: StockList, meta: { showGreeting: false, pageName: 'Stock List' } },
      { path: 'reports/out-of-stock', component: OutOfStock, meta: { showGreeting: false, pageName: 'Out Of Stock' } },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

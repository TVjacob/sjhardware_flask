// import { createRouter, createWebHistory } from 'vue-router';
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
import PurchaseDetails from '@/pages/reports/PurchaseDetails.vue';
import ExpenseDetailsReport from '@/pages/reports/ExpenseDetailsReport.vue';
import Login from '@/pages/Login.vue';

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', component: Dashboard, meta: { showGreeting: true, pageName: 'Dashboard',requiresAuth: true, } },
      { path: 'dashboard', component: Dashboard, meta: { showGreeting: true, pageName: 'Dashboard',requiresAuth: true, } },

      { path: 'products', component: Products, meta: { showGreeting: true, pageName: 'Products',requiresAuth: true, } },
      { path: 'customers', component: Customer, meta: { showGreeting: false, pageName: 'Customers',requiresAuth: true, } },
      { path: 'sales', component: Sales, meta: { showGreeting: false, pageName: 'Sales',requiresAuth: true, } },
      { path: 'purchases', component: Purchases, meta: { showGreeting: true, pageName: 'Purchases',requiresAuth: true, } },
      { path: 'expenses', component: Expenses, meta: { showGreeting: false, pageName: 'Expenses',requiresAuth: true, } },
      { path: 'reports/expenses/:id', component: ExpenseDetailsReport, meta: { showGreeting: false, pageName: 'Expenses Details',requiresAuth: true, } },

      { path: 'supplier', component: Supplier, meta: { showGreeting: false, pageName: 'Supplier',requiresAuth: true, } },
      { path: 'users', component: User, meta: { showGreeting: false, pageName: 'Users',requiresAuth: true, } },
      // { path: 'login', component: Login, meta: { showGreeting: false, pageName: 'Login',requiresAuth: true, } },

      { path: 'purchaselist', component: Purchaselist, meta: { showGreeting: false, pageName: 'Purchase List',requiresAuth: true, } },
      { path: 'saleslist', component: SalesList, meta: { showGreeting: false, pageName: 'Sales List',requiresAuth: true, } },

      // Reports Dashboard
      { path: 'reports', component: Report, meta: { showGreeting: false, pageName: 'Reports',requiresAuth: true, } },

      // Individual Reports
      { path: 'reports/general-ledger', component: GeneralLedger, meta: { showGreeting: false, pageName: 'General Ledger',requiresAuth: true, } },
      { path: 'reports/profit-loss', component: ProfitAndLoss, meta: { showGreeting: false, pageName: 'Profit & Loss',requiresAuth: true, } },
      { path: 'reports/trial-balance', component: TrialBalance, meta: { showGreeting: false, pageName: 'Trial Balance',requiresAuth: true, } },
      { path: 'reports/cash-flow', component: CashFlow, meta: { showGreeting: false, pageName: 'Cash Flow',requiresAuth: true, } },
      { path: 'reports/debtors-report', component: Debtor, meta: { showGreeting: false, pageName: 'Debtors Report',requiresAuth: true, } },
      { path: 'reports/creditors-report', component: Creditor, meta: { showGreeting: false, pageName: 'Creditors Report',requiresAuth: true, } },
      { path: 'reports/expenses-report', component: ExpenseReport, meta: { showGreeting: false, pageName: 'Expenses Report',requiresAuth: true, } },
      { path: 'reports/purchases-list', component: PurchaseReport, meta: { showGreeting: false, pageName: 'Purchases Report',requiresAuth: true, } },
      { path: 'reports/sales-list', component: SalesList, meta: { showGreeting: false, pageName: 'Sales Report',requiresAuth: true, } },
      { path: 'reports/performance-list', component: Performance, meta: { showGreeting: false, pageName: 'Performance Report',requiresAuth: true, } },
      { path: 'reports/consumption-list', component: Consumption, meta: { showGreeting: false, pageName: 'Consumption Report',requiresAuth: true, } },
      { path: 'reports/stock-list', component: StockList, meta: { showGreeting: false, pageName: 'Stock List',requiresAuth: true, } },
      { path: 'reports/out-of-stock', component: OutOfStock, meta: { showGreeting: false, pageName: 'Out Of Stock',requiresAuth: true, } },
      {
        path: '/purchase-orders/:id',
        name: 'PurchaseOrderDetails',
        component: PurchaseDetails,
        meta: { showGreeting: false, pageName: 'Purchase Order Details', requiresAuth: true,}
      },
      
    ],
  },
    {
      path: '/login',
      component: Login, // Standalone login page
      meta: { requiresAuth: false, pageName: 'Login' }
    }
  // },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// -------- Navigation Guard for Authentication --------
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token'); // JWT token
  const isLoggedIn = !!token;

  if (to.meta.requiresAuth && !isLoggedIn) {
    // Redirect to login if not logged in
    return next({ path: '/login' });
  }

  if (to.path === '/login' && isLoggedIn) {
    // Redirect logged-in user away from login page
    return next({ path: '/' });
  }

  next(); // allow access
});

export default router;

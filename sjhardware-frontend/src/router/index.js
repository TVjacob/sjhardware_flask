// import { createRouter, createWebHistory } from 'vue-router';
// import MainLayout from '../layouts/MainLayout.vue';
// import Dashboard from '../pages/Dashboard.vue';
// import Products from '../pages/Products.vue';
// import Sales from '../pages/Sales.vue';
// import Purchases from '../pages/Purchases.vue';
// import Payments from '../pages/Payments.vue';
// import Expenses from '../pages/Expenses.vue';

// const routes = [
//   {
//     path: '/',
//     component: MainLayout, // Wrap all pages in MainLayout
//     children: [
//       { path: '', component: Dashboard },      // / → Dashboard
//       { path: 'products', component: Products },
//       { path: 'sales', component: Sales },
//       { path: 'purchases', component: Purchases },
//       { path: 'payments', component: Payments },
//       { path: 'expenses', component: Expenses },
//     ],
//   },
// ];

// const router = createRouter({
//   history: createWebHistory(),
//   routes,
// });

// export default router;
import { createRouter, createWebHistory } from 'vue-router';
import MainLayout from '../layouts/MainLayout.vue';
import Dashboard from '../pages/Dashboard.vue';
import Products from '../pages/Products.vue';
import Sales from '../pages/Sales.vue';
import Purchases from '../pages/Purchases.vue';
import Payments from '../pages/Payments.vue';
import Expenses from '../pages/Expenses.vue';
import Supplier from '../pages/Supplier.vue';

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', component: Dashboard, meta: { showGreeting: true, pageName: 'Dashboard' } },
      { path: 'products', component: Products, meta: { showGreeting: true, pageName: 'Products' } },
      { path: 'sales', component: Sales, meta: { showGreeting: false, pageName: 'Sales' } },
      { path: 'purchases', component: Purchases, meta: { showGreeting: true, pageName: 'Purchases' } },
      { path: 'payments', component: Payments, meta: { showGreeting: false, pageName: 'Payments' } },
      { path: 'supplier', component: Supplier, meta: { showGreeting: false, pageName: 'Supplier' } },
      { path: 'expenses', component: Expenses, meta: { showGreeting: false, pageName: 'Expenses' } },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

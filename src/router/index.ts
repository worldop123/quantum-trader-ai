import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录 | QuantumTrader AI' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { title: '注册 | QuantumTrader AI' }
  },
  {
    path: '/',
    component: () => import('../layouts/UserLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/user/Dashboard.vue'),
        meta: { title: '仪表盘 | QuantumTrader AI' }
      },
      {
        path: 'trade',
        name: 'Trade',
        component: () => import('../views/user/Trade.vue'),
        meta: { title: '交易 | QuantumTrader AI' }
      },
      {
        path: 'positions',
        name: 'Positions',
        component: () => import('../views/user/Positions.vue'),
        meta: { title: '持仓 | QuantumTrader AI' }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('../views/user/Orders.vue'),
        meta: { title: '订单 | QuantumTrader AI' }
      },
      {
        path: 'assets',
        name: 'Assets',
        component: () => import('../views/user/Assets.vue'),
        meta: { title: '资产 | QuantumTrader AI' }
      },
      {
        path: 'ai-strategy',
        name: 'AIStrategy',
        component: () => import('../views/user/AIStrategy.vue'),
        meta: { title: 'AI策略 | QuantumTrader AI' }
      },
      {
        path: 'risk-control',
        name: 'RiskControl',
        component: () => import('../views/user/RiskControl.vue'),
        meta: { title: '风控设置 | QuantumTrader AI' }
      },
      {
        path: 'options',
        name: 'Options',
        component: () => import('../views/user/OptionTrading.vue'),
        meta: { title: '期权交易 | QuantumTrader AI' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/user/Settings.vue'),
        meta: { title: '设置 | QuantumTrader AI' }
      }
    ]
  },
  {
    path: '/admin',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('../views/admin/Dashboard.vue'),
        meta: { title: '管理后台 | QuantumTrader AI' }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('../views/admin/UserManagement.vue'),
        meta: { title: '用户管理 | QuantumTrader AI' }
      },
      {
        path: 'system',
        name: 'SystemSettings',
        component: () => import('../views/admin/SystemSettings.vue'),
        meta: { title: '系统设置 | QuantumTrader AI' }
      },
      {
        path: 'monitoring',
        name: 'DataMonitoring',
        component: () => import('../views/admin/DataMonitoring.vue'),
        meta: { title: '数据监控 | QuantumTrader AI' }
      },
      {
        path: 'risk',
        name: 'RiskManagement',
        component: () => import('../views/admin/RiskManagement.vue'),
        meta: { title: '风控管理 | QuantumTrader AI' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = to.meta.title as string || 'QuantumTrader AI'
  
  // 模拟认证检查
  const isLoggedIn = localStorage.getItem('quantum_token')
  const userRole = localStorage.getItem('quantum_role')
  
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
  } else if (to.meta.requiresAdmin && userRole !== 'admin') {
    next('/')
  } else if ((to.path === '/login' || to.path === '/register') && isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router

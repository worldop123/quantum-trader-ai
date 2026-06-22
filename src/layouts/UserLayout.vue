<template>
  <div class="min-h-screen bg-quantum-dark flex">
    <!-- Sidebar -->
    <aside class="w-64 bg-quantum-darker border-r border-quantum-border flex flex-col">
      <!-- Logo -->
      <div class="p-6 border-b border-quantum-border">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-quantum-cyan flex items-center justify-center">
            <Zap class="w-6 h-6 text-quantum-darker" />
          </div>
          <div>
            <h1 class="text-lg font-bold neon-text-cyan">QuantumTrader</h1>
            <p class="text-xs text-gray-500">AI Trading System</p>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4 space-y-1">
        <router-link to="/dashboard" class="sidebar-link" :class="{ active: $route.path === '/dashboard' }">
          <LayoutDashboard class="w-5 h-5" />
          <span>仪表盘</span>
        </router-link>
        <router-link to="/trade" class="sidebar-link" :class="{ active: $route.path === '/trade' }">
          <TrendingUp class="w-5 h-5" />
          <span>交易</span>
        </router-link>
        <router-link to="/positions" class="sidebar-link" :class="{ active: $route.path === '/positions' }">
          <Briefcase class="w-5 h-5" />
          <span>持仓</span>
        </router-link>
        <router-link to="/orders" class="sidebar-link" :class="{ active: $route.path === '/orders' }">
          <FileText class="w-5 h-5" />
          <span>订单</span>
        </router-link>
        <router-link to="/assets" class="sidebar-link" :class="{ active: $route.path === '/assets' }">
          <Wallet class="w-5 h-5" />
          <span>资产</span>
        </router-link>
        <router-link to="/ai-strategy" class="sidebar-link" :class="{ active: $route.path === '/ai-strategy' }">
          <Brain class="w-5 h-5" />
          <span>AI策略</span>
        </router-link>
        <router-link to="/risk-control" class="sidebar-link" :class="{ active: $route.path === '/risk-control' }">
          <Shield class="w-5 h-5" />
          <span>风控设置</span>
        </router-link>
        <router-link to="/settings" class="sidebar-link" :class="{ active: $route.path === '/settings' }">
          <Settings class="w-5 h-5" />
          <span>设置</span>
        </router-link>
      </nav>

      <!-- User Info -->
      <div class="p-4 border-t border-quantum-border">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-full bg-quantum-border flex items-center justify-center">
            <User class="w-5 h-5 text-gray-400" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-200 truncate">test_user</p>
            <p class="text-xs text-gray-500 truncate">test@quantumtrader.ai</p>
          </div>
        </div>
        <button @click="logout" class="w-full quantum-btn-secondary text-sm flex items-center justify-center gap-2">
          <LogOut class="w-4 h-4" />
          退出登录
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col">
      <!-- Header -->
      <header class="h-16 bg-quantum-darker border-b border-quantum-border px-6 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <h2 class="text-lg font-semibold text-gray-200">{{ pageTitle }}</h2>
          <span class="px-2 py-1 text-xs rounded bg-quantum-yellow/20 text-quantum-yellow">
            模拟盘
          </span>
        </div>
        <div class="flex items-center gap-4">
          <div class="text-right">
            <p class="text-xs text-gray-500">可用余额</p>
            <p class="text-sm font-mono text-quantum-green">${{ tradingStore.availableBalance.toLocaleString() }}</p>
          </div>
          <button class="p-2 rounded-lg hover:bg-quantum-border transition-colors">
            <Bell class="w-5 h-5 text-gray-400" />
          </button>
        </div>
      </header>

      <!-- Page Content -->
      <div class="flex-1 p-6 overflow-auto">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useTradingStore } from '../stores/trading'
import {
  LayoutDashboard,
  TrendingUp,
  Briefcase,
  FileText,
  Wallet,
  Brain,
  Shield,
  Settings,
  User,
  LogOut,
  Bell,
  Zap
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const tradingStore = useTradingStore()

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/dashboard': '仪表盘',
    '/trade': '交易',
    '/positions': '持仓管理',
    '/orders': '订单管理',
    '/assets': '资产概览',
    '/ai-strategy': 'AI策略中心',
    '/risk-control': '风控设置',
    '/settings': '系统设置'
  }
  return titles[route.path] || 'QuantumTrader'
})

function logout() {
  userStore.logout()
  router.push('/login')
}
</script>

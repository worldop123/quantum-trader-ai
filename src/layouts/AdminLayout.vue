<template>
  <div class="min-h-screen bg-quantum-dark flex">
    <!-- Sidebar -->
    <aside class="w-64 bg-quantum-darker border-r border-quantum-border flex flex-col">
      <!-- Logo -->
      <div class="p-6 border-b border-quantum-border">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-quantum-purple flex items-center justify-center">
            <Shield class="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 class="text-lg font-bold text-quantum-purple">Admin Panel</h1>
            <p class="text-xs text-gray-500">QuantumTrader AI</p>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4 space-y-1">
        <router-link to="/admin/dashboard" class="sidebar-link" :class="{ active: $route.path === '/admin/dashboard' }">
          <LayoutDashboard class="w-5 h-5" />
          <span>数据概览</span>
        </router-link>
        <router-link to="/admin/users" class="sidebar-link" :class="{ active: $route.path === '/admin/users' }">
          <Users class="w-5 h-5" />
          <span>用户管理</span>
        </router-link>
        <router-link to="/admin/monitoring" class="sidebar-link" :class="{ active: $route.path === '/admin/monitoring' }">
          <Activity class="w-5 h-5" />
          <span>数据监控</span>
        </router-link>
        <router-link to="/admin/risk" class="sidebar-link" :class="{ active: $route.path === '/admin/risk' }">
          <AlertTriangle class="w-5 h-5" />
          <span>风控管理</span>
        </router-link>
        <router-link to="/admin/system" class="sidebar-link" :class="{ active: $route.path === '/admin/system' }">
          <Settings class="w-5 h-5" />
          <span>系统设置</span>
        </router-link>
      </nav>

      <!-- User Info -->
      <div class="p-4 border-t border-quantum-border">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-full bg-quantum-purple/20 flex items-center justify-center">
            <Shield class="w-5 h-5 text-quantum-purple" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-200 truncate">admin</p>
            <p class="text-xs text-gray-500 truncate">admin@quantumtrader.ai</p>
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
          <span class="px-2 py-1 text-xs rounded bg-quantum-purple/20 text-quantum-purple">
            管理员
          </span>
        </div>
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-quantum-green animate-pulse"></span>
            <span class="text-xs text-gray-400">系统正常</span>
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
import {
  LayoutDashboard,
  Users,
  Activity,
  AlertTriangle,
  Settings,
  Shield,
  LogOut,
  Bell
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/admin/dashboard': '数据概览',
    '/admin/users': '用户管理',
    '/admin/monitoring': '数据监控',
    '/admin/risk': '风控管理',
    '/admin/system': '系统设置'
  }
  return titles[route.path] || '管理后台'
})

function logout() {
  userStore.logout()
  router.push('/login')
}
</script>

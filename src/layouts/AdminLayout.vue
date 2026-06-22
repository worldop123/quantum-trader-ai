<template>
  <div class="min-h-screen bg-quantum-dark flex flex-col md:flex-row">
    <!-- PC端侧边栏 (>=768px) -->
    <aside class="hidden md:flex w-64 bg-quantum-darker border-r border-quantum-border flex-col flex-shrink-0">
      <!-- Logo -->
      <div class="p-6 border-b border-quantum-border">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-quantum-purple flex items-center justify-center flex-shrink-0">
            <Shield class="w-6 h-6 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="text-lg font-bold text-quantum-purple truncate">Admin Panel</h1>
            <p class="text-xs text-gray-500">QuantumTrader AI</p>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4 space-y-1 overflow-y-auto">
        <router-link to="/admin/dashboard" class="sidebar-link" :class="{ active: $route.path === '/admin/dashboard' }">
          <LayoutDashboard class="w-5 h-5 flex-shrink-0" />
          <span>数据概览</span>
        </router-link>
        <router-link to="/admin/users" class="sidebar-link" :class="{ active: $route.path === '/admin/users' }">
          <Users class="w-5 h-5 flex-shrink-0" />
          <span>用户管理</span>
        </router-link>
        <router-link to="/admin/monitoring" class="sidebar-link" :class="{ active: $route.path === '/admin/monitoring' }">
          <Activity class="w-5 h-5 flex-shrink-0" />
          <span>数据监控</span>
        </router-link>
        <router-link to="/admin/risk" class="sidebar-link" :class="{ active: $route.path === '/admin/risk' }">
          <AlertTriangle class="w-5 h-5 flex-shrink-0" />
          <span>风控管理</span>
        </router-link>
        <router-link to="/admin/system" class="sidebar-link" :class="{ active: $route.path === '/admin/system' }">
          <Settings class="w-5 h-5 flex-shrink-0" />
          <span>系统设置</span>
        </router-link>
      </nav>

      <!-- User Info -->
      <div class="p-4 border-t border-quantum-border">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-full bg-quantum-purple/20 flex items-center justify-center flex-shrink-0">
            <Shield class="w-5 h-5 text-quantum-purple" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-200 truncate">admin</p>
            <p class="text-xs text-gray-500 truncate">admin@quantumtrader.ai</p>
          </div>
        </div>
        <button @click="logout" class="w-full quantum-btn-secondary text-sm flex items-center justify-center gap-2 min-h-[44px]">
          <LogOut class="w-4 h-4" />
          退出登录
        </button>
      </div>
    </aside>

    <!-- 移动端侧边栏抽屉 (<768px) -->
    <Drawer v-model="mobileSidebarOpen" position="left" :width="'280px'" :showClose="true">
      <template #header>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-quantum-purple flex items-center justify-center flex-shrink-0">
            <Shield class="w-6 h-6 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="text-lg font-bold text-quantum-purple truncate">Admin Panel</h1>
            <p class="text-xs text-gray-500">QuantumTrader AI</p>
          </div>
        </div>
      </template>
      <nav class="space-y-1">
        <router-link to="/admin/dashboard" class="sidebar-link" :class="{ active: $route.path === '/admin/dashboard' }" @click="closeMobileSidebar">
          <LayoutDashboard class="w-5 h-5 flex-shrink-0" />
          <span>数据概览</span>
        </router-link>
        <router-link to="/admin/users" class="sidebar-link" :class="{ active: $route.path === '/admin/users' }" @click="closeMobileSidebar">
          <Users class="w-5 h-5 flex-shrink-0" />
          <span>用户管理</span>
        </router-link>
        <router-link to="/admin/monitoring" class="sidebar-link" :class="{ active: $route.path === '/admin/monitoring' }" @click="closeMobileSidebar">
          <Activity class="w-5 h-5 flex-shrink-0" />
          <span>数据监控</span>
        </router-link>
        <router-link to="/admin/risk" class="sidebar-link" :class="{ active: $route.path === '/admin/risk' }" @click="closeMobileSidebar">
          <AlertTriangle class="w-5 h-5 flex-shrink-0" />
          <span>风控管理</span>
        </router-link>
        <router-link to="/admin/system" class="sidebar-link" :class="{ active: $route.path === '/admin/system' }" @click="closeMobileSidebar">
          <Settings class="w-5 h-5 flex-shrink-0" />
          <span>系统设置</span>
        </router-link>
      </nav>
      <div class="mt-6 pt-4 border-t border-quantum-border">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-full bg-quantum-purple/20 flex items-center justify-center flex-shrink-0">
            <Shield class="w-5 h-5 text-quantum-purple" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-200 truncate">admin</p>
            <p class="text-xs text-gray-500 truncate">admin@quantumtrader.ai</p>
          </div>
        </div>
        <button @click="logout" class="w-full quantum-btn-secondary text-sm flex items-center justify-center gap-2 min-h-[44px]">
          <LogOut class="w-4 h-4" />
          退出登录
        </button>
      </div>
    </Drawer>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col min-w-0">
      <!-- Header -->
      <header class="h-14 md:h-16 bg-quantum-darker border-b border-quantum-border px-3 md:px-6 flex items-center justify-between sticky top-0 z-50">
        <div class="flex items-center gap-2 md:gap-4 min-w-0">
          <!-- 移动端汉堡菜单 -->
          <button @click="openMobileSidebar" class="md:hidden p-2 rounded-lg hover:bg-quantum-border transition-colors flex-shrink-0 min-h-[44px] min-w-[44px] flex items-center justify-center">
            <Menu class="w-5 h-5 text-gray-300" />
          </button>
          <!-- 移动端Logo -->
          <div class="md:hidden flex items-center gap-2 flex-shrink-0">
            <div class="w-8 h-8 rounded-lg bg-quantum-purple flex items-center justify-center">
              <Shield class="w-5 h-5 text-white" />
            </div>
          </div>
          <h2 class="hidden md:block text-lg font-semibold text-gray-200 truncate">{{ pageTitle }}</h2>
          <span class="hidden md:inline-block px-2 py-1 text-xs rounded bg-quantum-purple/20 text-quantum-purple flex-shrink-0">
            管理员
          </span>
        </div>
        <div class="flex items-center gap-2 md:gap-4 flex-shrink-0">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-quantum-green animate-pulse"></span>
            <span class="text-xs text-gray-400 hidden sm:inline">系统正常</span>
          </div>
          <!-- WebSocket 连接状态 -->
          <WsStatus :show-text="true" :show-reconnect-count="true" />
          <button class="p-2 rounded-lg hover:bg-quantum-border transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center relative">
            <Bell class="w-5 h-5 text-gray-400" />
            <span class="absolute top-1 right-1 w-2 h-2 bg-quantum-red rounded-full"></span>
          </button>
        </div>
      </header>

      <!-- WebSocket 断线重连提示 -->
      <div v-if="showReconnectBanner" class="bg-quantum-yellow/10 border-b border-quantum-yellow/30 px-4 py-2 flex items-center justify-between gap-3">
        <div class="flex items-center gap-2 text-sm text-quantum-yellow">
          <WifiOff class="w-4 h-4 flex-shrink-0" />
          <span>实时连接已断开,正在尝试重连... ({{ reconnectCount }})</span>
        </div>
        <button @click="manualReconnect" class="text-xs px-2 py-1 rounded bg-quantum-yellow/20 text-quantum-yellow hover:bg-quantum-yellow/30 transition-colors">
          立即重连
        </button>
      </div>

      <!-- Page Content -->
      <div class="flex-1 p-3 md:p-6 overflow-auto pb-20 md:pb-6">
        <router-view />
      </div>
    </main>

    <!-- 移动端底部导航栏 (<768px) -->
    <BottomNav />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useWebSocket } from '../utils/websocket'
import Drawer from '../components/common/Drawer.vue'
import BottomNav from '../components/layout/BottomNav.vue'
import WsStatus from '../components/common/WsStatus.vue'
import {
  LayoutDashboard,
  Users,
  Activity,
  AlertTriangle,
  Settings,
  Shield,
  LogOut,
  Bell,
  Menu,
  WifiOff
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// WebSocket 全局连接管理
const { status: wsStatus, reconnectCount, connect, disconnect, isConnected } = useWebSocket()

// 是否显示断线重连提示横幅
const showReconnectBanner = ref(false)

// 监听连接状态,控制重连提示
watch(wsStatus, (newStatus) => {
  if (newStatus === 'disconnected' || newStatus === 'reconnecting') {
    showReconnectBanner.value = true
  } else if (newStatus === 'connected') {
    showReconnectBanner.value = false
  }
})

function manualReconnect() {
  if (!isConnected()) {
    connect()
  }
}

const mobileSidebarOpen = ref(false)

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

function openMobileSidebar() {
  mobileSidebarOpen.value = true
}

function closeMobileSidebar() {
  mobileSidebarOpen.value = false
}

function logout() {
  // 登出时断开 WebSocket
  disconnect()
  userStore.logout()
  router.push('/login')
}

onMounted(() => {
  // 登录后自动连接 WebSocket
  if (userStore.isLoggedIn) {
    connect()
  }
})

onBeforeUnmount(() => {
  // 布局卸载时断开连接
  disconnect()
})
</script>

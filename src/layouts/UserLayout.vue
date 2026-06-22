<template>
  <div class="min-h-screen bg-quantum-dark flex flex-col md:flex-row">
    <!-- PC端侧边栏 (>=768px) -->
    <aside class="hidden md:flex w-64 bg-quantum-darker border-r border-quantum-border flex-col flex-shrink-0">
      <!-- Logo -->
      <div class="p-6 border-b border-quantum-border">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-quantum-cyan flex items-center justify-center flex-shrink-0">
            <Zap class="w-6 h-6 text-quantum-darker" />
          </div>
          <div class="min-w-0">
            <h1 class="text-lg font-bold neon-text-cyan truncate">QuantumTrader</h1>
            <p class="text-xs text-gray-500">AI Trading System</p>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4 space-y-1 overflow-y-auto">
        <router-link to="/dashboard" class="sidebar-link" :class="{ active: $route.path === '/dashboard' }">
          <LayoutDashboard class="w-5 h-5 flex-shrink-0" />
          <span>仪表盘</span>
        </router-link>
        <router-link to="/trade" class="sidebar-link" :class="{ active: $route.path === '/trade' }">
          <TrendingUp class="w-5 h-5 flex-shrink-0" />
          <span>交易</span>
        </router-link>
        <router-link to="/positions" class="sidebar-link" :class="{ active: $route.path === '/positions' }">
          <Briefcase class="w-5 h-5 flex-shrink-0" />
          <span>持仓</span>
        </router-link>
        <router-link to="/orders" class="sidebar-link" :class="{ active: $route.path === '/orders' }">
          <FileText class="w-5 h-5 flex-shrink-0" />
          <span>订单</span>
        </router-link>
        <router-link to="/assets" class="sidebar-link" :class="{ active: $route.path === '/assets' }">
          <Wallet class="w-5 h-5 flex-shrink-0" />
          <span>资产</span>
        </router-link>
        <router-link to="/ai-strategy" class="sidebar-link" :class="{ active: $route.path === '/ai-strategy' }">
          <Brain class="w-5 h-5 flex-shrink-0" />
          <span>AI策略</span>
        </router-link>
        <router-link to="/risk-control" class="sidebar-link" :class="{ active: $route.path === '/risk-control' }">
          <Shield class="w-5 h-5 flex-shrink-0" />
          <span>风控设置</span>
        </router-link>
        <router-link to="/settings" class="sidebar-link" :class="{ active: $route.path === '/settings' }">
          <Settings class="w-5 h-5 flex-shrink-0" />
          <span>设置</span>
        </router-link>
      </nav>

      <!-- User Info -->
      <div class="p-4 border-t border-quantum-border">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-full bg-quantum-border flex items-center justify-center flex-shrink-0">
            <User class="w-5 h-5 text-gray-400" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-200 truncate">test_user</p>
            <p class="text-xs text-gray-500 truncate">test@quantumtrader.ai</p>
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
          <div class="w-10 h-10 rounded-lg bg-quantum-cyan flex items-center justify-center flex-shrink-0">
            <Zap class="w-6 h-6 text-quantum-darker" />
          </div>
          <div class="min-w-0">
            <h1 class="text-lg font-bold neon-text-cyan truncate">QuantumTrader</h1>
            <p class="text-xs text-gray-500">AI Trading System</p>
          </div>
        </div>
      </template>
      <nav class="space-y-1">
        <router-link to="/dashboard" class="sidebar-link" :class="{ active: $route.path === '/dashboard' }" @click="closeMobileSidebar">
          <LayoutDashboard class="w-5 h-5 flex-shrink-0" />
          <span>仪表盘</span>
        </router-link>
        <router-link to="/trade" class="sidebar-link" :class="{ active: $route.path === '/trade' }" @click="closeMobileSidebar">
          <TrendingUp class="w-5 h-5 flex-shrink-0" />
          <span>交易</span>
        </router-link>
        <router-link to="/positions" class="sidebar-link" :class="{ active: $route.path === '/positions' }" @click="closeMobileSidebar">
          <Briefcase class="w-5 h-5 flex-shrink-0" />
          <span>持仓</span>
        </router-link>
        <router-link to="/orders" class="sidebar-link" :class="{ active: $route.path === '/orders' }" @click="closeMobileSidebar">
          <FileText class="w-5 h-5 flex-shrink-0" />
          <span>订单</span>
        </router-link>
        <router-link to="/assets" class="sidebar-link" :class="{ active: $route.path === '/assets' }" @click="closeMobileSidebar">
          <Wallet class="w-5 h-5 flex-shrink-0" />
          <span>资产</span>
        </router-link>
        <router-link to="/ai-strategy" class="sidebar-link" :class="{ active: $route.path === '/ai-strategy' }" @click="closeMobileSidebar">
          <Brain class="w-5 h-5 flex-shrink-0" />
          <span>AI策略</span>
        </router-link>
        <router-link to="/risk-control" class="sidebar-link" :class="{ active: $route.path === '/risk-control' }" @click="closeMobileSidebar">
          <Shield class="w-5 h-5 flex-shrink-0" />
          <span>风控设置</span>
        </router-link>
        <router-link to="/settings" class="sidebar-link" :class="{ active: $route.path === '/settings' }" @click="closeMobileSidebar">
          <Settings class="w-5 h-5 flex-shrink-0" />
          <span>设置</span>
        </router-link>
      </nav>
      <div class="mt-6 pt-4 border-t border-quantum-border">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-full bg-quantum-border flex items-center justify-center flex-shrink-0">
            <User class="w-5 h-5 text-gray-400" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-200 truncate">test_user</p>
            <p class="text-xs text-gray-500 truncate">test@quantumtrader.ai</p>
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
            <div class="w-8 h-8 rounded-lg bg-quantum-cyan flex items-center justify-center">
              <Zap class="w-5 h-5 text-quantum-darker" />
            </div>
          </div>
          <h2 class="hidden md:block text-lg font-semibold text-gray-200 truncate">{{ pageTitle }}</h2>
          <span class="hidden md:inline-block px-2 py-1 text-xs rounded bg-quantum-yellow/20 text-quantum-yellow flex-shrink-0">
            模拟盘
          </span>
        </div>
        <div class="flex items-center gap-2 md:gap-4 flex-shrink-0">
          <div class="text-right">
            <p class="text-xs text-gray-500 hidden md:block">可用余额</p>
            <p class="text-sm font-mono text-quantum-green">
              <span class="md:hidden text-xs text-gray-500 mr-1">余额</span>${{ tradingStore.availableBalance.toLocaleString() }}
            </p>
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
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useTradingStore } from '../stores/trading'
import { useWebSocket } from '../utils/websocket'
import Drawer from '../components/common/Drawer.vue'
import BottomNav from '../components/layout/BottomNav.vue'
import WsStatus from '../components/common/WsStatus.vue'
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
  Zap,
  Menu,
  WifiOff
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const tradingStore = useTradingStore()

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
  // 初始化交易数据
  tradingStore.init().catch((err) => {
    console.error('Failed to init trading store:', err)
  })
  // 登录后自动连接 WebSocket
  if (userStore.isLoggedIn) {
    connect()
  }
})

onBeforeUnmount(() => {
  // 布局卸载时断开连接(通常在登出/路由切换离开用户区域时)
  disconnect()
})
</script>

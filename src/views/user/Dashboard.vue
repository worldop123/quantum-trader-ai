<template>
  <div class="space-y-6">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">总资产</p>
          <Wallet class="w-5 h-5 text-quantum-cyan" />
        </div>
        <p class="text-2xl font-bold text-gray-200 font-mono">
          <NumberTicker
            :value="tradingStore.totalBalance"
            :decimals="2"
            prefix="$"
            :flash-on-change="true"
            up-color="#00ff88"
            down-color="#ff4757"
            neutral-color="#e4e7ed"
          />
        </p>
        <p class="text-xs mt-1" :class="todayPnl >= 0 ? 'text-quantum-green' : 'text-quantum-red'">
          {{ todayPnl >= 0 ? '+' : '' }}{{ todayPnlPercent.toFixed(2) }}% 今日
        </p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">可用余额</p>
          <DollarSign class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold text-gray-200 font-mono">
          <NumberTicker
            :value="tradingStore.availableBalance"
            :decimals="2"
            prefix="$"
            :flash-on-change="true"
            up-color="#00ff88"
            down-color="#ff4757"
            neutral-color="#e4e7ed"
          />
        </p>
        <p class="text-xs text-gray-500 mt-1">{{ usagePercent.toFixed(0) }}% 使用率</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">持仓盈亏</p>
          <TrendingUp class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold font-mono">
          <NumberTicker
            :value="tradingStore.totalPnl"
            :decimals="2"
            prefix="$"
            :show-sign="true"
            :flash-on-change="true"
            up-color="#00ff88"
            down-color="#ff4757"
            neutral-color="#e4e7ed"
          />
        </p>
        <p class="text-xs mt-1" :class="tradingStore.totalPnl >= 0 ? 'text-quantum-green' : 'text-quantum-red'">
          {{ tradingStore.totalPnl >= 0 ? '+' : '' }}{{ pnlPercent.toFixed(2) }}%
        </p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">运行策略</p>
          <Brain class="w-5 h-5 text-quantum-purple" />
        </div>
        <p class="text-2xl font-bold text-gray-200 font-mono">
          <NumberTicker
            :value="runningStrategies"
            :decimals="0"
            :flash-on-change="true"
            up-color="#00ff88"
            down-color="#ff4757"
            neutral-color="#e4e7ed"
          />
          <span class="text-gray-500">/{{ totalStrategies }}</span>
        </p>
        <p class="text-xs text-quantum-purple mt-1">AI 策略运行中</p>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 quantum-card">
        <FundChart :data="fundChartData" :height="300" />
      </div>

      <div class="quantum-card">
        <AssetPieChart :data="assetPieData" :height="280" />
      </div>
    </div>

    <!-- Recent Positions & Orders -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="quantum-card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-200">当前持仓</h3>
          <router-link to="/positions" class="text-sm text-quantum-cyan hover:underline">查看全部</router-link>
        </div>
        <div class="space-y-3">
          <div v-for="position in tradingStore.positions.slice(0, 3)" :key="position.id"
            class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-quantum-border flex items-center justify-center">
                <span class="text-xs font-bold text-gray-400">{{ position.symbol.substring(0, 2) }}</span>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-200">{{ position.symbol }}</p>
                <p class="text-xs text-gray-500">{{ position.type === 'spot' ? '现货' : '合约' }} · {{ position.side === 'long' ? '做多' : '做空' }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm font-mono" :class="position.pnl >= 0 ? 'text-quantum-green' : 'text-quantum-red'">
                <NumberTicker
                  :value="position.pnl"
                  :decimals="2"
                  prefix="$"
                  :show-sign="true"
                  :flash-on-change="true"
                  up-color="#00ff88"
                  down-color="#ff4757"
                />
              </p>
              <p class="text-xs" :class="position.pnlPercent >= 0 ? 'text-quantum-green' : 'text-quantum-red'">
                {{ position.pnlPercent >= 0 ? '+' : '' }}{{ position.pnlPercent }}%
              </p>
            </div>
          </div>
          <div v-if="tradingStore.positions.length === 0" class="py-8 text-center text-gray-500">
            暂无持仓
          </div>
        </div>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-200">最近订单</h3>
          <router-link to="/orders" class="text-sm text-quantum-cyan hover:underline">查看全部</router-link>
        </div>
        <div class="space-y-3">
          <div v-for="order in tradingStore.orders.slice(0, 3)" :key="order.id"
            class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full flex items-center justify-center"
                :class="order.side === 'buy' ? 'bg-quantum-green/20' : 'bg-quantum-red/20'">
                <TrendingUp v-if="order.side === 'buy'" class="w-5 h-5 text-quantum-green" />
                <TrendingDown v-else class="w-5 h-5 text-quantum-red" />
              </div>
              <div>
                <p class="text-sm font-medium text-gray-200">{{ order.symbol }}</p>
                <p class="text-xs text-gray-500">{{ order.type === 'market' ? '市价' : '限价' }} · {{ order.side === 'buy' ? '买入' : '卖出' }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm font-mono text-gray-200">{{ order.quantity }}</p>
              <span class="text-xs px-2 py-0.5 rounded"
                :class="{
                  'bg-quantum-green/20 text-quantum-green': order.status === 'filled',
                  'bg-quantum-yellow/20 text-quantum-yellow': order.status === 'pending',
                  'bg-gray-500/20 text-gray-400': order.status === 'cancelled'
                }">
                {{ statusLabels[order.status] }}
              </span>
            </div>
          </div>
          <div v-if="tradingStore.orders.length === 0" class="py-8 text-center text-gray-500">
            暂无订单
          </div>
        </div>
      </div>
    </div>

    <!-- Notification Toast -->
    <div v-if="latestNotification" class="fixed bottom-6 right-6 quantum-card max-w-sm z-50 border-quantum-cyan/50">
      <div class="flex items-start gap-3">
        <div class="w-8 h-8 rounded-full bg-quantum-cyan/20 flex items-center justify-center shrink-0">
          <Bell class="w-4 h-4 text-quantum-cyan" />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-200">{{ latestNotification.title }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ latestNotification.message }}</p>
        </div>
        <button @click="latestNotification = null" class="text-gray-500 hover:text-gray-300 text-sm">×</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useTradingStore } from '../../stores/trading'
import { useWebSocket } from '../../utils/websocket'
import FundChart from '../../components/charts/FundChart.vue'
import AssetPieChart from '../../components/charts/AssetPieChart.vue'
import NumberTicker from '../../components/common/NumberTicker.vue'
import {
  Wallet,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Brain,
  Bell
} from 'lucide-vue-next'

const tradingStore = useTradingStore()
const { subscribe, unsubscribe } = useWebSocket()

const statusLabels: Record<string, string> = {
  filled: '已成交',
  pending: '待成交',
  cancelled: '已取消',
  rejected: '已拒绝'
}

const runningStrategies = computed(() =>
  tradingStore.aiStrategies.filter(s => s.status === 'running').length
)
const totalStrategies = computed(() => tradingStore.aiStrategies.length)

// 今日盈亏(基于持仓盈亏的模拟统计)
const todayPnl = computed(() => tradingStore.totalPnl)
const todayPnlPercent = computed(() => {
  if (tradingStore.totalBalance === 0) return 0
  return (todayPnl.value / tradingStore.totalBalance) * 100
})
const pnlPercent = computed(() => {
  if (tradingStore.totalBalance === 0) return 0
  return (tradingStore.totalPnl / tradingStore.totalBalance) * 100
})
const usagePercent = computed(() => {
  if (tradingStore.totalBalance === 0) return 0
  return ((tradingStore.totalBalance - tradingStore.availableBalance) / tradingStore.totalBalance) * 100
})

// 资金曲线数据
interface FundPoint { time: number; value: number }
const fundChartData = ref<FundPoint[]>([])

// 资产分布数据
interface AssetItem { name: string; value: number }
const assetPieData = ref<AssetItem[]>([])

// 最新通知
interface NotificationItem {
  title: string
  message: string
  level?: string
  time?: number
}
const latestNotification = ref<NotificationItem | null>(null)

// 生成初始资金曲线
function generateInitialFundData(): FundPoint[] {
  const result: FundPoint[] = []
  const now = Date.now()
  let value = 90000
  for (let i = 30; i >= 0; i--) {
    const time = now - i * 24 * 60 * 60 * 1000
    value += (Math.random() - 0.4) * 2000
    result.push({ time, value: Math.max(value, 50000) })
  }
  // 最后一个点对齐当前总资产
  result[result.length - 1].value = tradingStore.totalBalance
  return result
}

// 生成初始资产分布
function generateInitialAssetData(): AssetItem[] {
  return [
    { name: 'USDT', value: tradingStore.availableBalance },
    { name: 'BTC', value: 33750 },
    { name: 'ETH', value: 35200 },
    { name: 'SOL', value: 14200 }
  ]
}

// ============ WebSocket 订阅回调 ============

function onBalanceUpdate(data: any) {
  if (!data) return
  if (data.total_balance !== undefined) {
    tradingStore.totalBalance = Number(data.total_balance)
  }
  if (data.available_balance !== undefined) {
    tradingStore.availableBalance = Number(data.available_balance)
  }
  // 追加资金曲线点
  if (data.total_balance !== undefined) {
    fundChartData.value.push({
      time: Date.now(),
      value: Number(data.total_balance)
    })
    if (fundChartData.value.length > 200) fundChartData.value.shift()
  }
  // 更新资产分布
  if (data.assets && Array.isArray(data.assets)) {
    assetPieData.value = data.assets.map((a: any) => ({
      name: a.symbol ?? a.name,
      value: Number(a.value ?? a.amount ?? 0)
    }))
  }
}

function onPositionUpdate(data: any) {
  if (!data) return
  const posId = Number(data.id ?? data.position_id ?? 0)
  if (!posId) return
  const pos = tradingStore.positions.find(p => p.id === posId)
  if (pos) {
    if (data.current_price !== undefined) pos.currentPrice = Number(data.current_price)
    if (data.pnl !== undefined) pos.pnl = Number(data.pnl)
    if (data.pnl_percent !== undefined) pos.pnlPercent = Number(data.pnl_percent)
  }
}

function onNotification(data: any) {
  if (!data) return
  latestNotification.value = {
    title: data.title ?? '通知',
    message: data.message ?? data.content ?? '',
    level: data.level ?? 'info',
    time: Number(data.time ?? data.timestamp ?? Date.now())
  }
  // 5秒后自动消失
  setTimeout(() => {
    latestNotification.value = null
  }, 5000)
}

// ============ 订阅管理 ============

const subscriptions: Array<{ channel: string; callback: (data: any) => void }> = []

function subscribeAll() {
  subscribe('balance_update', onBalanceUpdate)
  subscribe('position_update', onPositionUpdate)
  subscribe('notification', onNotification)
  subscriptions.push({ channel: 'balance_update', callback: onBalanceUpdate })
  subscriptions.push({ channel: 'position_update', callback: onPositionUpdate })
  subscriptions.push({ channel: 'notification', callback: onNotification })
}

function unsubscribeAll() {
  subscriptions.forEach(({ channel, callback }) => {
    try {
      unsubscribe(channel, callback)
    } catch (e) {
      console.error(`[Dashboard] 取消订阅失败: ${channel}`, e)
    }
  })
  subscriptions.length = 0
}

onMounted(() => {
  fundChartData.value = generateInitialFundData()
  assetPieData.value = generateInitialAssetData()
  subscribeAll()
})

onBeforeUnmount(() => {
  unsubscribeAll()
})
</script>

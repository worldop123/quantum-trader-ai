<template>
  <div class="space-y-6">
    <!-- Stats Overview -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">运行策略</p>
          <Play class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold text-gray-200">
          <NumberTicker
            :value="runningCount"
            :decimals="0"
            :flash-on-change="true"
            up-color="#00ff88"
            down-color="#ff4757"
            neutral-color="#e4e7ed"
          />
          <span class="text-gray-500">/{{ totalCount }}</span>
        </p>
        <p class="text-xs text-gray-500 mt-1">AI 策略运行中</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">总收益</p>
          <TrendingUp class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold text-quantum-green font-mono">
          <NumberTicker
            :value="totalProfit"
            :decimals="2"
            prefix="$"
            :flash-on-change="true"
            up-color="#00ff88"
            down-color="#ff4757"
            neutral-color="#00ff88"
          />
        </p>
        <p class="text-xs text-quantum-green mt-1">累计收益</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">平均胜率</p>
          <Target class="w-5 h-5 text-quantum-cyan" />
        </div>
        <p class="text-2xl font-bold text-quantum-cyan font-mono">
          <NumberTicker
            :value="Number(avgWinRate)"
            :decimals="1"
            suffix="%"
            :flash-on-change="true"
            up-color="#00ff88"
            down-color="#ff4757"
            neutral-color="#00d4ff"
          />
        </p>
        <p class="text-xs text-gray-500 mt-1">策略平均胜率</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">总交易次数</p>
          <Zap class="w-5 h-5 text-quantum-yellow" />
        </div>
        <p class="text-2xl font-bold text-gray-200 font-mono">
          <NumberTicker
            :value="totalTrades"
            :decimals="0"
            :flash-on-change="true"
            up-color="#00ff88"
            down-color="#ff4757"
            neutral-color="#e4e7ed"
          />
        </p>
        <p class="text-xs text-gray-500 mt-1">累计执行交易</p>
      </div>
    </div>

    <!-- Strategy PnL Chart -->
    <div class="quantum-card">
      <StrategyPnlChart :data="pnlChartData" :initial-balance="10000" :height="300" />
    </div>

    <!-- Backtest Chart -->
    <div class="quantum-card">
      <BacktestChart :data="backtestChartData" :initial-balance="10000" :height="320" />
    </div>

    <!-- Strategy List -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-200">AI 策略列表</h3>
        <button class="quantum-btn-primary text-sm flex items-center gap-2">
          <Plus class="w-4 h-4" />
          创建策略
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="strategy in tradingStore.aiStrategies" :key="strategy.id"
          class="quantum-card hover:border-quantum-cyan/50 transition-colors">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h4 class="font-semibold text-gray-200">{{ strategy.name }}</h4>
              <p class="text-xs text-gray-500 mt-1">{{ strategy.type }}</p>
            </div>
            <span class="px-2 py-1 text-xs rounded-full"
              :class="{
                'bg-quantum-green/20 text-quantum-green': strategy.status === 'running',
                'bg-gray-500/20 text-gray-400': strategy.status === 'stopped',
                'bg-quantum-red/20 text-quantum-red': strategy.status === 'error'
              }">
              {{ statusLabels[strategy.status] }}
            </span>
          </div>

          <p class="text-sm text-gray-400 mb-4 line-clamp-2">{{ strategy.description }}</p>

          <div class="grid grid-cols-3 gap-2 mb-4 text-center">
            <div>
              <p class="text-lg font-bold text-quantum-cyan font-mono">{{ strategy.winRate }}%</p>
              <p class="text-xs text-gray-500">胜率</p>
            </div>
            <div>
              <p class="text-lg font-bold text-gray-300 font-mono">{{ strategy.totalTrades }}</p>
              <p class="text-xs text-gray-500">交易次数</p>
            </div>
            <div>
              <p class="text-lg font-bold font-mono" :class="strategy.profit >= 0 ? 'text-quantum-green' : 'text-quantum-red'">
                ${{ Math.abs(strategy.profit).toLocaleString() }}
              </p>
              <p class="text-xs text-gray-500">收益</p>
            </div>
          </div>

          <div class="flex gap-2">
            <button @click="toggleStrategy(strategy.id)"
              class="flex-1 py-2 rounded text-sm font-medium transition-colors"
              :class="strategy.status === 'running'
                ? 'bg-quantum-red/20 text-quantum-red hover:bg-quantum-red/30'
                : 'bg-quantum-green/20 text-quantum-green hover:bg-quantum-green/30'">
              {{ strategy.status === 'running' ? '停止' : '启动' }}
            </button>
            <button class="px-3 py-2 rounded bg-quantum-border text-gray-400 hover:bg-gray-700 transition-colors">
              <Settings class="w-4 h-4" />
            </button>
            <button class="px-3 py-2 rounded bg-quantum-border text-gray-400 hover:bg-gray-700 transition-colors">
              <BarChart3 class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Add Strategy Card -->
        <div class="quantum-card border-dashed flex flex-col items-center justify-center min-h-[240px] cursor-pointer hover:border-quantum-cyan/50 transition-colors">
          <div class="w-12 h-12 rounded-full bg-quantum-border flex items-center justify-center mb-3">
            <Plus class="w-6 h-6 text-gray-500" />
          </div>
          <p class="text-gray-400 font-medium">创建新策略</p>
          <p class="text-xs text-gray-600 mt-1">从模板或自定义创建</p>
        </div>
      </div>
    </div>

    <!-- Strategy Run Logs -->
    <div class="quantum-card">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-200">策略运行日志</h3>
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-quantum-green animate-pulse"></span>
          <span class="text-xs text-gray-400">实时更新</span>
        </div>
      </div>
      <div class="bg-quantum-darker rounded-lg p-4 h-64 overflow-auto font-mono text-xs space-y-1">
        <p v-for="(log, idx) in strategyLogs" :key="idx" class="text-gray-500">
          <span class="text-gray-600">[{{ log.time }}]</span>
          <span :class="logLevelClass(log.level)"> {{ log.level }} </span>
          <span class="text-gray-300">{{ log.message }}</span>
        </p>
        <p v-if="strategyLogs.length === 0" class="text-gray-600 text-center py-8">
          等待策略日志...
        </p>
      </div>
    </div>

    <!-- Strategy Templates -->
    <div class="quantum-card">
      <h3 class="text-lg font-semibold text-gray-200 mb-4">策略模板库</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="template in templates" :key="template.name"
          class="p-4 bg-quantum-darker rounded-lg border border-quantum-border hover:border-quantum-cyan/30 transition-colors cursor-pointer">
          <div class="w-10 h-10 rounded-lg bg-quantum-cyan/20 flex items-center justify-center mb-3">
            <component :is="template.icon" class="w-5 h-5 text-quantum-cyan" />
          </div>
          <h4 class="font-medium text-gray-200 mb-1">{{ template.name }}</h4>
          <p class="text-xs text-gray-500 line-clamp-2">{{ template.desc }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useTradingStore } from '../../stores/trading'
import { useWebSocket } from '../../utils/websocket'
import StrategyPnlChart from '../../components/charts/StrategyPnlChart.vue'
import BacktestChart from '../../components/charts/BacktestChart.vue'
import NumberTicker from '../../components/common/NumberTicker.vue'
import {
  Play,
  TrendingUp,
  Target,
  Zap,
  Plus,
  Settings,
  BarChart3,
  Grid3X3,
  TrendingUp as TrendIcon,
  RefreshCw,
  Layers
} from 'lucide-vue-next'
import { markRaw } from 'vue'

const tradingStore = useTradingStore()
const { subscribe, unsubscribe } = useWebSocket()

const statusLabels: Record<string, string> = {
  running: '运行中',
  stopped: '已停止',
  error: '异常'
}

const runningCount = computed(() =>
  tradingStore.aiStrategies.filter(s => s.status === 'running').length
)
const totalCount = computed(() => tradingStore.aiStrategies.length)

const totalProfit = computed(() =>
  tradingStore.aiStrategies.reduce((sum, s) => sum + s.profit, 0)
)

const avgWinRate = computed(() => {
  if (tradingStore.aiStrategies.length === 0) return '0.0'
  const total = tradingStore.aiStrategies.reduce((sum, s) => sum + s.winRate, 0)
  return (total / tradingStore.aiStrategies.length).toFixed(1)
})

const totalTrades = computed(() =>
  tradingStore.aiStrategies.reduce((sum, s) => sum + s.totalTrades, 0)
)

const templates = [
  { name: '网格交易', desc: '自动在价格区间内低买高卖', icon: markRaw(Grid3X3) },
  { name: '趋势追踪', desc: '跟随市场趋势进行交易', icon: markRaw(TrendIcon) },
  { name: '均值回归', desc: '捕捉价格偏离后的回归机会', icon: markRaw(RefreshCw) },
  { name: '套利策略', desc: '跨市场价差套利交易', icon: markRaw(Layers) }
]

// 策略收益曲线数据
interface PnlDataPoint {
  time: number
  pnl: number
  balance: number
}
const pnlChartData = ref<PnlDataPoint[]>([])

// 回测数据
interface BacktestDataPoint {
  time: number
  balance: number
  returnRate: number
  drawdown: number
}
const backtestChartData = ref<BacktestDataPoint[]>([])

// 策略运行日志
interface StrategyLog {
  time: string
  level: 'INFO' | 'WARN' | 'ERROR'
  message: string
}
const strategyLogs = ref<StrategyLog[]>([])

function logLevelClass(level: string): string {
  switch (level) {
    case 'INFO': return 'text-quantum-green'
    case 'WARN': return 'text-quantum-yellow'
    case 'ERROR': return 'text-quantum-red'
    default: return 'text-gray-400'
  }
}

function formatTime(time: number): string {
  const d = new Date(time)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`
}

// 生成初始策略收益曲线
function generateInitialPnlData(): PnlDataPoint[] {
  const result: PnlDataPoint[] = []
  const now = Date.now()
  let balance = 10000
  let pnl = 0
  for (let i = 60; i >= 0; i--) {
    const time = now - i * 60 * 60 * 1000
    const change = (Math.random() - 0.4) * 200
    balance += change
    pnl = balance - 10000
    result.push({ time, pnl, balance: Math.max(balance, 5000) })
  }
  // 最后一个点对齐当前总收益
  if (result.length > 0) {
    result[result.length - 1].pnl = totalProfit.value
    result[result.length - 1].balance = 10000 + totalProfit.value
  }
  return result
}

// 生成初始回测数据
function generateInitialBacktestData(): BacktestDataPoint[] {
  const result: BacktestDataPoint[] = []
  const now = Date.now()
  let balance = 10000
  let maxBalance = 10000
  for (let i = 90; i >= 0; i--) {
    const time = now - i * 24 * 60 * 60 * 1000
    const change = (Math.random() - 0.45) * 300
    balance += change
    if (balance > maxBalance) maxBalance = balance
    const returnRate = (balance - 10000) / 10000
    const drawdown = (maxBalance - balance) / maxBalance
    result.push({
      time,
      balance: Math.max(balance, 5000),
      returnRate,
      drawdown
    })
  }
  return result
}

// 生成初始日志
function generateInitialLogs(): StrategyLog[] {
  const now = Date.now()
  return [
    { time: formatTime(now - 1000), level: 'INFO', message: 'Quantum Grid Pro 执行买入 BTC 0.05' },
    { time: formatTime(now - 60000), level: 'INFO', message: 'Neural Trend Hunter 信号检测: 看多 ETH' },
    { time: formatTime(now - 120000), level: 'WARN', message: 'Mean Reversion Elite 价格波动较大,暂停交易' },
    { time: formatTime(now - 180000), level: 'INFO', message: 'Quantum Grid Pro 网格更新完成' },
    { time: formatTime(now - 240000), level: 'INFO', message: 'Neural Trend Hunter 执行卖出 ETH 2.0' }
  ]
}

// ============ WebSocket 订阅回调 ============

function onPositionUpdate(data: any) {
  if (!data) return
  // 更新策略持仓盈亏(将持仓盈亏累计到策略收益)
  const pnl = Number(data.pnl ?? 0)
  if (pnl !== 0 && pnlChartData.value.length > 0) {
    const last = pnlChartData.value[pnlChartData.value.length - 1]
    const newBalance = last.balance + pnl * 0.1 // 按比例计入策略收益
    pnlChartData.value.push({
      time: Date.now(),
      pnl: newBalance - 10000,
      balance: newBalance
    })
    if (pnlChartData.value.length > 300) pnlChartData.value.shift()
  }
}

function onNotification(data: any) {
  if (!data) return
  // 将通知作为策略日志
  const level = ((): 'INFO' | 'WARN' | 'ERROR' => {
    const lv = String(data.level ?? 'info').toLowerCase()
    if (lv === 'error') return 'ERROR'
    if (lv === 'warn' || lv === 'warning') return 'WARN'
    return 'INFO'
  })()
  const message = data.message ?? data.content ?? data.title ?? ''
  if (message) {
    strategyLogs.value.unshift({
      time: formatTime(Number(data.time ?? data.timestamp ?? Date.now())),
      level,
      message
    })
    if (strategyLogs.value.length > 100) strategyLogs.value.pop()
  }
}

// ============ 订阅管理 ============

const subscriptions: Array<{ channel: string; callback: (data: any) => void }> = []

function subscribeAll() {
  subscribe('position_update', onPositionUpdate)
  subscribe('notification', onNotification)
  subscriptions.push({ channel: 'position_update', callback: onPositionUpdate })
  subscriptions.push({ channel: 'notification', callback: onNotification })
}

function unsubscribeAll() {
  subscriptions.forEach(({ channel, callback }) => {
    try {
      unsubscribe(channel, callback)
    } catch (e) {
      console.error(`[AIStrategy] 取消订阅失败: ${channel}`, e)
    }
  })
  subscriptions.length = 0
}

function toggleStrategy(id: number) {
  tradingStore.toggleStrategy(id)
}

onMounted(() => {
  pnlChartData.value = generateInitialPnlData()
  backtestChartData.value = generateInitialBacktestData()
  strategyLogs.value = generateInitialLogs()
  subscribeAll()
})

onBeforeUnmount(() => {
  unsubscribeAll()
})
</script>

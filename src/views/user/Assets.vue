<template>
  <div class="space-y-6">
    <!-- Asset Overview Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">总资产估值</p>
          <Wallet class="w-5 h-5 text-quantum-cyan" />
        </div>
        <p class="text-2xl font-bold text-gray-200 font-mono">
          <NumberTicker
            :value="totalAssets"
            :decimals="2"
            prefix="$"
            :flash-on-change="true"
            up-color="#00ff88"
            down-color="#ff4757"
            neutral-color="#e4e7ed"
          />
        </p>
        <p class="text-xs mt-1" :class="totalPnl >= 0 ? 'text-quantum-green' : 'text-quantum-red'">
          {{ totalPnl >= 0 ? '+' : '' }}{{ totalPnlPercent }}% 今日
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
        <p class="text-xs text-gray-500 mt-1">USDT</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">持仓市值</p>
          <Briefcase class="w-5 h-5 text-quantum-purple" />
        </div>
        <p class="text-2xl font-bold text-gray-200 font-mono">
          <NumberTicker
            :value="positionValue"
            :decimals="2"
            prefix="$"
            :flash-on-change="true"
            up-color="#00ff88"
            down-color="#ff4757"
            neutral-color="#e4e7ed"
          />
        </p>
        <p class="text-xs text-gray-500 mt-1">{{ positionsCount }} 个持仓</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">累计盈亏</p>
          <TrendingUp class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold font-mono">
          <NumberTicker
            :value="totalPnl"
            :decimals="2"
            prefix="$"
            :show-sign="true"
            :flash-on-change="true"
            up-color="#00ff88"
            down-color="#ff4757"
            neutral-color="#e4e7ed"
          />
        </p>
        <p class="text-xs mt-1" :class="totalPnl >= 0 ? 'text-quantum-green' : 'text-quantum-red'">
          {{ totalPnl >= 0 ? '+' : '' }}{{ totalPnlPercent }}%
        </p>
      </div>
    </div>

    <!-- Asset Distribution & History -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 quantum-card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-200">资产明细</h3>
          <button class="text-sm text-quantum-cyan hover:underline">充值</button>
        </div>
        <div class="space-y-3">
          <div v-for="asset in assets" :key="asset.symbol"
            class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg hover:bg-quantum-border/30 transition-colors">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-quantum-border flex items-center justify-center">
                <span class="text-xs font-bold text-gray-400">{{ asset.symbol.substring(0, 2) }}</span>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-200">{{ asset.symbol }}</p>
                <p class="text-xs text-gray-500">{{ asset.name }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm font-mono text-gray-200">{{ asset.balance }}</p>
              <p class="text-xs text-gray-500">≈ ${{ asset.value.toLocaleString() }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="quantum-card">
        <AssetPieChart :data="assetPieData" :height="240" />
      </div>
    </div>

    <!-- Fund Curve -->
    <div class="quantum-card">
      <FundChart :data="fundChartData" :height="300" />
    </div>

    <!-- Transaction History -->
    <div class="quantum-card">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-200">资金流水</h3>
        <div class="flex gap-2">
          <select class="quantum-input w-28 text-sm">
            <option value="all">全部类型</option>
            <option value="deposit">充值</option>
            <option value="withdraw">提现</option>
            <option value="trade">交易</option>
          </select>
        </div>
      </div>
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-quantum-border text-gray-500 text-left">
            <th class="py-3 px-4 font-medium">时间</th>
            <th class="py-3 px-4 font-medium">类型</th>
            <th class="py-3 px-4 font-medium">币种</th>
            <th class="py-3 px-4 font-medium text-right">数量</th>
            <th class="py-3 px-4 font-medium">状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tx in transactions" :key="tx.id" class="border-b border-quantum-border/50">
            <td class="py-3 px-4 text-gray-500 text-xs">{{ tx.time }}</td>
            <td class="py-3 px-4">
              <span class="px-2 py-1 text-xs rounded"
                :class="{
                  'bg-quantum-green/20 text-quantum-green': tx.type === 'deposit',
                  'bg-quantum-red/20 text-quantum-red': tx.type === 'withdraw',
                  'bg-quantum-blue/20 text-quantum-blue': tx.type === 'trade'
                }">
                {{ tx.typeLabel }}
              </span>
            </td>
            <td class="py-3 px-4 text-gray-300">{{ tx.symbol }}</td>
            <td class="py-3 px-4 text-right font-mono" :class="tx.amount > 0 ? 'text-quantum-green' : 'text-quantum-red'">
              {{ tx.amount > 0 ? '+' : '' }}{{ tx.amount }}
            </td>
            <td class="py-3 px-4">
              <span class="text-xs text-quantum-green">已完成</span>
            </td>
          </tr>
        </tbody>
      </table>
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
  Briefcase,
  TrendingUp
} from 'lucide-vue-next'

const tradingStore = useTradingStore()
const { subscribe, unsubscribe } = useWebSocket()

const assets = ref([
  { symbol: 'USDT', name: 'Tether', balance: '75,000.00', value: 75000 },
  { symbol: 'BTC', name: 'Bitcoin', balance: '0.50000000', value: 33750 },
  { symbol: 'ETH', name: 'Ethereum', balance: '10.00000000', value: 35200 },
  { symbol: 'SOL', name: 'Solana', balance: '100.00000000', value: 14200 }
])

const transactions = [
  { id: 1, time: '2026-06-22 10:30:00', type: 'deposit', typeLabel: '充值', symbol: 'USDT', amount: 10000 },
  { id: 2, time: '2026-06-21 14:20:00', type: 'trade', typeLabel: '交易', symbol: 'ETH', amount: -5 },
  { id: 3, time: '2026-06-20 10:30:00', type: 'trade', typeLabel: '交易', symbol: 'BTC', amount: 0.5 },
  { id: 4, time: '2026-06-19 09:15:00', type: 'withdraw', typeLabel: '提现', symbol: 'USDT', amount: -5000 }
]

// 资金曲线数据
interface FundPoint { time: number; value: number }
const fundChartData = ref<FundPoint[]>([])

// 资产分布数据(供 AssetPieChart 使用)
interface AssetItem { name: string; value: number }
const assetPieData = ref<AssetItem[]>([])

const totalAssets = computed(() =>
  assets.value.reduce((sum, a) => sum + a.value, 0)
)

const positionValue = computed(() =>
  tradingStore.positions.reduce((sum, p) => sum + p.quantity * p.currentPrice, 0)
)

const positionsCount = computed(() => tradingStore.positions.length)

const totalPnl = computed(() => tradingStore.totalPnl)

const totalPnlPercent = computed(() => {
  const principal = tradingStore.totalBalance - tradingStore.totalPnl
  if (principal === 0) return '0.00'
  return ((tradingStore.totalPnl / principal) * 100).toFixed(2)
})

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
  result[result.length - 1].value = totalAssets.value
  return result
}

// 根据资产列表生成饼图数据
function buildPieDataFromAssets(): AssetItem[] {
  return assets.value.map(a => ({ name: a.symbol, value: a.value }))
}

// ============ WebSocket 订阅回调 ============

function onBalanceUpdate(data: any) {
  if (!data) return
  if (data.total_balance !== undefined) {
    tradingStore.totalBalance = Number(data.total_balance)
  }
  if (data.available_balance !== undefined) {
    tradingStore.availableBalance = Number(data.available_balance)
    // 同步更新 USDT 资产
    const usdt = assets.value.find(a => a.symbol === 'USDT')
    if (usdt) {
      usdt.value = Number(data.available_balance)
      usdt.balance = Number(data.available_balance).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }
  }
  // 追加资金曲线点
  if (data.total_balance !== undefined) {
    fundChartData.value.push({
      time: Date.now(),
      value: Number(data.total_balance)
    })
    if (fundChartData.value.length > 200) fundChartData.value.shift()
  }
  // 更新资产明细与饼图
  if (data.assets && Array.isArray(data.assets)) {
    const newAssets: typeof assets.value = []
    data.assets.forEach((a: any) => {
      const symbol = a.symbol ?? a.name ?? ''
      const value = Number(a.value ?? a.amount ?? 0)
      const balance = a.balance ?? String(value)
      newAssets.push({
        symbol,
        name: a.name ?? symbol,
        balance: String(balance),
        value
      })
    })
    if (newAssets.length > 0) {
      assets.value = newAssets
      assetPieData.value = buildPieDataFromAssets()
    }
  }
}

// ============ 订阅管理 ============

const subscriptions: Array<{ channel: string; callback: (data: any) => void }> = []

function subscribeAll() {
  subscribe('balance_update', onBalanceUpdate)
  subscriptions.push({ channel: 'balance_update', callback: onBalanceUpdate })
}

function unsubscribeAll() {
  subscriptions.forEach(({ channel, callback }) => {
    try {
      unsubscribe(channel, callback)
    } catch (e) {
      console.error(`[Assets] 取消订阅失败: ${channel}`, e)
    }
  })
  subscriptions.length = 0
}

onMounted(() => {
  fundChartData.value = generateInitialFundData()
  assetPieData.value = buildPieDataFromAssets()
  subscribeAll()
})

onBeforeUnmount(() => {
  unsubscribeAll()
})
</script>

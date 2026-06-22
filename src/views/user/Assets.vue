<template>
  <div class="space-y-6">
    <!-- Asset Overview Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">总资产估值</p>
          <Wallet class="w-5 h-5 text-quantum-cyan" />
        </div>
        <p class="text-2xl font-bold text-gray-200 font-mono">${{ totalAssets.toLocaleString() }}</p>
        <p class="text-xs text-quantum-green mt-1">+2.35% 今日</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">可用余额</p>
          <DollarSign class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold text-gray-200 font-mono">${{ tradingStore.availableBalance.toLocaleString() }}</p>
        <p class="text-xs text-gray-500 mt-1">USDT</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">持仓市值</p>
          <Briefcase class="w-5 h-5 text-quantum-purple" />
        </div>
        <p class="text-2xl font-bold text-gray-200 font-mono">${{ positionValue.toLocaleString() }}</p>
        <p class="text-xs text-gray-500 mt-1">{{ positionsCount }} 个持仓</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">累计盈亏</p>
          <TrendingUp class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold font-mono" :class="totalPnl >= 0 ? 'text-quantum-green' : 'text-quantum-red'">
          {{ totalPnl >= 0 ? '+' : '' }}${{ totalPnl.toLocaleString() }}
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
        <h3 class="text-lg font-semibold text-gray-200 mb-4">资产分布</h3>
        <div class="h-48 flex items-center justify-center bg-quantum-darker rounded-lg mb-4">
          <div class="text-center">
            <PieChart class="w-12 h-12 text-gray-600 mx-auto mb-2" />
            <p class="text-gray-500 text-sm">图表开发中</p>
          </div>
        </div>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-500">USDT</span>
            <span class="text-gray-300">75.0%</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">BTC</span>
            <span class="text-gray-300">15.5%</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">ETH</span>
            <span class="text-gray-300">6.8%</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">其他</span>
            <span class="text-gray-300">2.7%</span>
          </div>
        </div>
      </div>
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
import { computed } from 'vue'
import { useTradingStore } from '../../stores/trading'
import {
  Wallet,
  DollarSign,
  Briefcase,
  TrendingUp,
  PieChart
} from 'lucide-vue-next'

const tradingStore = useTradingStore()

const assets = [
  { symbol: 'USDT', name: 'Tether', balance: '75,000.00', value: 75000 },
  { symbol: 'BTC', name: 'Bitcoin', balance: '0.50000000', value: 33750 },
  { symbol: 'ETH', name: 'Ethereum', balance: '10.00000000', value: 35200 },
  { symbol: 'SOL', name: 'Solana', balance: '100.00000000', value: 14200 }
]

const transactions = [
  { id: 1, time: '2026-06-22 10:30:00', type: 'deposit', typeLabel: '充值', symbol: 'USDT', amount: 10000 },
  { id: 2, time: '2026-06-21 14:20:00', type: 'trade', typeLabel: '交易', symbol: 'ETH', amount: -5 },
  { id: 3, time: '2026-06-20 10:30:00', type: 'trade', typeLabel: '交易', symbol: 'BTC', amount: 0.5 },
  { id: 4, time: '2026-06-19 09:15:00', type: 'withdraw', typeLabel: '提现', symbol: 'USDT', amount: -5000 }
]

const totalAssets = computed(() => 
  assets.reduce((sum, a) => sum + a.value, 0)
)

const positionValue = computed(() => 
  tradingStore.positions.reduce((sum, p) => sum + p.quantity * p.currentPrice, 0)
)

const positionsCount = computed(() => tradingStore.positions.length)

const totalPnl = computed(() => tradingStore.totalPnl)

const totalPnlPercent = computed(() => 
  ((totalPnl.value / tradingStore.totalBalance) * 100).toFixed(2)
)
</script>

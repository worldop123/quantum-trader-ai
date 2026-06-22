<template>
  <div class="space-y-6">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">总资产</p>
          <Wallet class="w-5 h-5 text-quantum-cyan" />
        </div>
        <p class="text-2xl font-bold text-gray-200 font-mono">${{ tradingStore.totalBalance.toLocaleString() }}</p>
        <p class="text-xs text-quantum-green mt-1">+2.35% 今日</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">可用余额</p>
          <DollarSign class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold text-gray-200 font-mono">${{ tradingStore.availableBalance.toLocaleString() }}</p>
        <p class="text-xs text-gray-500 mt-1">75% 使用率</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">持仓盈亏</p>
          <TrendingUp class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold font-mono" :class="tradingStore.totalPnl >= 0 ? 'text-quantum-green' : 'text-quantum-red'">
          {{ tradingStore.totalPnl >= 0 ? '+' : '' }}${{ tradingStore.totalPnl.toLocaleString() }}
        </p>
        <p class="text-xs mt-1" :class="tradingStore.totalPnl >= 0 ? 'text-quantum-green' : 'text-quantum-red'">
          {{ tradingStore.totalPnl >= 0 ? '+' : '' }}{{ ((tradingStore.totalPnl / tradingStore.totalBalance) * 100).toFixed(2) }}%
        </p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">运行策略</p>
          <Brain class="w-5 h-5 text-quantum-purple" />
        </div>
        <p class="text-2xl font-bold text-gray-200 font-mono">{{ runningStrategies }}/{{ totalStrategies }}</p>
        <p class="text-xs text-quantum-purple mt-1">AI 策略运行中</p>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 quantum-card">
        <FundChart />
      </div>

      <div class="quantum-card">
        <AssetPieChart />
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
                {{ position.pnl >= 0 ? '+' : '' }}${{ position.pnl.toLocaleString() }}
              </p>
              <p class="text-xs" :class="position.pnlPercent >= 0 ? 'text-quantum-green' : 'text-quantum-red'">
                {{ position.pnlPercent >= 0 ? '+' : '' }}{{ position.pnlPercent }}%
              </p>
            </div>
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTradingStore } from '../../stores/trading'
import FundChart from '../../components/charts/FundChart.vue'
import AssetPieChart from '../../components/charts/AssetPieChart.vue'
import {
  Wallet,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Brain
} from 'lucide-vue-next'

const tradingStore = useTradingStore()

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
</script>

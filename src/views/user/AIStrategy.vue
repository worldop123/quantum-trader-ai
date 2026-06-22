<template>
  <div class="space-y-6">
    <!-- Stats Overview -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">运行策略</p>
          <Play class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold text-gray-200">{{ runningCount }}/{{ totalCount }}</p>
        <p class="text-xs text-gray-500 mt-1">AI 策略运行中</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">总收益</p>
          <TrendingUp class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold text-quantum-green font-mono">${{ totalProfit.toLocaleString() }}</p>
        <p class="text-xs text-quantum-green mt-1">累计收益</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">平均胜率</p>
          <Target class="w-5 h-5 text-quantum-cyan" />
        </div>
        <p class="text-2xl font-bold text-quantum-cyan font-mono">{{ avgWinRate }}%</p>
        <p class="text-xs text-gray-500 mt-1">策略平均胜率</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">总交易次数</p>
          <Zap class="w-5 h-5 text-quantum-yellow" />
        </div>
        <p class="text-2xl font-bold text-gray-200 font-mono">{{ totalTrades.toLocaleString() }}</p>
        <p class="text-xs text-gray-500 mt-1">累计执行交易</p>
      </div>
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
import { computed, markRaw } from 'vue'
import { useTradingStore } from '../../stores/trading'
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

const tradingStore = useTradingStore()

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

function toggleStrategy(id: number) {
  tradingStore.toggleStrategy(id)
}
</script>

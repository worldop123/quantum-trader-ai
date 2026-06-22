<template>
  <div class="space-y-6">
    <!-- Stats Overview -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">总用户数</p>
          <Users class="w-5 h-5 text-quantum-purple" />
        </div>
        <p class="text-2xl font-bold text-gray-200">12,847</p>
        <p class="text-xs text-quantum-green mt-1">+128 今日新增</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">总交易量</p>
          <TrendingUp class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold text-gray-200 font-mono">$2.4B</p>
        <p class="text-xs text-quantum-green mt-1">+15.3% 较昨日</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">运行策略</p>
          <Brain class="w-5 h-5 text-quantum-cyan" />
        </div>
        <p class="text-2xl font-bold text-gray-200">3,421</p>
        <p class="text-xs text-gray-500 mt-1">AI 策略运行中</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">系统状态</p>
          <Activity class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold text-quantum-green">正常</p>
        <p class="text-xs text-gray-500 mt-1">99.97% 可用性</p>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="quantum-card">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">用户增长趋势</h3>
        <div class="h-64">
          <FundChart :data="userGrowthData" :height="240" />
        </div>
      </div>

      <div class="quantum-card">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">交易量分布</h3>
        <div class="h-64">
          <AssetPieChart :data="tradeVolumeData" :height="240" />
        </div>
      </div>
    </div>

    <!-- Recent Activity & Alerts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="quantum-card">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">最近注册用户</h3>
        <div class="space-y-3">
          <div v-for="user in recentUsers" :key="user.id" 
            class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-quantum-border flex items-center justify-center">
                <User class="w-4 h-4 text-gray-500" />
              </div>
              <div>
                <p class="text-sm font-medium text-gray-200">{{ user.username }}</p>
                <p class="text-xs text-gray-500">{{ user.email }}</p>
              </div>
            </div>
            <span class="text-xs text-gray-500">{{ user.time }}</span>
          </div>
        </div>
      </div>

      <div class="quantum-card">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">系统告警</h3>
        <div class="space-y-3">
          <div v-for="alert in alerts" :key="alert.id" 
            class="flex items-start gap-3 p-3 bg-quantum-darker rounded-lg">
            <div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0"
              :class="{
                'bg-quantum-red/20': alert.level === 'error',
                'bg-quantum-yellow/20': alert.level === 'warning',
                'bg-quantum-blue/20': alert.level === 'info'
              }">
              <AlertTriangle v-if="alert.level === 'warning'" class="w-4 h-4 text-quantum-yellow" />
              <XCircle v-else-if="alert.level === 'error'" class="w-4 h-4 text-quantum-red" />
              <Info v-else class="w-4 h-4 text-quantum-blue" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-200">{{ alert.title }}</p>
              <p class="text-xs text-gray-500 truncate">{{ alert.message }}</p>
            </div>
            <span class="text-xs text-gray-500 shrink-0">{{ alert.time }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import FundChart from '../../components/charts/FundChart.vue'
import AssetPieChart from '../../components/charts/AssetPieChart.vue'
import {
  Users,
  TrendingUp,
  Brain,
  Activity,
  User,
  AlertTriangle,
  XCircle,
  Info
} from 'lucide-vue-next'

// 用户增长趋势数据(累计用户数)
interface FundPoint { time: number; value: number }
const userGrowthData = ref<FundPoint[]>([])

// 交易量分布数据(按交易对)
interface AssetItem { name: string; value: number }
const tradeVolumeData = ref<AssetItem[]>([])

function generateUserGrowthData(): FundPoint[] {
  const result: FundPoint[] = []
  const now = Date.now()
  let users = 8000
  for (let i = 30; i >= 0; i--) {
    const time = now - i * 24 * 60 * 60 * 1000
    users += Math.floor(Math.random() * 200 + 50)
    result.push({ time, value: users })
  }
  // 最后一个点对齐展示的总用户数
  result[result.length - 1].value = 12847
  return result
}

onMounted(() => {
  userGrowthData.value = generateUserGrowthData()
  tradeVolumeData.value = [
    { name: 'BTC/USDT', value: 980000000 },
    { name: 'ETH/USDT', value: 620000000 },
    { name: 'SOL/USDT', value: 320000000 },
    { name: 'BNB/USDT', value: 240000000 },
    { name: 'XRP/USDT', value: 180000000 },
    { name: '其他', value: 60000000 }
  ]
})

const recentUsers = [
  { id: 1, username: 'user_001', email: 'user001@example.com', time: '2分钟前' },
  { id: 2, username: 'trader_pro', email: 'trader@example.com', time: '5分钟前' },
  { id: 3, username: 'crypto_fan', email: 'crypto@example.com', time: '12分钟前' },
  { id: 4, username: 'quantum_user', email: 'quantum@example.com', time: '25分钟前' },
  { id: 5, username: 'ai_trader', email: 'ai@example.com', time: '1小时前' }
]

const alerts = [
  { id: 1, level: 'warning', title: '高波动率警告', message: 'BTC 价格波动超过 5%', time: '10分钟前' },
  { id: 2, level: 'info', title: '系统维护通知', message: '将于本周日凌晨进行系统维护', time: '1小时前' },
  { id: 3, level: 'error', title: 'API 限流告警', message: '部分用户 API 请求频率超限', time: '2小时前' },
  { id: 4, level: 'info', title: '新功能上线', message: '期权交易功能已上线', time: '昨天' }
]
</script>

<template>
  <div class="space-y-6">
    <!-- System Status -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">API 服务</p>
          <Activity class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-xl font-bold text-quantum-green">正常</p>
        <p class="text-xs text-gray-500 mt-1">延迟: 12ms</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">撮合引擎</p>
          <Zap class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-xl font-bold text-quantum-green">正常</p>
        <p class="text-xs text-gray-500 mt-1">TPS: 12,450</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">数据库</p>
          <Database class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-xl font-bold text-quantum-green">正常</p>
        <p class="text-xs text-gray-500 mt-1">连接数: 234/500</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">AI 服务</p>
          <Brain class="w-5 h-5 text-quantum-cyan" />
        </div>
        <p class="text-xl font-bold text-quantum-cyan">运行中</p>
        <p class="text-xs text-gray-500 mt-1">GPU 使用率: 67%</p>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="quantum-card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-200">实时交易量</h3>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-quantum-green animate-pulse"></span>
            <span class="text-xs text-gray-400">实时</span>
          </div>
        </div>
        <div class="h-64">
          <FundChart :data="realtimeVolumeData" :height="240" />
        </div>
      </div>

      <div class="quantum-card">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">系统资源使用</h3>
        <div class="space-y-4">
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-400">CPU 使用率</span>
              <span class="text-gray-300 font-mono">45%</span>
            </div>
            <div class="h-2 bg-quantum-darker rounded-full overflow-hidden">
              <div class="h-full bg-quantum-cyan rounded-full" style="width: 45%"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-400">内存使用率</span>
              <span class="text-gray-300 font-mono">62%</span>
            </div>
            <div class="h-2 bg-quantum-darker rounded-full overflow-hidden">
              <div class="h-full bg-quantum-green rounded-full" style="width: 62%"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-400">磁盘使用率</span>
              <span class="text-gray-300 font-mono">38%</span>
            </div>
            <div class="h-2 bg-quantum-darker rounded-full overflow-hidden">
              <div class="h-full bg-quantum-yellow rounded-full" style="width: 38%"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-400">网络带宽</span>
              <span class="text-gray-300 font-mono">23%</span>
            </div>
            <div class="h-2 bg-quantum-darker rounded-full overflow-hidden">
              <div class="h-full bg-quantum-purple rounded-full" style="width: 23%"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Real-time Logs -->
    <div class="quantum-card">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-200">实时日志</h3>
        <div class="flex gap-2">
          <select class="quantum-input w-28 text-sm">
            <option value="all">全部级别</option>
            <option value="error">Error</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>
          <button class="quantum-btn-secondary text-sm">导出日志</button>
        </div>
      </div>
      <div class="bg-quantum-darker rounded-lg p-4 h-64 overflow-auto font-mono text-xs space-y-1">
        <p class="text-gray-500">[2026-06-22 10:30:15] <span class="text-quantum-green">INFO</span> 用户 #10001 登录成功</p>
        <p class="text-gray-500">[2026-06-22 10:30:12] <span class="text-quantum-green">INFO</span> 订单 #1002 撮合成功</p>
        <p class="text-gray-500">[2026-06-22 10:30:08] <span class="text-quantum-yellow">WARN</span> BTC 价格波动超过 3%</p>
        <p class="text-gray-500">[2026-06-22 10:30:05] <span class="text-quantum-green">INFO</span> AI 策略 #1 执行买入操作</p>
        <p class="text-gray-500">[2026-06-22 10:30:01] <span class="text-quantum-green">INFO</span> 系统心跳检测正常</p>
        <p class="text-gray-500">[2026-06-22 10:29:58] <span class="text-quantum-green">INFO</span> 用户 #10005 注册成功</p>
        <p class="text-gray-500">[2026-06-22 10:29:55] <span class="text-quantum-red">ERROR</span> API 请求超时 (重试中...)</p>
        <p class="text-gray-500">[2026-06-22 10:29:52] <span class="text-quantum-green">INFO</span> 数据库备份完成</p>
        <p class="text-gray-500">[2026-06-22 10:29:48] <span class="text-quantum-green">INFO</span> 撮合引擎处理 1,234 笔订单</p>
        <p class="text-gray-500">[2026-06-22 10:29:45] <span class="text-quantum-yellow">WARN</span> 内存使用率接近阈值</p>
        <p class="text-gray-500">[2026-06-22 10:29:40] <span class="text-quantum-green">INFO</span> AI 模型推理完成</p>
        <p class="text-gray-500">[2026-06-22 10:29:35] <span class="text-quantum-green">INFO</span> 缓存刷新完成</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import FundChart from '../../components/charts/FundChart.vue'
import { useWebSocket } from '../../utils/websocket'
import { Activity, Zap, Database, Brain } from 'lucide-vue-next'

const { subscribe, unsubscribe } = useWebSocket()

// 实时交易量数据
interface VolumePoint { time: number; value: number }
const realtimeVolumeData = ref<VolumePoint[]>([])

// 生成初始实时交易量数据
function generateInitialVolumeData(): VolumePoint[] {
  const result: VolumePoint[] = []
  const now = Date.now()
  let volume = 1200000
  for (let i = 60; i >= 0; i--) {
    const time = now - i * 60 * 1000
    volume += Math.floor((Math.random() - 0.5) * 200000)
    result.push({ time, value: Math.max(volume, 500000) })
  }
  return result
}

// 定时模拟实时数据(降级方案:WebSocket 未连接时也能展示动态效果)
let simulateTimer: ReturnType<typeof setInterval> | null = null

function startSimulation() {
  simulateTimer = setInterval(() => {
    const last = realtimeVolumeData.value[realtimeVolumeData.value.length - 1]
    const newVolume = (last ? last.value : 1200000) + Math.floor((Math.random() - 0.5) * 200000)
    realtimeVolumeData.value.push({
      time: Date.now(),
      value: Math.max(newVolume, 500000)
    })
    if (realtimeVolumeData.value.length > 120) realtimeVolumeData.value.shift()
  }, 5000)
}

function stopSimulation() {
  if (simulateTimer) {
    clearInterval(simulateTimer)
    simulateTimer = null
  }
}

// ============ WebSocket 订阅回调 ============

function onTradeUpdate(data: any) {
  if (!data) return
  // 根据逐笔成交累计实时交易量
  const amount = Number(data.price ?? 0) * Number(data.quantity ?? data.size ?? 0)
  if (amount > 0) {
    const last = realtimeVolumeData.value[realtimeVolumeData.value.length - 1]
    const now = Date.now()
    if (last && now - last.time < 60000) {
      // 同一分钟内累计
      last.value += amount
    } else {
      realtimeVolumeData.value.push({ time: now, value: amount })
      if (realtimeVolumeData.value.length > 120) realtimeVolumeData.value.shift()
    }
  }
}

function onNotification(data: any) {
  if (!data) return
  // 通知可作为系统监控事件,此处仅用于触发数据刷新
}

// ============ 订阅管理 ============

const subscriptions: Array<{ channel: string; callback: (data: any) => void }> = []

function subscribeAll() {
  subscribe('trade:BTC-USDT', onTradeUpdate)
  subscribe('notification', onNotification)
  subscriptions.push({ channel: 'trade:BTC-USDT', callback: onTradeUpdate })
  subscriptions.push({ channel: 'notification', callback: onNotification })
}

function unsubscribeAll() {
  subscriptions.forEach(({ channel, callback }) => {
    try {
      unsubscribe(channel, callback)
    } catch (e) {
      console.error(`[DataMonitoring] 取消订阅失败: ${channel}`, e)
    }
  })
  subscriptions.length = 0
}

onMounted(() => {
  realtimeVolumeData.value = generateInitialVolumeData()
  subscribeAll()
  // 启动降级模拟(WebSocket 无数据时保持图表动态)
  startSimulation()
})

onBeforeUnmount(() => {
  unsubscribeAll()
  stopSimulation()
})
</script>

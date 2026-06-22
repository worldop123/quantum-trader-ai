<template>
  <div class="strategy-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="time-range-tabs">
        <button
          v-for="range in timeRanges"
          :key="range.value"
          :class="['tab-btn', { active: currentRange === range.value }]"
          @click="handleRangeChange(range.value)"
        >
          {{ range.label }}
        </button>
      </div>
    </div>
    <div class="chart-summary">
      <div class="summary-item">
        <span class="label">总收益</span>
        <span class="value" :class="{ positive: totalPnl >= 0, negative: totalPnl < 0 }">
          {{ totalPnl >= 0 ? '+' : '' }}{{ totalPnl.toFixed(2) }} USDT
        </span>
      </div>
      <div class="summary-item">
        <span class="label">收益率</span>
        <span class="value" :class="{ positive: totalReturn >= 0, negative: totalReturn < 0 }">
          {{ totalReturn >= 0 ? '+' : '' }}{{ totalReturn.toFixed(2) }}%
        </span>
      </div>
      <div class="summary-item">
        <span class="label">最大回撤</span>
        <span class="value negative">-{{ maxDrawdown.toFixed(2) }}%</span>
      </div>
    </div>
    <div ref="chartRef" class="chart-container"></div>
    <div v-if="loading" class="chart-loading">
      <Skeleton variant="chart" :rows="1" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import Skeleton from '@/components/common/Skeleton.vue'

interface PnlDataPoint {
  time: number
  pnl: number
  balance: number
}

interface Props {
  title?: string
  data?: PnlDataPoint[]
  loading?: boolean
  height?: number
  initialBalance?: number
}

const props = withDefaults(defineProps<Props>(), {
  title: '策略收益曲线',
  data: () => [],
  loading: false,
  height: 300,
  initialBalance: 10000,
})

const emit = defineEmits<{
  (e: 'rangeChange', range: string): void
}>()

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const currentRange = ref('all')

const timeRanges = [
  { label: '1天', value: '1d' },
  { label: '7天', value: '7d' },
  { label: '30天', value: '30d' },
  { label: '全部', value: 'all' },
]

const totalPnl = computed(() => {
  if (!props.data || props.data.length === 0) return 0
  return props.data[props.data.length - 1].pnl
})

const totalReturn = computed(() => {
  if (!props.initialBalance) return 0
  return (totalPnl.value / props.initialBalance) * 100
})

const maxDrawdown = computed(() => {
  if (!props.data || props.data.length < 2) return 0

  let maxBalance = props.data[0].balance
  let maxDrawdown = 0

  for (const point of props.data) {
    if (point.balance > maxBalance) {
      maxBalance = point.balance
    }
    const drawdown = ((maxBalance - point.balance) / maxBalance) * 100
    if (drawdown > maxDrawdown) {
      maxDrawdown = drawdown
    }
  }

  return maxDrawdown
})

function initChart() {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value, 'dark')

  const option = {
    backgroundColor: 'transparent',
    grid: {
      left: '3%',
      right: '4%',
      bottom: '8%',
      top: '5%',
      containLabel: true,
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(20, 25, 35, 0.95)',
      borderColor: '#2a3441',
      borderWidth: 1,
      textStyle: {
        color: '#fff',
        fontSize: 12,
      },
      formatter: function (params: any) {
        const data = params[0]
        const date = new Date(data.value[0])
        const dateStr = `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
        const pnl = data.value[1].toFixed(2)
        const balance = data.value[2].toFixed(2)
        return `<div style="padding: 4px;">
          <div style="color: #8892a6; margin-bottom: 4px;">${dateStr}</div>
          <div style="color: ${data.value[1] >= 0 ? '#00ff88' : '#ff4757'}; font-weight: 600;">
            ${data.value[1] >= 0 ? '+' : ''}${pnl} USDT
          </div>
          <div style="color: #8892a6; margin-top: 2px;">
            权益: ${balance} USDT
          </div>
        </div>`
      },
    },
    xAxis: {
      type: 'time',
      axisLine: {
        lineStyle: {
          color: '#2a3441',
        },
      },
      axisLabel: {
        color: '#8892a6',
        fontSize: 10,
      },
      splitLine: {
        show: false,
      },
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false,
      },
      axisLabel: {
        color: '#8892a6',
        fontSize: 10,
        formatter: function (value: number) {
          return value >= 0 ? `+${value.toFixed(0)}` : value.toFixed(0)
        },
      },
      splitLine: {
        lineStyle: {
          color: '#1e2530',
          type: 'dashed',
        },
      },
    },
    series: [
      {
        name: '累计收益',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: '#00d4ff',
          width: 2,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.02)' },
          ]),
        },
        data: [],
      },
    ],
  }

  chartInstance.setOption(option)
}

function updateChart() {
  if (!chartInstance || !props.data || props.data.length === 0) return

  const chartData = props.data.map((point) => [point.time, point.pnl, point.balance])

  chartInstance.setOption({
    series: [
      {
        data: chartData,
      },
    ],
  })
}

function handleRangeChange(range: string) {
  currentRange.value = range
  emit('rangeChange', range)
}

function handleResize() {
  if (chartInstance) {
    chartInstance.resize()
  }
}

watch(() => props.data, () => {
  nextTick(() => {
    updateChart()
  })
}, { deep: true })

watch(() => props.loading, () => {
  if (!props.loading && chartInstance) {
    nextTick(() => {
      chartInstance.resize()
    })
  }
})

onMounted(() => {
  nextTick(() => {
    initChart()
    updateChart()
  })
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  window.removeEventListener('resize', handleResize)
})

// 暴露方法
defineExpose({
  resize: handleResize,
})
</script>

<style scoped>
.strategy-chart {
  width: 100%;
  height: 100%;
  position: relative;
  background: linear-gradient(135deg, rgba(20, 25, 35, 0.8) 0%, rgba(15, 20, 30, 0.9) 100%);
  border: 1px solid #2a3441;
  border-radius: 12px;
  padding: 16px;
  box-sizing: border-box;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chart-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #e4e7ed;
}

.time-range-tabs {
  display: flex;
  gap: 4px;
  background: rgba(42, 52, 65, 0.5);
  padding: 2px;
  border-radius: 6px;
}

.tab-btn {
  padding: 4px 10px;
  font-size: 11px;
  color: #8892a6;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: #e4e7ed;
}

.tab-btn.active {
  background: #00d4ff;
  color: #0f1419;
  font-weight: 600;
}

.chart-summary {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #2a3441;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-item .label {
  font-size: 11px;
  color: #8892a6;
}

.summary-item .value {
  font-size: 16px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.summary-item .value.positive {
  color: #00ff88;
}

.summary-item .value.negative {
  color: #ff4757;
}

.chart-container {
  width: 100%;
  height: v-bind('height + "px"');
}

.chart-loading {
  position: absolute;
  top: 80px;
  left: 16px;
  right: 16px;
  bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>

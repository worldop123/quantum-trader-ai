<template>
  <div class="backtest-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
    </div>
    <div class="metrics-bar">
      <div class="metric-item">
        <span class="metric-label">总收益率</span>
        <span class="metric-value" :class="{ positive: totalReturn >= 0, negative: totalReturn < 0 }">
          {{ totalReturn >= 0 ? '+' : '' }}{{ totalReturn.toFixed(2) }}%
        </span>
      </div>
      <div class="metric-item">
        <span class="metric-label">年化收益</span>
        <span class="metric-value" :class="{ positive: annualizedReturn >= 0, negative: annualizedReturn < 0 }">
          {{ annualizedReturn >= 0 ? '+' : '' }}{{ annualizedReturn.toFixed(2) }}%
        </span>
      </div>
      <div class="metric-item">
        <span class="metric-label">最大回撤</span>
        <span class="metric-value negative">-{{ maxDrawdown.toFixed(2) }}%</span>
      </div>
      <div class="metric-item">
        <span class="metric-label">夏普比率</span>
        <span class="metric-value">{{ sharpeRatio.toFixed(2) }}</span>
      </div>
      <div class="metric-item">
        <span class="metric-label">胜率</span>
        <span class="metric-value">{{ winRate.toFixed(1) }}%</span>
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

interface BacktestDataPoint {
  time: number
  balance: number
  returnRate: number
  drawdown: number
}

interface Props {
  title?: string
  data?: BacktestDataPoint[]
  loading?: boolean
  height?: number
  initialBalance?: number
  metrics?: {
    totalReturn?: number
    annualizedReturn?: number
    maxDrawdown?: number
    sharpeRatio?: number
    winRate?: number
  }
}

const props = withDefaults(defineProps<Props>(), {
  title: '回测收益曲线',
  data: () => [],
  loading: false,
  height: 350,
  initialBalance: 10000,
  metrics: () => ({}),
})

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const totalReturn = computed(() => {
  if (props.metrics?.totalReturn !== undefined) return props.metrics.totalReturn
  if (!props.data || props.data.length === 0) return 0
  return props.data[props.data.length - 1].returnRate * 100
})

const annualizedReturn = computed(() => {
  if (props.metrics?.annualizedReturn !== undefined) return props.metrics.annualizedReturn
  return 0
})

const maxDrawdown = computed(() => {
  if (props.metrics?.maxDrawdown !== undefined) return props.metrics.maxDrawdown
  if (!props.data || props.data.length < 2) return 0

  let maxBalance = props.data[0].balance
  let maxDd = 0

  for (const point of props.data) {
    if (point.balance > maxBalance) {
      maxBalance = point.balance
    }
    const dd = ((maxBalance - point.balance) / maxBalance) * 100
    if (dd > maxDd) {
      maxDd = dd
    }
  }

  return maxDd
})

const sharpeRatio = computed(() => {
  if (props.metrics?.sharpeRatio !== undefined) return props.metrics.sharpeRatio
  return 0
})

const winRate = computed(() => {
  if (props.metrics?.winRate !== undefined) return props.metrics.winRate
  return 0
})

function initChart() {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value, 'dark')

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(20, 25, 35, 0.95)',
      borderColor: '#2a3441',
      borderWidth: 1,
      textStyle: {
        color: '#fff',
        fontSize: 12,
      },
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: '#2a3441',
        },
      },
    },
    legend: {
      data: ['收益率', '回撤'],
      top: 0,
      right: 10,
      textStyle: {
        color: '#8892a6',
        fontSize: 11,
      },
    },
    grid: [
      {
        left: '3%',
        right: '4%',
        top: '10%',
        height: '55%',
        containLabel: true,
      },
      {
        left: '3%',
        right: '4%',
        top: '72%',
        height: '20%',
        containLabel: true,
      },
    ],
    xAxis: [
      {
        type: 'time',
        gridIndex: 0,
        axisLine: {
          lineStyle: {
            color: '#2a3441',
          },
        },
        axisLabel: {
          show: false,
        },
        axisTick: {
          show: false,
        },
        splitLine: {
          show: false,
        },
      },
      {
        type: 'time',
        gridIndex: 1,
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
    ],
    yAxis: [
      {
        type: 'value',
        gridIndex: 0,
        axisLine: {
          show: false,
        },
        axisLabel: {
          color: '#8892a6',
          fontSize: 10,
          formatter: function (value: number) {
            return value >= 0 ? `+${value.toFixed(1)}%` : `${value.toFixed(1)}%`
          },
        },
        splitLine: {
          lineStyle: {
            color: '#1e2530',
            type: 'dashed',
          },
        },
      },
      {
        type: 'value',
        gridIndex: 1,
        inverse: true,
        axisLine: {
          show: false,
        },
        axisLabel: {
          color: '#8892a6',
          fontSize: 10,
          formatter: function (value: number) {
            return `-${value.toFixed(1)}%`
          },
        },
        splitLine: {
          lineStyle: {
            color: '#1e2530',
            type: 'dashed',
          },
        },
      },
    ],
    series: [
      {
        name: '收益率',
        type: 'line',
        xAxisIndex: 0,
        yAxisIndex: 0,
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
      {
        name: '回撤',
        type: 'line',
        xAxisIndex: 1,
        yAxisIndex: 1,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: '#ff4757',
          width: 1.5,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 71, 87, 0.4)' },
            { offset: 1, color: 'rgba(255, 71, 87, 0.02)' },
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

  const returnData = props.data.map((point) => [point.time, point.returnRate * 100])
  const drawdownData = props.data.map((point) => [point.time, point.drawdown * 100])

  chartInstance.setOption({
    series: [
      {
        data: returnData,
      },
      {
        data: drawdownData,
      },
    ],
  })
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
.backtest-chart {
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
  margin-bottom: 12px;
}

.chart-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #e4e7ed;
}

.metrics-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 12px;
  padding: 12px;
  background: rgba(42, 52, 65, 0.3);
  border-radius: 8px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 80px;
}

.metric-label {
  font-size: 11px;
  color: #8892a6;
}

.metric-value {
  font-size: 15px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.metric-value.positive {
  color: #00ff88;
}

.metric-value.negative {
  color: #ff4757;
}

.chart-container {
  width: 100%;
  height: v-bind('height + "px"');
}

.chart-loading {
  position: absolute;
  top: 100px;
  left: 16px;
  right: 16px;
  bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>

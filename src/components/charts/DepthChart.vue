<template>
  <div class="depth-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="depth-summary">
        <div class="bid-summary">
          <span class="label">买一</span>
          <span class="price bid-price">{{ bidPrice }}</span>
          <span class="amount">{{ bidAmount }}</span>
        </div>
        <div class="ask-summary">
          <span class="label">卖一</span>
          <span class="price ask-price">{{ askPrice }}</span>
          <span class="amount">{{ askAmount }}</span>
        </div>
      </div>
    </div>
    <div ref="chartRef" class="chart-container"></div>
    <div v-if="loading" class="chart-loading">
      <Skeleton variant="chart" :rows="1" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import Skeleton from '@/components/common/Skeleton.vue'

interface DepthData {
  bids: Array<[number, number]> // [价格, 数量]
  asks: Array<[number, number]>
}

interface Props {
  title?: string
  data?: DepthData
  loading?: boolean
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  title: '深度图',
  data: () => ({ bids: [], asks: [] }),
  loading: false,
  height: 250,
})

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const bidPrice = ref('0.00')
const askPrice = ref('0.00')
const bidAmount = ref('0.00')
const askAmount = ref('0.00')

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
        const price = data.value[0].toFixed(2)
        const amount = data.value[1].toFixed(4)
        const total = data.value[2] ? data.value[2].toFixed(4) : amount
        return `<div style="padding: 4px;">
          <div style="color: #8892a6; margin-bottom: 4px;">价格: ${price}</div>
          <div style="color: #e4e7ed;">数量: ${amount}</div>
          <div style="color: #8892a6; margin-top: 4px;">累计: ${total}</div>
        </div>`
      },
    },
    xAxis: {
      type: 'value',
      scale: true,
      axisLine: {
        lineStyle: {
          color: '#2a3441',
        },
      },
      axisLabel: {
        color: '#8892a6',
        fontSize: 10,
        formatter: function (value: number) {
          return value.toFixed(2)
        },
      },
      splitLine: {
        lineStyle: {
          color: '#1e2530',
          type: 'dashed',
        },
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
        name: '买盘',
        type: 'line',
        step: 'end',
        symbol: 'none',
        lineStyle: {
          color: '#00ff88',
          width: 1.5,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 255, 136, 0.4)' },
            { offset: 1, color: 'rgba(0, 255, 136, 0.02)' },
          ]),
        },
        data: [],
      },
      {
        name: '卖盘',
        type: 'line',
        step: 'start',
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
  if (!chartInstance || !props.data) return

  const bids = props.data.bids || []
  const asks = props.data.asks || []

  // 计算累计深度
  let bidTotal = 0
  const bidData = bids.map(([price, amount]) => {
    bidTotal += amount
    return [price, amount, bidTotal]
  })

  let askTotal = 0
  const askData = asks.map(([price, amount]) => {
    askTotal += amount
    return [price, amount, askTotal]
  })

  // 更新买一卖一
  if (bids.length > 0) {
    bidPrice.value = bids[0][0].toFixed(2)
    bidAmount.value = bids[0][1].toFixed(4)
  }
  if (asks.length > 0) {
    askPrice.value = asks[0][0].toFixed(2)
    askAmount.value = asks[0][1].toFixed(4)
  }

  chartInstance.setOption({
    series: [
      {
        data: bidData,
      },
      {
        data: askData,
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
.depth-chart {
  width: 100%;
  height: 100%;
  position: relative;
  background: linear-gradient(135deg, rgba(20, 25, 35, 0.8) 0%, rgba(15, 20, 30, 0.9) 100%);
  border: 1px solid #2a3441;
  border-radius: 12px;
  padding: 12px;
  box-sizing: border-box;
}

.chart-header {
  margin-bottom: 8px;
}

.chart-title {
  margin: 0 0 8px 0;
  font-size: 13px;
  font-weight: 600;
  color: #e4e7ed;
}

.depth-summary {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 11px;
}

.bid-summary,
.ask-summary {
  display: flex;
  align-items: center;
  gap: 6px;
}

.label {
  color: #8892a6;
}

.price {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.bid-price {
  color: #00ff88;
}

.ask-price {
  color: #ff4757;
}

.amount {
  color: #8892a6;
  font-variant-numeric: tabular-nums;
}

.chart-container {
  width: 100%;
  height: v-bind('height + "px"');
}

.chart-loading {
  position: absolute;
  top: 48px;
  left: 12px;
  right: 12px;
  bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>

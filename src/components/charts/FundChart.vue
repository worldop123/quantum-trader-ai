<template>
  <div class="fund-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="time-range-tabs">
        <button
          v-for="range in timeRanges"
          :key="range.value"
          :class="['tab-btn', { active: activeRange === range.value }]"
          @click="activeRange = range.value"
        >
          {{ range.label }}
        </button>
      </div>
    </div>
    <div ref="chartRef" class="chart-container"></div>
    <div v-if="loading" class="chart-loading">
      <Skeleton variant="chart" :rows="1" />
    </div>
    <div v-if="error" class="chart-error">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import Skeleton from '@/components/common/Skeleton.vue'

interface Props {
  title?: string
  data?: Array<{ time: number; value: number }>
  loading?: boolean
  error?: string
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  title: '资金曲线',
  data: () => [],
  loading: false,
  error: '',
  height: 300,
})

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const activeRange = ref('30d')

const timeRanges = [
  { label: '1天', value: '1d' },
  { label: '7天', value: '7d' },
  { label: '30天', value: '30d' },
  { label: '全部', value: 'all' },
]

function initChart() {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value, 'dark')

  const option = {
    backgroundColor: 'transparent',
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true,
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(20, 25, 35, 0.95)',
      borderColor: '#00d4ff',
      borderWidth: 1,
      textStyle: {
        color: '#fff',
        fontSize: 12,
      },
      formatter: function (params: any) {
        const data = params[0]
        const date = new Date(data.value[0])
        const dateStr = date.toLocaleDateString()
        const value = data.value[1].toFixed(2)
        return `<div style="padding: 4px;">
          <div style="color: #8892a6; margin-bottom: 4px;">${dateStr}</div>
          <div style="color: #00ff88; font-size: 14px; font-weight: bold;">${value} USDT</div>
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
        fontSize: 11,
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
        fontSize: 11,
        formatter: '{value}',
      },
      splitLine: {
        lineStyle: {
          color: '#1e2530',
          type: 'dashed',
        },
      },
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100,
      },
    ],
    series: [
      {
        name: '总资产',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: '#00d4ff',
          width: 2,
          shadowColor: 'rgba(0, 212, 255, 0.5)',
          shadowBlur: 10,
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

  const chartData = props.data.map((item) => [item.time, item.value])

  chartInstance.setOption({
    series: [
      {
        data: chartData,
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
.fund-chart {
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
}

.tab-btn {
  padding: 4px 10px;
  font-size: 12px;
  background: transparent;
  border: 1px solid #2a3441;
  border-radius: 6px;
  color: #8892a6;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  border-color: #00d4ff;
  color: #00d4ff;
}

.tab-btn.active {
  background: rgba(0, 212, 255, 0.15);
  border-color: #00d4ff;
  color: #00d4ff;
}

.chart-container {
  width: 100%;
  height: v-bind('height + "px"');
}

.chart-loading {
  position: absolute;
  top: 48px;
  left: 16px;
  right: 16px;
  bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #ff4757;
  font-size: 13px;
}
</style>

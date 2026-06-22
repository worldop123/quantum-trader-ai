<template>
  <div class="pie-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="total-value">
        <span class="label">总资产</span>
        <span class="value">{{ totalValue.toFixed(2) }} USDT</span>
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

interface AssetItem {
  name: string
  value: number
  color?: string
}

interface Props {
  title?: string
  data?: AssetItem[]
  loading?: boolean
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  title: '资产分布',
  data: () => [],
  loading: false,
  height: 280,
})

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const colors = [
  '#00d4ff',
  '#00ff88',
  '#ffc107',
  '#ff4757',
  '#a855f7',
  '#f97316',
  '#14b8a6',
  '#6366f1',
]

const totalValue = computed(() => {
  return props.data.reduce((sum, item) => sum + item.value, 0)
})

function initChart() {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value, 'dark')

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(20, 25, 35, 0.95)',
      borderColor: '#2a3441',
      borderWidth: 1,
      textStyle: {
        color: '#fff',
        fontSize: 12,
      },
      formatter: function (params: any) {
        const percent = params.percent.toFixed(1)
        const value = params.value.toFixed(2)
        return `<div style="padding: 4px;">
          <div style="color: #e4e7ed; font-weight: 600; margin-bottom: 4px;">${params.name}</div>
          <div style="color: #00d4ff;">${value} USDT</div>
          <div style="color: #8892a6; margin-top: 2px;">占比: ${percent}%</div>
        </div>`
      },
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 12,
      textStyle: {
        color: '#8892a6',
        fontSize: 11,
      },
      formatter: function (name: string) {
        const item = props.data.find((d) => d.name === name)
        if (item) {
          const percent = ((item.value / totalValue.value) * 100).toFixed(1)
          return `${name}  ${percent}%`
        }
        return name
      },
    },
    series: [
      {
        name: '资产分布',
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 4,
          borderColor: '#0f1419',
          borderWidth: 2,
        },
        label: {
          show: false,
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            color: '#fff',
          },
          itemStyle: {
            shadowBlur: 20,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
        labelLine: {
          show: false,
        },
        data: [],
      },
    ],
  }

  chartInstance.setOption(option)
}

function updateChart() {
  if (!chartInstance || !props.data || props.data.length === 0) return

  const chartData = props.data.map((item, index) => ({
    name: item.name,
    value: item.value,
    itemStyle: {
      color: item.color || colors[index % colors.length],
    },
  }))

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
.pie-chart {
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

.total-value {
  text-align: right;
}

.total-value .label {
  display: block;
  font-size: 11px;
  color: #8892a6;
  margin-bottom: 2px;
}

.total-value .value {
  font-size: 16px;
  font-weight: 700;
  color: #00d4ff;
  font-variant-numeric: tabular-nums;
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
</style>

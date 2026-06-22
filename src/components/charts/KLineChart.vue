<template>
  <div class="kline-chart">
    <!-- 指标切换栏 -->
    <div class="indicator-bar">
      <div class="indicator-tabs">
        <button
          v-for="ind in indicators"
          :key="ind.value"
          :class="['indicator-btn', { active: activeIndicator === ind.value }]"
          @click="activeIndicator = ind.value"
        >
          {{ ind.label }}
        </button>
      </div>
      <div class="timeframe-tabs">
        <button
          v-for="tf in timeframes"
          :key="tf.value"
          :class="['tf-btn', { active: timeframe === tf.value }]"
          @click="handleTimeframeChange(tf.value)"
        >
          {{ tf.label }}
        </button>
      </div>
    </div>

    <!-- 图表区域 -->
    <div ref="chartRef" class="chart-container">
      <div v-if="loading" class="chart-loading">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>
      <div v-else-if="error" class="chart-error">
        <span>{{ error }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import * as echarts from 'echarts'

interface KLineData {
  time: number
  open: number
  close: number
  low: number
  high: number
  volume: number
}

interface Props {
  data?: KLineData[]
  loading?: boolean
  error?: string
  symbol?: string
  timeframe?: string
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  loading: false,
  error: '',
  symbol: 'BTC-USDT',
  timeframe: '1h',
})

const emit = defineEmits<{
  (e: 'timeframeChange', timeframe: string): void
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

// 指标列表
const indicators = [
  { label: 'MA', value: 'ma' },
  { label: 'MACD', value: 'macd' },
  { label: 'RSI', value: 'rsi' },
  { label: 'BOLL', value: 'boll' },
]

const activeIndicator = ref('ma')

// 周期列表
const timeframes = [
  { label: '1分', value: '1m' },
  { label: '5分', value: '5m' },
  { label: '15分', value: '15m' },
  { label: '1时', value: '1h' },
  { label: '4时', value: '4h' },
  { label: '1日', value: '1d' },
  { label: '1周', value: '1w' },
]

// MA周期配置
const maPeriods = [5, 10, 20, 60]
const maColors = ['#f59e0b', '#8b5cf6', '#06b6d4', '#10b981']

// 计算MA均线
function calculateMA(data: KLineData[], period: number): (number | null)[] {
  const result: (number | null)[] = []
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null)
    } else {
      let sum = 0
      for (let j = 0; j < period; j++) {
        sum += data[i - j].close
      }
      result.push(sum / period)
    }
  }
  return result
}

// 计算MACD
function calculateMACD(data: KLineData[], fast = 12, slow = 26, signal = 9) {
  const closes = data.map((d) => d.close)

  // 计算EMA
  function calculateEMA(values: number[], period: number): number[] {
    const ema: number[] = []
    const multiplier = 2 / (period + 1)

    for (let i = 0; i < values.length; i++) {
      if (i === 0) {
        ema.push(values[i])
      } else {
        ema.push(values[i] * multiplier + ema[i - 1] * (1 - multiplier))
      }
    }
    return ema
  }

  const fastEMA = calculateEMA(closes, fast)
  const slowEMA = calculateEMA(closes, slow)

  // DIF (差离值)
  const dif: number[] = []
  for (let i = 0; i < closes.length; i++) {
    dif.push(fastEMA[i] - slowEMA[i])
  }

  // DEA (讯号线)
  const dea = calculateEMA(dif, signal)

  // MACD柱状图
  const macd: number[] = []
  for (let i = 0; i < closes.length; i++) {
    macd.push((dif[i] - dea[i]) * 2)
  }

  return { dif, dea, macd }
}

// 计算RSI
function calculateRSI(data: KLineData[], period = 14): (number | null)[] {
  const result: (number | null)[] = []
  const changes: number[] = []

  for (let i = 1; i < data.length; i++) {
    changes.push(data[i].close - data[i - 1].close)
  }

  for (let i = 0; i < data.length; i++) {
    if (i < period) {
      result.push(null)
    } else {
      let gains = 0
      let losses = 0

      for (let j = i - period + 1; j <= i; j++) {
        const change = changes[j - 1] || 0
        if (change > 0) {
          gains += change
        } else {
          losses += Math.abs(change)
        }
      }

      const avgGain = gains / period
      const avgLoss = losses / period

      if (avgLoss === 0) {
        result.push(100)
      } else {
        const rs = avgGain / avgLoss
        result.push(100 - 100 / (1 + rs))
      }
    }
  }

  return result
}

// 计算布林带
function calculateBollingerBands(data: KLineData[], period = 20, stdDev = 2) {
  const middle: (number | null)[] = []
  const upper: (number | null)[] = []
  const lower: (number | null)[] = []

  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      middle.push(null)
      upper.push(null)
      lower.push(null)
    } else {
      // 计算中轨（SMA）
      let sum = 0
      for (let j = 0; j < period; j++) {
        sum += data[i - j].close
      }
      const sma = sum / period
      middle.push(sma)

      // 计算标准差
      let varianceSum = 0
      for (let j = 0; j < period; j++) {
        varianceSum += Math.pow(data[i - j].close - sma, 2)
      }
      const stdDeviation = Math.sqrt(varianceSum / period)

      upper.push(sma + stdDev * stdDeviation)
      lower.push(sma - stdDev * stdDeviation)
    }
  }

  return { middle, upper, lower }
}

// 初始化图表
function initChart() {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value, 'dark')

  // 响应式
  const resizeObserver = new ResizeObserver(() => {
    chartInstance?.resize()
  })
  resizeObserver.observe(chartRef.value)
}

// 更新图表数据
function updateChart() {
  if (!chartInstance || !props.data || props.data.length === 0) return

  const data = props.data
  const dates = data.map((item) => {
    const date = new Date(item.time)
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
  })

  // 基础配置
  const option: any = {
    backgroundColor: 'transparent',
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
      backgroundColor: 'rgba(20, 25, 35, 0.95)',
      borderColor: '#00d4ff',
      borderWidth: 1,
      textStyle: {
        color: '#fff',
        fontSize: 12,
      },
    },
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 50,
        end: 100,
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        bottom: '2%',
        height: 16,
        start: 50,
        end: 100,
        borderColor: '#2a3441',
        fillerColor: 'rgba(0, 212, 255, 0.2)',
        handleStyle: {
          color: '#00d4ff',
        },
        textStyle: {
          color: '#8892a6',
          fontSize: 10,
        },
      },
    ],
  }

  // 根据指标类型配置不同的图表
  if (activeIndicator.value === 'ma') {
    updateMAChart(option, data, dates)
  } else if (activeIndicator.value === 'macd') {
    updateMACDChart(option, data, dates)
  } else if (activeIndicator.value === 'rsi') {
    updateRSIChart(option, data, dates)
  } else if (activeIndicator.value === 'boll') {
    updateBOLLChart(option, data, dates)
  }

  chartInstance.setOption(option, true)
}

// MA均线模式
function updateMAChart(option: any, data: KLineData[], dates: string[]) {
  // 计算MA均线
  const maData: Record<string, (number | null)[]> = {}
  maPeriods.forEach((period) => {
    maData[`MA${period}`] = calculateMA(data, period)
  })

  option.grid = [
    { left: '3%', right: '4%', top: '5%', height: '60%', containLabel: true },
    { left: '3%', right: '4%', top: '72%', height: '18%', containLabel: true },
  ]

  option.xAxis = [
    {
      type: 'category',
      data: dates,
      scale: true,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#2a3441' } },
      axisLabel: { color: '#8892a6', fontSize: 10 },
      splitLine: { show: false },
    },
    {
      type: 'category',
      gridIndex: 1,
      data: dates,
      scale: true,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#2a3441' } },
      axisLabel: { show: false },
      splitLine: { show: false },
    },
  ]

  option.yAxis = [
    {
      scale: true,
      splitNumber: 4,
      axisLine: { show: false },
      axisLabel: { color: '#8892a6', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e2530', type: 'dashed' } },
    },
    {
      scale: true,
      gridIndex: 1,
      splitNumber: 2,
      axisLine: { show: false },
      axisLabel: { color: '#8892a6', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e2530', type: 'dashed' } },
    },
  ]

  option.series = [
    {
      name: 'K线',
      type: 'candlestick',
      data: data.map((item) => [item.open, item.close, item.low, item.high, item.volume]),
      itemStyle: {
        color: '#00ff88',
        color0: '#ff4757',
        borderColor: '#00ff88',
        borderColor0: '#ff4757',
      },
    },
    // MA均线
    ...maPeriods.map((period, index) => ({
      name: `MA${period}`,
      type: 'line',
      data: maData[`MA${period}`],
      smooth: true,
      lineStyle: {
        width: 1,
        color: maColors[index],
      },
      showSymbol: false,
    })),
    {
      name: '成交量',
      type: 'bar',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: data.map((item, index) => ({
        value: item.volume,
        itemStyle: {
          color: index > 0 && data[index].close >= data[index - 1].close ? 'rgba(0, 255, 136, 0.6)' : 'rgba(255, 71, 87, 0.6)',
        },
      })),
    },
  ]

  // tooltip formatter
  option.tooltip.formatter = function (params: any) {
    const kline = params.find((p: any) => p.seriesName === 'K线')
    if (!kline) return ''

    const data = kline.data
    let html = `<div style="font-weight: 600; margin-bottom: 8px; color: #00d4ff;">${kline.axisValue}</div>`
    html += `<div style="display: flex; justify-content: space-between; gap: 20px;">`
    html += `<div>开盘: <span style="color: ${data[1] >= data[2] ? '#00ff88' : '#ff4757'}; font-weight: 600;">${data[1].toFixed(2)}</span></div>`
    html += `<div>收盘: <span style="color: ${data[1] >= data[2] ? '#00ff88' : '#ff4757'}; font-weight: 600;">${data[2].toFixed(2)}</span></div>`
    html += `</div>`
    html += `<div style="display: flex; justify-content: space-between; gap: 20px; margin-top: 4px;">`
    html += `<div>最低: <span style="color: #ff4757; font-weight: 600;">${data[3].toFixed(2)}</span></div>`
    html += `<div>最高: <span style="color: #00ff88; font-weight: 600;">${data[4].toFixed(2)}</span></div>`
    html += `</div>`
    html += `<div style="margin-top: 4px;">成交量: <span style="color: #e4e7ed;">${(data[5] / 1000).toFixed(2)}K</span></div>`

    // MA数据
    params.forEach((p: any) => {
      if (p.seriesName.startsWith('MA') && p.value !== null) {
        html += `<div style="margin-top: 4px; color: ${p.color};">${p.seriesName}: ${p.value.toFixed(2)}</div>`
      }
    })

    return html
  }
}

// MACD模式
function updateMACDChart(option: any, data: KLineData[], dates: string[]) {
  const macdData = calculateMACD(data)

  option.grid = [
    { left: '3%', right: '4%', top: '5%', height: '55%', containLabel: true },
    { left: '3%', right: '4%', top: '65%', height: '25%', containLabel: true },
  ]

  option.xAxis = [
    {
      type: 'category',
      data: dates,
      scale: true,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#2a3441' } },
      axisLabel: { color: '#8892a6', fontSize: 10 },
      splitLine: { show: false },
    },
    {
      type: 'category',
      gridIndex: 1,
      data: dates,
      scale: true,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#2a3441' } },
      axisLabel: { show: false },
      splitLine: { show: false },
    },
  ]

  option.yAxis = [
    {
      scale: true,
      splitNumber: 4,
      axisLine: { show: false },
      axisLabel: { color: '#8892a6', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e2530', type: 'dashed' } },
    },
    {
      scale: true,
      gridIndex: 1,
      splitNumber: 2,
      axisLine: { show: false },
      axisLabel: { color: '#8892a6', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e2530', type: 'dashed' } },
    },
  ]

  option.series = [
    {
      name: 'K线',
      type: 'candlestick',
      data: data.map((item) => [item.open, item.close, item.low, item.high, item.volume]),
      itemStyle: {
        color: '#00ff88',
        color0: '#ff4757',
        borderColor: '#00ff88',
        borderColor0: '#ff4757',
      },
    },
    // DIF线
    {
      name: 'DIF',
      type: 'line',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: macdData.dif,
      smooth: true,
      lineStyle: { width: 1.5, color: '#00d4ff' },
      showSymbol: false,
    },
    // DEA线
    {
      name: 'DEA',
      type: 'line',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: macdData.dea,
      smooth: true,
      lineStyle: { width: 1.5, color: '#f59e0b' },
      showSymbol: false,
    },
    // MACD柱状图
    {
      name: 'MACD',
      type: 'bar',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: macdData.macd.map((val) => ({
        value: val,
        itemStyle: {
          color: val >= 0 ? 'rgba(0, 255, 136, 0.7)' : 'rgba(255, 71, 87, 0.7)',
        },
      })),
    },
  ]

  option.tooltip.formatter = function (params: any) {
    const kline = params.find((p: any) => p.seriesName === 'K线')
    const dif = params.find((p: any) => p.seriesName === 'DIF')
    const dea = params.find((p: any) => p.seriesName === 'DEA')
    const macd = params.find((p: any) => p.seriesName === 'MACD')

    let html = `<div style="font-weight: 600; margin-bottom: 8px; color: #00d4ff;">${kline?.axisValue || ''}</div>`

    if (kline) {
      const d = kline.data
      html += `<div style="color: ${d[1] >= d[2] ? '#00ff88' : '#ff4757'}; font-weight: 600;">${d[2].toFixed(2)}</div>`
    }

    html += `<div style="margin-top: 8px; border-top: 1px solid #2a3441; padding-top: 8px;">`
    if (dif && dif.value !== null) {
      html += `<div style="color: #00d4ff;">DIF: ${dif.value.toFixed(4)}</div>`
    }
    if (dea && dea.value !== null) {
      html += `<div style="color: #f59e0b;">DEA: ${dea.value.toFixed(4)}</div>`
    }
    if (macd && macd.value !== null) {
      html += `<div style="color: ${macd.value >= 0 ? '#00ff88' : '#ff4757'};">MACD: ${macd.value.toFixed(4)}</div>`
    }
    html += `</div>`

    return html
  }
}

// RSI模式
function updateRSIChart(option: any, data: KLineData[], dates: string[]) {
  const rsi6 = calculateRSI(data, 6)
  const rsi14 = calculateRSI(data, 14)
  const rsi24 = calculateRSI(data, 24)

  option.grid = [
    { left: '3%', right: '4%', top: '5%', height: '55%', containLabel: true },
    { left: '3%', right: '4%', top: '65%', height: '25%', containLabel: true },
  ]

  option.xAxis = [
    {
      type: 'category',
      data: dates,
      scale: true,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#2a3441' } },
      axisLabel: { color: '#8892a6', fontSize: 10 },
      splitLine: { show: false },
    },
    {
      type: 'category',
      gridIndex: 1,
      data: dates,
      scale: true,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#2a3441' } },
      axisLabel: { show: false },
      splitLine: { show: false },
    },
  ]

  option.yAxis = [
    {
      scale: true,
      splitNumber: 4,
      axisLine: { show: false },
      axisLabel: { color: '#8892a6', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e2530', type: 'dashed' } },
    },
    {
      min: 0,
      max: 100,
      gridIndex: 1,
      splitNumber: 2,
      axisLine: { show: false },
      axisLabel: { color: '#8892a6', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e2530', type: 'dashed' } },
    },
  ]

  option.series = [
    {
      name: 'K线',
      type: 'candlestick',
      data: data.map((item) => [item.open, item.close, item.low, item.high, item.volume]),
      itemStyle: {
        color: '#00ff88',
        color0: '#ff4757',
        borderColor: '#00ff88',
        borderColor0: '#ff4757',
      },
    },
    // RSI6
    {
      name: 'RSI6',
      type: 'line',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: rsi6,
      smooth: true,
      lineStyle: { width: 1.5, color: '#00d4ff' },
      showSymbol: false,
    },
    // RSI14
    {
      name: 'RSI14',
      type: 'line',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: rsi14,
      smooth: true,
      lineStyle: { width: 1.5, color: '#f59e0b' },
      showSymbol: false,
    },
    // RSI24
    {
      name: 'RSI24',
      type: 'line',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: rsi24,
      smooth: true,
      lineStyle: { width: 1.5, color: '#8b5cf6' },
      showSymbol: false,
    },
    // 超买超卖线
    {
      name: '超买线',
      type: 'line',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: new Array(data.length).fill(70),
      lineStyle: { width: 1, color: '#ff4757', type: 'dashed' },
      showSymbol: false,
      silent: true,
    },
    {
      name: '超卖线',
      type: 'line',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: new Array(data.length).fill(30),
      lineStyle: { width: 1, color: '#00ff88', type: 'dashed' },
      showSymbol: false,
      silent: true,
    },
  ]

  option.tooltip.formatter = function (params: any) {
    const kline = params.find((p: any) => p.seriesName === 'K线')
    const rsi6 = params.find((p: any) => p.seriesName === 'RSI6')
    const rsi14 = params.find((p: any) => p.seriesName === 'RSI14')
    const rsi24 = params.find((p: any) => p.seriesName === 'RSI24')

    let html = `<div style="font-weight: 600; margin-bottom: 8px; color: #00d4ff;">${kline?.axisValue || ''}</div>`

    if (kline) {
      const d = kline.data
      html += `<div style="color: ${d[1] >= d[2] ? '#00ff88' : '#ff4757'}; font-weight: 600;">${d[2].toFixed(2)}</div>`
    }

    html += `<div style="margin-top: 8px; border-top: 1px solid #2a3441; padding-top: 8px;">`
    if (rsi6 && rsi6.value !== null) {
      html += `<div style="color: #00d4ff;">RSI6: ${rsi6.value.toFixed(2)}</div>`
    }
    if (rsi14 && rsi14.value !== null) {
      html += `<div style="color: #f59e0b;">RSI14: ${rsi14.value.toFixed(2)}</div>`
    }
    if (rsi24 && rsi24.value !== null) {
      html += `<div style="color: #8b5cf6;">RSI24: ${rsi24.value.toFixed(2)}</div>`
    }
    html += `</div>`

    return html
  }
}

// 布林带模式
function updateBOLLChart(option: any, data: KLineData[], dates: string[]) {
  const boll = calculateBollingerBands(data)

  option.grid = [
    { left: '3%', right: '4%', top: '5%', height: '60%', containLabel: true },
    { left: '3%', right: '4%', top: '72%', height: '18%', containLabel: true },
  ]

  option.xAxis = [
    {
      type: 'category',
      data: dates,
      scale: true,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#2a3441' } },
      axisLabel: { color: '#8892a6', fontSize: 10 },
      splitLine: { show: false },
    },
    {
      type: 'category',
      gridIndex: 1,
      data: dates,
      scale: true,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#2a3441' } },
      axisLabel: { show: false },
      splitLine: { show: false },
    },
  ]

  option.yAxis = [
    {
      scale: true,
      splitNumber: 4,
      axisLine: { show: false },
      axisLabel: { color: '#8892a6', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e2530', type: 'dashed' } },
    },
    {
      scale: true,
      gridIndex: 1,
      splitNumber: 2,
      axisLine: { show: false },
      axisLabel: { color: '#8892a6', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e2530', type: 'dashed' } },
    },
  ]

  option.series = [
    // 上轨
    {
      name: '上轨',
      type: 'line',
      data: boll.upper,
      smooth: true,
      lineStyle: { width: 1, color: '#ff4757' },
      showSymbol: false,
      areaStyle: {
        color: 'transparent',
      },
    },
    // 中轨
    {
      name: '中轨',
      type: 'line',
      data: boll.middle,
      smooth: true,
      lineStyle: { width: 1.5, color: '#f59e0b' },
      showSymbol: false,
    },
    // 下轨
    {
      name: '下轨',
      type: 'line',
      data: boll.lower,
      smooth: true,
      lineStyle: { width: 1, color: '#00ff88' },
      showSymbol: false,
      // 填充上下轨之间的区域
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0, 212, 255, 0.05)' },
          { offset: 1, color: 'rgba(0, 212, 255, 0.02)' },
        ]),
      },
    },
    // K线
    {
      name: 'K线',
      type: 'candlestick',
      data: data.map((item) => [item.open, item.close, item.low, item.high, item.volume]),
      itemStyle: {
        color: '#00ff88',
        color0: '#ff4757',
        borderColor: '#00ff88',
        borderColor0: '#ff4757',
      },
      z: 10,
    },
    // 成交量
    {
      name: '成交量',
      type: 'bar',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: data.map((item, index) => ({
        value: item.volume,
        itemStyle: {
          color: index > 0 && data[index].close >= data[index - 1].close ? 'rgba(0, 255, 136, 0.6)' : 'rgba(255, 71, 87, 0.6)',
        },
      })),
    },
  ]

  option.tooltip.formatter = function (params: any) {
    const kline = params.find((p: any) => p.seriesName === 'K线')
    const upper = params.find((p: any) => p.seriesName === '上轨')
    const middle = params.find((p: any) => p.seriesName === '中轨')
    const lower = params.find((p: any) => p.seriesName === '下轨')

    let html = `<div style="font-weight: 600; margin-bottom: 8px; color: #00d4ff;">${kline?.axisValue || ''}</div>`

    if (kline) {
      const d = kline.data
      html += `<div style="color: ${d[1] >= d[2] ? '#00ff88' : '#ff4757'}; font-weight: 600;">${d[2].toFixed(2)}</div>`
    }

    html += `<div style="margin-top: 8px; border-top: 1px solid #2a3441; padding-top: 8px;">`
    if (upper && upper.value !== null) {
      html += `<div style="color: #ff4757;">上轨: ${upper.value.toFixed(2)}</div>`
    }
    if (middle && middle.value !== null) {
      html += `<div style="color: #f59e0b;">中轨: ${middle.value.toFixed(2)}</div>`
    }
    if (lower && lower.value !== null) {
      html += `<div style="color: #00ff88;">下轨: ${lower.value.toFixed(2)}</div>`
    }
    html += `</div>`

    return html
  }
}

function handleTimeframeChange(tf: string) {
  emit('timeframeChange', tf)
}

// 监听数据变化
watch(
  () => props.data,
  () => {
    nextTick(() => {
      updateChart()
    })
  },
  { deep: true }
)

// 监听指标变化
watch(activeIndicator, () => {
  nextTick(() => {
    updateChart()
  })
})

onMounted(() => {
  initChart()
  updateChart()
})

onUnmounted(() => {
  chartInstance?.dispose()
  chartInstance = null
})

// 暴露方法
defineExpose({
  resize: () => chartInstance?.resize(),
})
</script>

<style scoped>
.kline-chart {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, rgba(20, 25, 35, 0.8) 0%, rgba(15, 20, 30, 0.9) 100%);
  border: 1px solid #2a3441;
  border-radius: 12px;
  padding: 12px;
  box-sizing: border-box;
}

.indicator-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  flex-shrink: 0;
}

.indicator-tabs,
.timeframe-tabs {
  display: flex;
  gap: 4px;
  background: rgba(42, 52, 65, 0.5);
  padding: 2px;
  border-radius: 6px;
}

.indicator-btn,
.tf-btn {
  padding: 4px 10px;
  font-size: 11px;
  color: #8892a6;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.indicator-btn:hover,
.tf-btn:hover {
  color: #e4e7ed;
}

.indicator-btn.active,
.tf-btn.active {
  background: #00d4ff;
  color: #0f1419;
  font-weight: 600;
}

.chart-container {
  flex: 1;
  width: 100%;
  min-height: 350px;
  position: relative;
}

.chart-loading,
.chart-error {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8892a6;
  font-size: 13px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #2a3441;
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.chart-error {
  color: #ff4757;
}

/* 响应式 */
@media (max-width: 768px) {
  .indicator-bar {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }

  .timeframe-tabs {
    width: 100%;
    overflow-x: auto;
  }

  .chart-container {
    min-height: 300px;
  }
}
</style>

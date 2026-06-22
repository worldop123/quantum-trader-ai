<template>
  <div class="option-chain">
    <!-- 到期日切换 -->
    <div class="expiry-tabs">
      <button
        v-for="expiry in expiryDates"
        :key="expiry"
        :class="['expiry-tab', { active: currentExpiry === expiry }]"
        @click="currentExpiry = expiry"
      >
        {{ formatExpiry(expiry) }}
      </button>
    </div>

    <!-- 显示模式切换 -->
    <div class="view-switcher">
      <button
        :class="['switch-btn', { active: displayMode === 'price' }]"
        @click="displayMode = 'price'"
      >
        价格
      </button>
      <button
        :class="['switch-btn', { active: displayMode === 'greeks' }]"
        @click="displayMode = 'greeks'"
      >
        希腊字母
      </button>
    </div>

    <!-- T型报价表 -->
    <div class="chain-table">
      <!-- 表头 -->
      <div class="table-header">
        <div class="call-side">
          <span class="col-title">看涨期权</span>
        </div>
        <div class="strike-col">
          <span class="col-title">行权价</span>
        </div>
        <div class="put-side">
          <span class="col-title">看跌期权</span>
        </div>
      </div>

      <!-- 列标题 -->
      <div class="table-subheader">
        <div class="call-side">
          <span v-if="displayMode === 'price'">最新价</span>
          <span v-if="displayMode === 'price'">涨跌幅</span>
          <span v-if="displayMode === 'greeks'">Delta</span>
          <span v-if="displayMode === 'greeks'">Gamma</span>
        </div>
        <div class="strike-col"></div>
        <div class="put-side">
          <span v-if="displayMode === 'price'">最新价</span>
          <span v-if="displayMode === 'price'">涨跌幅</span>
          <span v-if="displayMode === 'greeks'">Delta</span>
          <span v-if="displayMode === 'greeks'">Gamma</span>
        </div>
      </div>

      <!-- 数据行 -->
      <div class="table-body">
        <div
          v-for="(row, index) in optionData"
          :key="index"
          :class="['option-row', { 'at-the-money': row.isATM }]"
        >
          <!-- 看涨期权 -->
          <div class="call-side" @click="handleSelectOption(row.call, 'call')">
            <span v-if="displayMode === 'price'" class="price">
              {{ row.call.lastPrice.toFixed(2) }}
            </span>
            <span
              v-if="displayMode === 'price'"
              :class="['change', { positive: row.call.changePercent >= 0, negative: row.call.changePercent < 0 }]"
            >
              {{ row.call.changePercent >= 0 ? '+' : '' }}{{ row.call.changePercent.toFixed(2) }}%
            </span>
            <span v-if="displayMode === 'greeks'" class="greek">
              {{ row.call.delta.toFixed(4) }}
            </span>
            <span v-if="displayMode === 'greeks'" class="greek">
              {{ row.call.gamma.toFixed(4) }}
            </span>
          </div>

          <!-- 行权价 -->
          <div class="strike-col">
            <span class="strike-price">{{ row.strikePrice.toFixed(2) }}</span>
          </div>

          <!-- 看跌期权 -->
          <div class="put-side" @click="handleSelectOption(row.put, 'put')">
            <span v-if="displayMode === 'price'" class="price">
              {{ row.put.lastPrice.toFixed(2) }}
            </span>
            <span
              v-if="displayMode === 'price'"
              :class="['change', { positive: row.put.changePercent >= 0, negative: row.put.changePercent < 0 }]"
            >
              {{ row.put.changePercent >= 0 ? '+' : '' }}{{ row.put.changePercent.toFixed(2) }}%
            </span>
            <span v-if="displayMode === 'greeks'" class="greek">
              {{ row.put.delta.toFixed(4) }}
            </span>
            <span v-if="displayMode === 'greeks'" class="greek">
              {{ row.put.gamma.toFixed(4) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 选中的期权信息 -->
    <div v-if="selectedOption" class="selected-info">
      <div class="info-header">
        <span class="info-title">{{ selectedOption.symbol }}</span>
        <span :class="['option-type', selectedOption.type]">
          {{ selectedOption.type === 'call' ? '看涨' : '看跌' }}
        </span>
      </div>
      <div class="info-grid">
        <div class="info-item">
          <span class="label">最新价</span>
          <span class="value">{{ selectedOption.lastPrice.toFixed(2) }}</span>
        </div>
        <div class="info-item">
          <span class="label">涨跌幅</span>
          <span :class="['value', { positive: selectedOption.changePercent >= 0, negative: selectedOption.changePercent < 0 }]">
            {{ selectedOption.changePercent >= 0 ? '+' : '' }}{{ selectedOption.changePercent.toFixed(2) }}%
          </span>
        </div>
        <div class="info-item">
          <span class="label">Delta</span>
          <span class="value">{{ selectedOption.delta.toFixed(4) }}</span>
        </div>
        <div class="info-item">
          <span class="label">Gamma</span>
          <span class="value">{{ selectedOption.gamma.toFixed(4) }}</span>
        </div>
        <div class="info-item">
          <span class="label">Theta</span>
          <span class="value">{{ selectedOption.theta.toFixed(4) }}</span>
        </div>
        <div class="info-item">
          <span class="label">Vega</span>
          <span class="value">{{ selectedOption.vega.toFixed(4) }}</span>
        </div>
      </div>
      <div class="info-actions">
        <button class="action-btn buy">买入</button>
        <button class="action-btn sell">卖出</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface OptionContract {
  symbol: string
  type: 'call' | 'put'
  strikePrice: number
  lastPrice: number
  changePercent: number
  volume: number
  openInterest: number
  delta: number
  gamma: number
  theta: number
  vega: number
}

interface OptionRow {
  strikePrice: number
  isATM: boolean
  call: OptionContract
  put: OptionContract
}

const emit = defineEmits<{
  (e: 'select', option: OptionContract, type: string): void
}>()

// 模拟数据 - 到期日
const expiryDates = [
  '2024-06-28',
  '2024-07-05',
  '2024-07-12',
  '2024-07-26',
  '2024-09-27',
  '2024-12-27',
]

const currentExpiry = ref('2024-06-28')
const displayMode = ref<'price' | 'greeks'>('price')
const selectedOption = ref<OptionContract | null>(null)

// 模拟标的价格
const underlyingPrice = 43000

// 生成模拟期权数据
const optionData = computed<OptionRow[]>(() => {
  const strikes = []
  const atmStrike = Math.round(underlyingPrice / 500) * 500

  for (let i = -10; i <= 10; i++) {
    const strike = atmStrike + i * 500
    if (strike <= 0) continue

    const isATM = strike === atmStrike
    const moneyness = (underlyingPrice - strike) / strike

    // 看涨期权
    const callPrice = Math.max(0, underlyingPrice - strike) + Math.random() * 200 + 50
    const callDelta = Math.min(1, Math.max(0, 0.5 + moneyness * 5))
    const callGamma = Math.exp(-Math.abs(moneyness) * 3) * 0.001

    // 看跌期权
    const putPrice = Math.max(0, strike - underlyingPrice) + Math.random() * 200 + 50
    const putDelta = Math.min(0, Math.max(-1, -0.5 + moneyness * 5))
    const putGamma = callGamma // 看涨看跌Gamma相同

    strikes.push({
      strikePrice: strike,
      isATM,
      call: {
        symbol: `BTC-${strike}-C`,
        type: 'call' as const,
        strikePrice: strike,
        lastPrice: callPrice,
        changePercent: (Math.random() - 0.5) * 20,
        volume: Math.floor(Math.random() * 1000),
        openInterest: Math.floor(Math.random() * 5000),
        delta: callDelta,
        gamma: callGamma,
        theta: -Math.random() * 10 - 5,
        vega: Math.random() * 50 + 20,
      },
      put: {
        symbol: `BTC-${strike}-P`,
        type: 'put' as const,
        strikePrice: strike,
        lastPrice: putPrice,
        changePercent: (Math.random() - 0.5) * 20,
        volume: Math.floor(Math.random() * 1000),
        openInterest: Math.floor(Math.random() * 5000),
        delta: putDelta,
        gamma: putGamma,
        theta: -Math.random() * 10 - 5,
        vega: Math.random() * 50 + 20,
      },
    })
  }

  return strikes
})

function formatExpiry(date: string): string {
  const d = new Date(date)
  const month = d.getMonth() + 1
  const day = d.getDate()
  return `${month}月${day}日`
}

function handleSelectOption(option: OptionContract, type: string) {
  selectedOption.value = option
  emit('select', option, type)
}

onMounted(() => {
  // 默认选中平值看涨
  const atmRow = optionData.value.find((row) => row.isATM)
  if (atmRow) {
    selectedOption.value = atmRow.call
  }
})
</script>

<style scoped>
.option-chain {
  width: 100%;
  background: linear-gradient(135deg, rgba(20, 25, 35, 0.8) 0%, rgba(15, 20, 30, 0.9) 100%);
  border: 1px solid #2a3441;
  border-radius: 12px;
  padding: 16px;
  box-sizing: border-box;
}

.expiry-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.expiry-tab {
  padding: 6px 12px;
  font-size: 12px;
  color: #8892a6;
  background: rgba(42, 52, 65, 0.5);
  border: 1px solid #2a3441;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.expiry-tab:hover {
  color: #e4e7ed;
  border-color: #3a4451;
}

.expiry-tab.active {
  background: #00d4ff;
  color: #0f1419;
  border-color: #00d4ff;
  font-weight: 600;
}

.view-switcher {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
  background: rgba(42, 52, 65, 0.5);
  padding: 2px;
  border-radius: 6px;
  width: fit-content;
}

.switch-btn {
  padding: 4px 12px;
  font-size: 11px;
  color: #8892a6;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.switch-btn:hover {
  color: #e4e7ed;
}

.switch-btn.active {
  background: #00d4ff;
  color: #0f1419;
  font-weight: 600;
}

.chain-table {
  border: 1px solid #2a3441;
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  display: flex;
  background: rgba(42, 52, 65, 0.5);
  border-bottom: 1px solid #2a3441;
}

.table-subheader {
  display: flex;
  background: rgba(30, 37, 48, 0.5);
  border-bottom: 1px solid #2a3441;
  font-size: 10px;
  color: #8892a6;
}

.call-side,
.put-side {
  flex: 1;
  display: flex;
  justify-content: space-around;
  padding: 8px 4px;
  font-size: 11px;
}

.call-side {
  border-right: 1px solid #2a3441;
}

.put-side {
  border-left: 1px solid #2a3441;
}

.strike-col {
  width: 80px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 4px;
  background: rgba(20, 25, 35, 0.8);
}

.col-title {
  font-weight: 600;
  color: #e4e7ed;
  font-size: 12px;
}

.table-body {
  max-height: 400px;
  overflow-y: auto;
}

.option-row {
  display: flex;
  border-bottom: 1px solid #1e2530;
  cursor: pointer;
  transition: background 0.2s ease;
}

.option-row:hover {
  background: rgba(0, 212, 255, 0.05);
}

.option-row.at-the-money {
  background: rgba(255, 193, 7, 0.05);
}

.option-row.at-the-money .strike-col {
  background: rgba(255, 193, 7, 0.1);
}

.option-row .call-side:hover {
  background: rgba(0, 255, 136, 0.05);
}

.option-row .put-side:hover {
  background: rgba(255, 71, 87, 0.05);
}

.price {
  font-weight: 600;
  color: #e4e7ed;
  font-variant-numeric: tabular-nums;
}

.change {
  font-size: 10px;
  font-variant-numeric: tabular-nums;
}

.change.positive {
  color: #00ff88;
}

.change.negative {
  color: #ff4757;
}

.greek {
  font-size: 11px;
  color: #8892a6;
  font-variant-numeric: tabular-nums;
}

.strike-price {
  font-weight: 700;
  color: #ffc107;
  font-size: 13px;
  font-variant-numeric: tabular-nums;
}

.at-the-money .strike-price {
  color: #ffc107;
  text-shadow: 0 0 10px rgba(255, 193, 7, 0.5);
}

.selected-info {
  margin-top: 16px;
  padding: 12px;
  background: rgba(42, 52, 65, 0.3);
  border-radius: 8px;
  border: 1px solid #2a3441;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.info-title {
  font-size: 14px;
  font-weight: 600;
  color: #e4e7ed;
}

.option-type {
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 4px;
}

.option-type.call {
  background: rgba(0, 255, 136, 0.1);
  color: #00ff88;
}

.option-type.put {
  background: rgba(255, 71, 87, 0.1);
  color: #ff4757;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  font-size: 10px;
  color: #8892a6;
}

.info-item .value {
  font-size: 13px;
  font-weight: 600;
  color: #e4e7ed;
  font-variant-numeric: tabular-nums;
}

.info-item .value.positive {
  color: #00ff88;
}

.info-item .value.negative {
  color: #ff4757;
}

.info-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn.buy {
  background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
  color: #0f1419;
}

.action-btn.buy:hover {
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3);
  transform: translateY(-1px);
}

.action-btn.sell {
  background: linear-gradient(135deg, #ff4757 0%, #ff2d3f 100%);
  color: #fff;
}

.action-btn.sell:hover {
  box-shadow: 0 4px 12px rgba(255, 71, 87, 0.3);
  transform: translateY(-1px);
}

/* 滚动条样式 */
.table-body::-webkit-scrollbar {
  width: 6px;
}

.table-body::-webkit-scrollbar-track {
  background: #1e2530;
}

.table-body::-webkit-scrollbar-thumb {
  background: #3a4451;
  border-radius: 3px;
}

.table-body::-webkit-scrollbar-thumb:hover {
  background: #4a5461;
}
</style>

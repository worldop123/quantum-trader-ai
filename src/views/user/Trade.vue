<template>
  <div class="h-full flex flex-col gap-4">
    <!-- Trading Pair Header -->
    <div class="quantum-card flex items-center justify-between">
      <div class="flex items-center gap-4">
        <select v-model="selectedSymbol" class="quantum-input w-48">
          <option value="BTC/USDT">BTC/USDT</option>
          <option value="ETH/USDT">ETH/USDT</option>
          <option value="SOL/USDT">SOL/USDT</option>
          <option value="BNB/USDT">BNB/USDT</option>
          <option value="XRP/USDT">XRP/USDT</option>
        </select>
        <div>
          <p class="text-2xl font-bold font-mono text-quantum-green">${{ currentPrice.toLocaleString() }}</p>
          <p class="text-sm text-quantum-green">+2.35% ↑</p>
        </div>
      </div>
      <div class="flex gap-4 text-sm">
        <div class="text-center">
          <p class="text-gray-500">24h 最高</p>
          <p class="font-mono text-gray-300">$68,500</p>
        </div>
        <div class="text-center">
          <p class="text-gray-500">24h 最低</p>
          <p class="font-mono text-gray-300">$65,200</p>
        </div>
        <div class="text-center">
          <p class="text-gray-500">24h 成交量</p>
          <p class="font-mono text-gray-300">$2.4B</p>
        </div>
      </div>
    </div>

    <!-- Main Trading Area -->
    <div class="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-4">
      <!-- Chart -->
      <div class="lg:col-span-3 quantum-card flex flex-col">
        <div class="flex items-center justify-between mb-4">
          <div class="flex gap-2">
            <button v-for="tf in timeframes" :key="tf.value"
              @click="selectedTimeframe = tf.value"
              class="px-3 py-1 text-xs rounded transition-colors"
              :class="selectedTimeframe === tf.value ? 'bg-quantum-cyan text-quantum-darker' : 'bg-quantum-border text-gray-400 hover:bg-gray-700'">
              {{ tf.label }}
            </button>
          </div>
          <div class="flex gap-2">
            <button class="p-2 rounded bg-quantum-border hover:bg-gray-700 transition-colors">
              <CandlestickChart class="w-4 h-4 text-gray-400" />
            </button>
            <button class="p-2 rounded bg-quantum-border hover:bg-gray-700 transition-colors">
              <LineChart class="w-4 h-4 text-gray-400" />
            </button>
            <button class="p-2 rounded bg-quantum-border hover:bg-gray-700 transition-colors">
              <Activity class="w-4 h-4 text-gray-400" />
            </button>
          </div>
        </div>
        <div class="flex-1 flex items-center justify-center bg-quantum-darker rounded-lg">
          <div class="text-center">
            <CandlestickChart class="w-16 h-16 text-gray-600 mx-auto mb-3" />
            <p class="text-gray-500">K线图表开发中</p>
            <p class="text-gray-600 text-sm">TradingView / ECharts K线图</p>
          </div>
        </div>
      </div>

      <!-- Order Panel -->
      <div class="quantum-card flex flex-col">
        <!-- Order Type Tabs -->
        <div class="flex border-b border-quantum-border mb-4">
          <button @click="orderType = 'spot'"
            class="flex-1 py-2 text-sm font-medium transition-colors"
            :class="orderType === 'spot' ? 'text-quantum-cyan border-b-2 border-quantum-cyan' : 'text-gray-500 hover:text-gray-300'">
            现货
          </button>
          <button @click="orderType = 'futures'"
            class="flex-1 py-2 text-sm font-medium transition-colors"
            :class="orderType === 'futures' ? 'text-quantum-cyan border-b-2 border-quantum-cyan' : 'text-gray-500 hover:text-gray-300'">
            合约
          </button>
          <button @click="orderType = 'option'"
            class="flex-1 py-2 text-sm font-medium transition-colors"
            :class="orderType === 'option' ? 'text-quantum-cyan border-b-2 border-quantum-cyan' : 'text-gray-500 hover:text-gray-300'">
            期权
          </button>
        </div>

        <!-- Buy/Sell Tabs -->
        <div class="flex gap-2 mb-4">
          <button @click="side = 'buy'"
            class="flex-1 py-2 rounded font-medium transition-colors"
            :class="side === 'buy' ? 'bg-quantum-green text-white' : 'bg-quantum-border text-gray-400 hover:bg-gray-700'">
            买入
          </button>
          <button @click="side = 'sell'"
            class="flex-1 py-2 rounded font-medium transition-colors"
            :class="side === 'sell' ? 'bg-quantum-red text-white' : 'bg-quantum-border text-gray-400 hover:bg-gray-700'">
            卖出
          </button>
        </div>

        <!-- Order Form -->
        <div class="space-y-4 flex-1">
          <!-- Market/Limit -->
          <div class="flex gap-2">
            <button @click="orderMode = 'market'"
              class="flex-1 py-1 text-xs rounded transition-colors"
              :class="orderMode === 'market' ? 'bg-quantum-cyan/20 text-quantum-cyan' : 'text-gray-500 hover:text-gray-300'">
              市价
            </button>
            <button @click="orderMode = 'limit'"
              class="flex-1 py-1 text-xs rounded transition-colors"
              :class="orderMode === 'limit' ? 'bg-quantum-cyan/20 text-quantum-cyan' : 'text-gray-500 hover:text-gray-300'">
              限价
            </button>
          </div>

          <!-- Price Input (limit only) -->
          <div v-if="orderMode === 'limit'">
            <label class="quantum-label">价格 (USDT)</label>
            <input v-model.number="price" type="number" step="0.01" class="quantum-input" placeholder="输入价格" />
          </div>

          <!-- Quantity Input -->
          <div>
            <label class="quantum-label">数量 ({{ selectedSymbol.split('/')[0] }})</label>
            <input v-model.number="quantity" type="number" step="0.0001" class="quantum-input" placeholder="输入数量" />
          </div>

          <!-- Quick Amount Buttons -->
          <div class="flex gap-2">
            <button v-for="pct in [25, 50, 75, 100]" :key="pct"
              @click="setQuantityPercent(pct)"
              class="flex-1 py-1 text-xs rounded bg-quantum-border text-gray-400 hover:bg-gray-700 hover:text-gray-300 transition-colors">
              {{ pct }}%
            </button>
          </div>

          <!-- Total -->
          <div>
            <label class="quantum-label">总额 (USDT)</label>
            <div class="quantum-input bg-quantum-darker text-gray-400">
              ${{ total.toLocaleString() }}
            </div>
          </div>

          <!-- Leverage (futures only) -->
          <div v-if="orderType === 'futures'">
            <label class="quantum-label">杠杆倍数</label>
            <div class="flex gap-2">
              <button v-for="lev in leverageOptions" :key="lev"
                @click="leverage = lev"
                class="flex-1 py-1 text-xs rounded transition-colors"
                :class="leverage === lev ? 'bg-quantum-yellow/20 text-quantum-yellow' : 'bg-quantum-border text-gray-400 hover:bg-gray-700'">
                {{ lev }}x
              </button>
            </div>
          </div>

          <!-- Submit Button -->
          <button @click="submitOrder" 
            class="w-full py-3 rounded font-bold transition-all"
            :class="side === 'buy' ? 'bg-quantum-green hover:bg-green-400 text-white' : 'bg-quantum-red hover:bg-red-400 text-white'">
            {{ side === 'buy' ? '买入' : '卖出' }} {{ selectedSymbol.split('/')[0] }}
          </button>
        </div>

        <!-- Available Balance -->
        <div class="mt-4 pt-4 border-t border-quantum-border text-xs text-gray-500 flex justify-between">
          <span>可用余额</span>
          <span class="font-mono text-gray-400">${{ tradingStore.availableBalance.toLocaleString() }}</span>
        </div>
      </div>
    </div>

    <!-- Order Book & Recent Trades -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div class="quantum-card">
        <h3 class="text-sm font-semibold text-gray-200 mb-3">订单簿</h3>
        <div class="space-y-1 text-xs font-mono">
          <div class="grid grid-cols-3 text-gray-500 pb-2 border-b border-quantum-border">
            <span>价格</span>
            <span class="text-center">数量</span>
            <span class="text-right">总额</span>
          </div>
          <!-- Asks -->
          <div v-for="i in 5" :key="'ask-' + i" class="grid grid-cols-3 py-1 relative">
            <div class="absolute inset-0 bg-quantum-red/10" :style="{ width: (20 + i * 15) + '%', right: 0 }"></div>
            <span class="text-quantum-red relative z-10">{{ (68000 + i * 100).toLocaleString() }}</span>
            <span class="text-center text-gray-400 relative z-10">{{ (Math.random() * 2).toFixed(4) }}</span>
            <span class="text-right text-gray-500 relative z-10">{{ (Math.random() * 100000).toFixed(2) }}</span>
          </div>
          <!-- Current Price -->
          <div class="py-2 text-center text-lg font-bold text-quantum-green border-y border-quantum-border my-1">
            ${{ currentPrice.toLocaleString() }}
          </div>
          <!-- Bids -->
          <div v-for="i in 5" :key="'bid-' + i" class="grid grid-cols-3 py-1 relative">
            <div class="absolute inset-0 bg-quantum-green/10" :style="{ width: (90 - i * 15) + '%', right: 0 }"></div>
            <span class="text-quantum-green relative z-10">{{ (67500 - i * 100).toLocaleString() }}</span>
            <span class="text-center text-gray-400 relative z-10">{{ (Math.random() * 2).toFixed(4) }}</span>
            <span class="text-right text-gray-500 relative z-10">{{ (Math.random() * 100000).toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <div class="quantum-card">
        <h3 class="text-sm font-semibold text-gray-200 mb-3">最新成交</h3>
        <div class="space-y-1 text-xs font-mono">
          <div class="grid grid-cols-3 text-gray-500 pb-2 border-b border-quantum-border">
            <span>价格</span>
            <span class="text-center">数量</span>
            <span class="text-right">时间</span>
          </div>
          <div v-for="i in 10" :key="i" class="grid grid-cols-3 py-1">
            <span :class="i % 2 === 0 ? 'text-quantum-green' : 'text-quantum-red'">
              {{ (67500 + (Math.random() - 0.5) * 200).toFixed(2) }}
            </span>
            <span class="text-center text-gray-400">{{ (Math.random() * 0.5).toFixed(4) }}</span>
            <span class="text-right text-gray-500">{{ new Date(Date.now() - i * 30000).toLocaleTimeString() }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTradingStore } from '../../stores/trading'
import {
  CandlestickChart,
  LineChart,
  Activity
} from 'lucide-vue-next'

const tradingStore = useTradingStore()

const selectedSymbol = ref('BTC/USDT')
const currentPrice = ref(67500)
const selectedTimeframe = ref('1h')
const orderType = ref<'spot' | 'futures' | 'option'>('spot')
const side = ref<'buy' | 'sell'>('buy')
const orderMode = ref<'market' | 'limit'>('limit')
const price = ref(67500)
const quantity = ref(0)
const leverage = ref(5)

const timeframes = [
  { label: '1m', value: '1m' },
  { label: '5m', value: '5m' },
  { label: '15m', value: '15m' },
  { label: '1h', value: '1h' },
  { label: '4h', value: '4h' },
  { label: '1d', value: '1d' }
]

const leverageOptions = [2, 5, 10, 20, 50, 100]

const total = computed(() => {
  const p = orderMode.value === 'market' ? currentPrice.value : price.value
  return (quantity.value || 0) * p
})

function setQuantityPercent(pct: number) {
  const available = tradingStore.availableBalance * (pct / 100)
  const p = orderMode.value === 'market' ? currentPrice.value : price.value
  quantity.value = parseFloat((available / p).toFixed(6))
}

function submitOrder() {
  if (!quantity.value || quantity.value <= 0) {
    alert('请输入有效的数量')
    return
  }
  
  const p = orderMode.value === 'market' ? currentPrice.value : price.value
  tradingStore.placeOrder(
    selectedSymbol.value,
    side.value,
    orderMode.value,
    quantity.value,
    p
  )
  
  alert(`${side.value === 'buy' ? '买入' : '卖出'}订单已提交`)
  quantity.value = 0
}
</script>

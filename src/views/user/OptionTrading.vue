<template>
  <div class="option-trading p-4">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-white">期权交易</h1>
      <div class="flex items-center gap-4">
        <WsStatus />
      </div>
    </div>

    <!-- Tab切换 -->
    <div class="flex gap-2 mb-6 border-b border-gray-700">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        :class="[
          'px-4 py-2 text-sm font-medium transition-all',
          activeTab === tab.key
            ? 'text-cyan-400 border-b-2 border-cyan-400'
            : 'text-gray-400 hover:text-gray-200'
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 期权链T型报价 -->
    <div v-if="activeTab === 'chain'" class="space-y-4">
      <!-- 交易对和到期日选择 -->
      <div class="flex flex-wrap items-center gap-4 bg-gray-800/50 rounded-lg p-4">
        <div class="flex items-center gap-2">
          <span class="text-gray-400 text-sm">交易对：</span>
          <select
            v-model="selectedSymbol"
            class="bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-cyan-500 focus:outline-none"
          >
            <option value="BTC-USDT">BTC-USDT</option>
            <option value="ETH-USDT">ETH-USDT</option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-gray-400 text-sm">显示模式：</span>
          <button
            @click="displayMode = 'price'"
            :class="[
              'px-3 py-1 text-sm rounded transition-all',
              displayMode === 'price'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                : 'bg-gray-700 text-gray-400 hover:text-gray-200'
            ]"
          >
            价格
          </button>
          <button
            @click="displayMode = 'greeks'"
            :class="[
              'px-3 py-1 text-sm rounded transition-all',
              displayMode === 'greeks'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                : 'bg-gray-700 text-gray-400 hover:text-gray-200'
            ]"
          >
            希腊字母
          </button>
        </div>
      </div>

      <!-- 到期日Tab -->
      <div class="flex gap-2 overflow-x-auto pb-2">
        <button
          v-for="expiry in expiries"
          :key="expiry"
          @click="selectedExpiry = expiry"
          :class="[
            'px-4 py-2 text-sm rounded-lg whitespace-nowrap transition-all',
            selectedExpiry === expiry
              ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
              : 'bg-gray-800 text-gray-400 hover:text-gray-200 border border-gray-700'
          ]"
        >
          {{ expiry }}
        </button>
      </div>

      <!-- T型报价表格 -->
      <div class="bg-gray-800/50 rounded-lg overflow-hidden border border-gray-700">
        <!-- 表头 -->
        <div class="grid grid-cols-3 bg-gray-900/50 text-sm font-medium">
          <div class="p-3 text-center text-green-400">看涨期权 (Call)</div>
          <div class="p-3 text-center text-yellow-400 border-x border-gray-700">行权价</div>
          <div class="p-3 text-center text-red-400">看跌期权 (Put)</div>
        </div>

        <!-- 期权链数据 -->
        <div class="max-h-[500px] overflow-y-auto">
          <div
            v-for="(row, index) in optionChain"
            :key="index"
            class="grid grid-cols-3 border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors cursor-pointer"
          >
            <!-- 看涨期权 -->
            <div
              @click="selectOption(row.call, 'call')"
              :class="[
                'p-3 text-center transition-all',
                selectedOption?.type === 'call' && selectedOption?.strike === row.strike
                  ? 'bg-green-500/20'
                  : 'hover:bg-green-500/10'
              ]"
            >
              <template v-if="displayMode === 'price'">
                <div class="text-white font-medium">{{ row.call.lastPrice }}</div>
                <div :class="['text-xs mt-1', row.call.change >= 0 ? 'text-green-400' : 'text-red-400']">
                  {{ row.call.change >= 0 ? '+' : '' }}{{ row.call.changePercent }}%
                </div>
              </template>
              <template v-else>
                <div class="text-white text-sm">Δ: {{ row.call.delta }}</div>
                <div class="text-gray-400 text-xs mt-1">Γ: {{ row.call.gamma }} | Θ: {{ row.call.theta }}</div>
              </template>
            </div>

            <!-- 行权价 -->
            <div
              :class="[
                'p-3 text-center font-bold border-x border-gray-700',
                row.isATM ? 'text-yellow-400 bg-yellow-500/10' : 'text-white'
              ]"
            >
              {{ row.strike }}
              <span v-if="row.isATM" class="text-xs ml-1 text-yellow-500">平值</span>
            </div>

            <!-- 看跌期权 -->
            <div
              @click="selectOption(row.put, 'put')"
              :class="[
                'p-3 text-center transition-all',
                selectedOption?.type === 'put' && selectedOption?.strike === row.strike
                  ? 'bg-red-500/20'
                  : 'hover:bg-red-500/10'
              ]"
            >
              <template v-if="displayMode === 'price'">
                <div class="text-white font-medium">{{ row.put.lastPrice }}</div>
                <div :class="['text-xs mt-1', row.put.change >= 0 ? 'text-green-400' : 'text-red-400']">
                  {{ row.put.change >= 0 ? '+' : '' }}{{ row.put.changePercent }}%
                </div>
              </template>
              <template v-else>
                <div class="text-white text-sm">Δ: {{ row.put.delta }}</div>
                <div class="text-gray-400 text-xs mt-1">Γ: {{ row.put.gamma }} | Θ: {{ row.put.theta }}</div>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- 选中期权详情 -->
      <div v-if="selectedOption" class="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
        <h3 class="text-lg font-bold text-white mb-4">
          {{ selectedOption.type === 'call' ? '看涨' : '看跌' }}期权 - 行权价 {{ selectedOption.strike }}
        </h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div class="bg-gray-900/50 rounded p-3">
            <div class="text-gray-400 text-xs">最新价</div>
            <div class="text-white font-bold text-lg">{{ selectedOption.lastPrice }}</div>
          </div>
          <div class="bg-gray-900/50 rounded p-3">
            <div class="text-gray-400 text-xs">涨跌幅</div>
            <div :class="['font-bold text-lg', selectedOption.change >= 0 ? 'text-green-400' : 'text-red-400']">
              {{ selectedOption.change >= 0 ? '+' : '' }}{{ selectedOption.changePercent }}%
            </div>
          </div>
          <div class="bg-gray-900/50 rounded p-3">
            <div class="text-gray-400 text-xs">成交量</div>
            <div class="text-white font-bold text-lg">{{ selectedOption.volume }}</div>
          </div>
          <div class="bg-gray-900/50 rounded p-3">
            <div class="text-gray-400 text-xs">持仓量</div>
            <div class="text-white font-bold text-lg">{{ selectedOption.openInterest }}</div>
          </div>
        </div>

        <!-- 希腊字母 -->
        <div class="grid grid-cols-4 gap-4 mb-4">
          <div class="text-center">
            <div class="text-gray-400 text-xs">Delta</div>
            <div class="text-cyan-400 font-medium">{{ selectedOption.delta }}</div>
          </div>
          <div class="text-center">
            <div class="text-gray-400 text-xs">Gamma</div>
            <div class="text-purple-400 font-medium">{{ selectedOption.gamma }}</div>
          </div>
          <div class="text-center">
            <div class="text-gray-400 text-xs">Theta</div>
            <div class="text-orange-400 font-medium">{{ selectedOption.theta }}</div>
          </div>
          <div class="text-center">
            <div class="text-gray-400 text-xs">Vega</div>
            <div class="text-green-400 font-medium">{{ selectedOption.vega }}</div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex gap-4">
          <button
            @click="openOrderPanel('buy')"
            class="flex-1 bg-green-500/20 text-green-400 border border-green-500/50 py-3 rounded-lg font-medium hover:bg-green-500/30 transition-all"
          >
            买入开仓
          </button>
          <button
            @click="openOrderPanel('sell')"
            class="flex-1 bg-red-500/20 text-red-400 border border-red-500/50 py-3 rounded-lg font-medium hover:bg-red-500/30 transition-all"
          >
            卖出开仓
          </button>
        </div>
      </div>
    </div>

    <!-- 期权持仓 -->
    <div v-if="activeTab === 'positions'" class="space-y-4">
      <div class="bg-gray-800/50 rounded-lg border border-gray-700 overflow-hidden">
        <div class="p-4 border-b border-gray-700">
          <h2 class="text-lg font-bold text-white">期权持仓</h2>
        </div>

        <!-- 持仓列表 -->
        <div v-if="positions.length > 0" class="divide-y divide-gray-700">
          <div
            v-for="pos in positions"
            :key="pos.id"
            class="p-4 hover:bg-gray-700/30 transition-colors"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-3">
                <span
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium',
                    pos.type === 'call'
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-red-500/20 text-red-400'
                  ]"
                >
                  {{ pos.type === 'call' ? '看涨' : '看跌' }}
                </span>
                <span class="text-white font-medium">{{ pos.symbol }}</span>
                <span class="text-gray-400">行权价 {{ pos.strike }}</span>
                <span class="text-gray-400 text-sm">{{ pos.expiry }}</span>
              </div>
              <button
                @click="closePosition(pos)"
                class="px-3 py-1 bg-red-500/20 text-red-400 border border-red-500/50 rounded text-sm hover:bg-red-500/30 transition-all"
              >
                平仓
              </button>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span class="text-gray-400">持仓数量：</span>
                <span class="text-white">{{ pos.quantity }}</span>
              </div>
              <div>
                <span class="text-gray-400">成本价：</span>
                <span class="text-white">{{ pos.costPrice }}</span>
              </div>
              <div>
                <span class="text-gray-400">最新价：</span>
                <span class="text-white">{{ pos.lastPrice }}</span>
              </div>
              <div>
                <span class="text-gray-400">盈亏：</span>
                <span :class="pos.pnl >= 0 ? 'text-green-400' : 'text-red-400'">
                  {{ pos.pnl >= 0 ? '+' : '' }}{{ pos.pnl }} USDT
                  ({{ pos.pnlPercent >= 0 ? '+' : '' }}{{ pos.pnlPercent }}%)
                </span>
              </div>
            </div>

            <!-- 希腊字母 -->
            <div class="grid grid-cols-4 gap-4 mt-3 text-xs">
              <div class="text-gray-400">
                Delta: <span class="text-cyan-400">{{ pos.delta }}</span>
              </div>
              <div class="text-gray-400">
                Gamma: <span class="text-purple-400">{{ pos.gamma }}</span>
              </div>
              <div class="text-gray-400">
                Theta: <span class="text-orange-400">{{ pos.theta }}</span>
              </div>
              <div class="text-gray-400">
                Vega: <span class="text-green-400">{{ pos.vega }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="p-12 text-center text-gray-500">
          <div class="text-4xl mb-4">📊</div>
          <div>暂无期权持仓</div>
        </div>
      </div>
    </div>

    <!-- 期权订单 -->
    <div v-if="activeTab === 'orders'" class="space-y-4">
      <div class="bg-gray-800/50 rounded-lg border border-gray-700 overflow-hidden">
        <div class="p-4 border-b border-gray-700 flex items-center justify-between">
          <h2 class="text-lg font-bold text-white">期权订单</h2>
          <div class="flex gap-2">
            <button
              v-for="status in orderStatuses"
              :key="status.key"
              @click="orderStatusFilter = status.key"
              :class="[
                'px-3 py-1 text-sm rounded transition-all',
                orderStatusFilter === status.key
                  ? 'bg-cyan-500/20 text-cyan-400'
                  : 'bg-gray-700 text-gray-400 hover:text-gray-200'
              ]"
            >
              {{ status.label }}
            </button>
          </div>
        </div>

        <!-- 订单列表 -->
        <div v-if="filteredOrders.length > 0" class="divide-y divide-gray-700">
          <div
            v-for="order in filteredOrders"
            :key="order.id"
            class="p-4 hover:bg-gray-700/30 transition-colors"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-3">
                <span
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium',
                    order.side === 'buy'
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-red-500/20 text-red-400'
                  ]"
                >
                  {{ order.side === 'buy' ? '买入' : '卖出' }}
                </span>
                <span class="text-white font-medium">{{ order.symbol }}</span>
                <span class="text-gray-400 text-sm">{{ order.type === 'call' ? '看涨' : '看跌' }}</span>
              </div>
              <span
                :class="[
                  'px-2 py-1 rounded text-xs',
                  order.status === 'filled' ? 'bg-green-500/20 text-green-400' :
                  order.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                  'bg-gray-500/20 text-gray-400'
                ]"
              >
                {{ orderStatusMap[order.status] }}
              </span>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-gray-400">
              <div>价格：<span class="text-white">{{ order.price }}</span></div>
              <div>数量：<span class="text-white">{{ order.quantity }}</span></div>
              <div>行权价：<span class="text-white">{{ order.strike }}</span></div>
              <div>时间：<span class="text-white">{{ order.time }}</span></div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="p-12 text-center text-gray-500">
          <div class="text-4xl mb-4">📋</div>
          <div>暂无订单记录</div>
        </div>
      </div>
    </div>

    <!-- 下单弹窗 -->
    <div
      v-if="showOrderPanel"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      @click.self="showOrderPanel = false"
    >
      <div class="bg-gray-800 rounded-xl border border-gray-700 w-full max-w-md p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-white">
            {{ orderSide === 'buy' ? '买入' : '卖出' }}期权
          </h3>
          <button
            @click="showOrderPanel = false"
            class="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        <!-- 期权信息 -->
        <div class="bg-gray-900/50 rounded-lg p-4 mb-6">
          <div class="flex items-center gap-3 mb-2">
            <span
              :class="[
                'px-2 py-1 rounded text-xs font-medium',
                selectedOption?.type === 'call'
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-red-500/20 text-red-400'
              ]"
            >
              {{ selectedOption?.type === 'call' ? '看涨' : '看跌' }}
            </span>
            <span class="text-white font-medium">{{ selectedSymbol }}</span>
          </div>
          <div class="text-gray-400 text-sm">
            行权价：{{ selectedOption?.strike }} | 到期日：{{ selectedExpiry }}
          </div>
        </div>

        <!-- 订单类型 -->
        <div class="mb-4">
          <label class="block text-gray-400 text-sm mb-2">订单类型</label>
          <div class="flex gap-2">
            <button
              @click="orderType = 'limit'"
              :class="[
                'flex-1 py-2 rounded-lg text-sm font-medium transition-all',
                orderType === 'limit'
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                  : 'bg-gray-700 text-gray-400 border border-gray-600'
              ]"
            >
              限价单
            </button>
            <button
              @click="orderType = 'market'"
              :class="[
                'flex-1 py-2 rounded-lg text-sm font-medium transition-all',
                orderType === 'market'
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                  : 'bg-gray-700 text-gray-400 border border-gray-600'
              ]"
            >
              市价单
            </button>
          </div>
        </div>

        <!-- 价格输入 -->
        <div v-if="orderType === 'limit'" class="mb-4">
          <label class="block text-gray-400 text-sm mb-2">价格 (USDT)</label>
          <input
            v-model.number="orderPrice"
            type="number"
            step="0.01"
            class="w-full bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:border-cyan-500 focus:outline-none"
            placeholder="输入价格"
          />
        </div>

        <!-- 数量输入 -->
        <div class="mb-4">
          <label class="block text-gray-400 text-sm mb-2">数量 (张)</label>
          <input
            v-model.number="orderQuantity"
            type="number"
            step="1"
            min="1"
            class="w-full bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:border-cyan-500 focus:outline-none"
            placeholder="输入数量"
          />
        </div>

        <!-- 预估权利金 -->
        <div class="bg-gray-900/50 rounded-lg p-4 mb-6">
          <div class="flex justify-between text-sm">
            <span class="text-gray-400">预估权利金</span>
            <span class="text-white font-medium">
              {{ estimatedPremium.toFixed(2) }} USDT
            </span>
          </div>
        </div>

        <!-- 风险提示 -->
        <div class="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 mb-6">
          <div class="text-yellow-400 text-sm">
            ⚠️ 期权交易风险较高，可能损失全部权利金。请谨慎操作。
          </div>
        </div>

        <!-- 下单按钮 -->
        <button
          @click="submitOrder"
          :disabled="isSubmitting"
          :class="[
            'w-full py-3 rounded-lg font-bold text-white transition-all',
            orderSide === 'buy'
              ? 'bg-green-500 hover:bg-green-600'
              : 'bg-red-500 hover:bg-red-600',
            isSubmitting ? 'opacity-50 cursor-not-allowed' : ''
          ]"
        >
          {{ isSubmitting ? '提交中...' : `确认${orderSide === 'buy' ? '买入' : '卖出'}` }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import WsStatus from '@/components/common/WsStatus.vue'

// Tab配置
const tabs = [
  { key: 'chain', label: '期权链' },
  { key: 'positions', label: '我的持仓' },
  { key: 'orders', label: '订单历史' },
]

const activeTab = ref('chain')

// 交易对和到期日
const selectedSymbol = ref('BTC-USDT')
const selectedExpiry = ref('2024-06-28')
const displayMode = ref<'price' | 'greeks'>('price')

const expiries = [
  '2024-06-28',
  '2024-07-05',
  '2024-07-12',
  '2024-07-19',
  '2024-07-26',
  '2024-08-30',
]

// 选中期权
const selectedOption = ref<any>(null)

// 期权链模拟数据
const optionChain = ref<any[]>([])

// 生成模拟期权链数据
function generateOptionChain() {
  const strikes = [
    58000, 59000, 60000, 61000, 62000, 63000, 64000, 65000, 66000, 67000, 68000
  ]
  const atmStrike = 63000

  optionChain.value = strikes.map(strike => {
    const isATM = strike === atmStrike
    const distance = Math.abs(strike - atmStrike) / atmStrike

    // 看涨期权价格（行权价越高，价格越低）
    const callPrice = Math.max(0.1, 5000 * (1 - (strike - 58000) / 10000))
    // 看跌期权价格（行权价越低，价格越低）
    const putPrice = Math.max(0.1, 5000 * (1 - (68000 - strike) / 10000))

    return {
      strike,
      isATM,
      call: {
        lastPrice: callPrice.toFixed(2),
        change: (Math.random() - 0.5) * 100,
        changePercent: ((Math.random() - 0.5) * 10).toFixed(2),
        volume: Math.floor(Math.random() * 1000),
        openInterest: Math.floor(Math.random() * 5000),
        delta: (1 - distance * 2).toFixed(4),
        gamma: (0.0001 * (1 - distance)).toFixed(6),
        theta: (-0.5 * (1 - distance)).toFixed(4),
        vega: (10 * (1 - distance)).toFixed(4),
      },
      put: {
        lastPrice: putPrice.toFixed(2),
        change: (Math.random() - 0.5) * 100,
        changePercent: ((Math.random() - 0.5) * 10).toFixed(2),
        volume: Math.floor(Math.random() * 1000),
        openInterest: Math.floor(Math.random() * 5000),
        delta: (-distance * 2).toFixed(4),
        gamma: (0.0001 * (1 - distance)).toFixed(6),
        theta: (-0.5 * (1 - distance)).toFixed(4),
        vega: (10 * (1 - distance)).toFixed(4),
      },
    }
  })
}

// 选中期权
function selectOption(option: any, type: 'call' | 'put') {
  selectedOption.value = {
    ...option,
    type,
    strike: option.strike || (type === 'call' ? option.strike : option.strike),
  }
}

// 持仓数据
const positions = ref<any[]>([
  {
    id: 1,
    symbol: 'BTC-USDT',
    type: 'call',
    strike: 64000,
    expiry: '2024-06-28',
    quantity: 10,
    costPrice: 1200.50,
    lastPrice: 1580.30,
    pnl: 3798.00,
    pnlPercent: 31.64,
    delta: '0.4523',
    gamma: '0.000085',
    theta: '-0.3567',
    vega: '8.2345',
  },
  {
    id: 2,
    symbol: 'ETH-USDT',
    type: 'put',
    strike: 3400,
    expiry: '2024-07-05',
    quantity: 50,
    costPrice: 85.20,
    lastPrice: 72.40,
    pnl: -640.00,
    pnlPercent: -15.02,
    delta: '-0.3876',
    gamma: '0.001234',
    theta: '-0.1234',
    vega: '2.3456',
  },
])

// 订单数据
const orders = ref<any[]>([
  {
    id: 'opt-001',
    symbol: 'BTC-USDT',
    type: 'call',
    side: 'buy',
    strike: 64000,
    price: 1200.50,
    quantity: 10,
    status: 'filled',
    time: '2024-06-20 14:30:25',
  },
  {
    id: 'opt-002',
    symbol: 'ETH-USDT',
    type: 'put',
    side: 'buy',
    strike: 3400,
    price: 85.20,
    quantity: 50,
    status: 'filled',
    time: '2024-06-21 09:15:42',
  },
  {
    id: 'opt-003',
    symbol: 'BTC-USDT',
    type: 'call',
    side: 'sell',
    strike: 66000,
    price: 800.00,
    quantity: 5,
    status: 'pending',
    time: '2024-06-22 10:20:18',
  },
])

const orderStatuses = [
  { key: 'all', label: '全部' },
  { key: 'pending', label: '挂单中' },
  { key: 'filled', label: '已成交' },
  { key: 'canceled', label: '已撤销' },
]

const orderStatusFilter = ref('all')

const orderStatusMap: Record<string, string> = {
  pending: '挂单中',
  filled: '已成交',
  canceled: '已撤销',
}

const filteredOrders = computed(() => {
  if (orderStatusFilter.value === 'all') {
    return orders.value
  }
  return orders.value.filter(o => o.status === orderStatusFilter.value)
})

// 下单弹窗
const showOrderPanel = ref(false)
const orderSide = ref<'buy' | 'sell'>('buy')
const orderType = ref<'limit' | 'market'>('limit')
const orderPrice = ref(0)
const orderQuantity = ref(1)
const isSubmitting = ref(false)

const estimatedPremium = computed(() => {
  const price = orderType.value === 'market'
    ? parseFloat(selectedOption.value?.lastPrice || '0')
    : orderPrice.value
  return price * orderQuantity.value
})

function openOrderPanel(side: 'buy' | 'sell') {
  orderSide.value = side
  orderPrice.value = parseFloat(selectedOption.value?.lastPrice || '0')
  orderQuantity.value = 1
  showOrderPanel.value = true
}

async function submitOrder() {
  isSubmitting.value = true

  // 模拟下单
  await new Promise(resolve => setTimeout(resolve, 1000))

  // 添加到订单列表
  orders.value.unshift({
    id: `opt-${Date.now()}`,
    symbol: selectedSymbol.value,
    type: selectedOption.value?.type,
    side: orderSide.value,
    strike: selectedOption.value?.strike,
    price: orderType.value === 'market' ? selectedOption.value?.lastPrice : orderPrice.value,
    quantity: orderQuantity.value,
    status: 'filled',
    time: new Date().toLocaleString('zh-CN'),
  })

  isSubmitting.value = false
  showOrderPanel.value = false

  // 切换到订单页
  activeTab.value = 'orders'
}

function closePosition(pos: any) {
  if (confirm(`确定要平仓 ${pos.symbol} ${pos.type === 'call' ? '看涨' : '看跌'}期权吗？`)) {
    // 模拟平仓
    positions.value = positions.value.filter(p => p.id !== pos.id)
  }
}

onMounted(() => {
  generateOptionChain()
})
</script>

<style scoped>
.option-trading {
  min-height: 100vh;
}
</style>

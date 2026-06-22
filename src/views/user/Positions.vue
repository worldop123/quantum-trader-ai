<template>
  <div class="space-y-6">
    <!-- Filter Bar -->
    <div class="quantum-card flex flex-wrap items-center gap-3 md:gap-4">
      <div class="flex gap-2 overflow-x-auto">
        <button v-for="tab in tabs" :key="tab.value"
          @click="activeTab = tab.value"
          class="px-4 py-2 rounded text-sm font-medium transition-colors flex-shrink-0 min-h-[44px]"
          :class="activeTab === tab.value ? 'bg-quantum-cyan text-quantum-darker' : 'bg-quantum-border text-gray-400 hover:bg-gray-700'">
          {{ tab.label }}
        </button>
      </div>
      <div class="flex-1"></div>
      <select v-model="filterType" class="quantum-input w-28 md:w-32 text-sm">
        <option value="all">全部类型</option>
        <option value="spot">现货</option>
        <option value="futures">合约</option>
        <option value="option">期权</option>
      </select>
      <input v-model="searchSymbol" type="text" class="quantum-input w-32 md:w-40 text-sm" placeholder="搜索交易对..." />
    </div>

    <!-- Positions Table (PC端) -->
    <div class="quantum-card overflow-hidden hidden md:block">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-quantum-border text-gray-500 text-left">
            <th class="py-3 px-4 font-medium">交易对</th>
            <th class="py-3 px-4 font-medium">类型</th>
            <th class="py-3 px-4 font-medium">方向</th>
            <th class="py-3 px-4 font-medium text-right">数量</th>
            <th class="py-3 px-4 font-medium text-right">开仓价格</th>
            <th class="py-3 px-4 font-medium text-right">当前价格</th>
            <th class="py-3 px-4 font-medium text-right">盈亏</th>
            <th class="py-3 px-4 font-medium text-right">盈亏率</th>
            <th class="py-3 px-4 font-medium text-center">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="position in filteredPositions" :key="position.id" 
            class="border-b border-quantum-border/50 hover:bg-quantum-darker/50 transition-colors">
            <td class="py-3 px-4">
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-full bg-quantum-border flex items-center justify-center">
                  <span class="text-xs font-bold text-gray-400">{{ position.symbol.substring(0, 2) }}</span>
                </div>
                <span class="font-medium text-gray-200">{{ position.symbol }}</span>
              </div>
            </td>
            <td class="py-3 px-4">
              <span class="px-2 py-1 text-xs rounded"
                :class="{
                  'bg-quantum-blue/20 text-quantum-blue': position.type === 'spot',
                  'bg-quantum-yellow/20 text-quantum-yellow': position.type === 'futures',
                  'bg-quantum-purple/20 text-quantum-purple': position.type === 'option'
                }">
                {{ typeLabels[position.type] }}
              </span>
            </td>
            <td class="py-3 px-4">
              <span :class="position.side === 'long' ? 'text-quantum-green' : 'text-quantum-red'">
                {{ position.side === 'long' ? '做多' : '做空' }}
              </span>
              <span v-if="position.leverage" class="text-xs text-gray-500 ml-1">
                {{ position.leverage }}x
              </span>
            </td>
            <td class="py-3 px-4 text-right font-mono text-gray-300">{{ position.quantity }}</td>
            <td class="py-3 px-4 text-right font-mono text-gray-300">${{ position.entryPrice.toLocaleString() }}</td>
            <td class="py-3 px-4 text-right font-mono text-gray-300">${{ position.currentPrice.toLocaleString() }}</td>
            <td class="py-3 px-4 text-right font-mono font-medium">
              <NumberTicker
                :value="position.pnl"
                :decimals="2"
                prefix="$"
                :show-sign="true"
                :flash-on-change="true"
                :up-color="'#10b981'"
                :down-color="'#ef4444'"
              />
            </td>
            <td class="py-3 px-4 text-right font-mono"
              :class="position.pnlPercent >= 0 ? 'text-quantum-green' : 'text-quantum-red'">
              {{ position.pnlPercent >= 0 ? '+' : '' }}{{ position.pnlPercent }}%
            </td>
            <td class="py-3 px-4 text-center">
              <button @click="closePosition(position.id)" class="text-quantum-red hover:text-red-400 text-sm min-h-[44px]">
                平仓
              </button>
            </td>
          </tr>
          <tr v-if="filteredPositions.length === 0">
            <td colspan="9" class="py-12 text-center text-gray-500">
              <Briefcase class="w-12 h-12 mx-auto mb-3 text-gray-600" />
              <p>暂无持仓</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Positions Cards (移动端) -->
    <div class="block md:hidden space-y-3">
      <div v-for="position in filteredPositions" :key="position.id"
        class="quantum-card">
        <!-- Card Header -->
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-quantum-border flex items-center justify-center flex-shrink-0">
              <span class="text-xs font-bold text-gray-400">{{ position.symbol.substring(0, 2) }}</span>
            </div>
            <span class="font-medium text-gray-200">{{ position.symbol }}</span>
          </div>
          <span class="px-2 py-1 text-xs rounded"
            :class="{
              'bg-quantum-blue/20 text-quantum-blue': position.type === 'spot',
              'bg-quantum-yellow/20 text-quantum-yellow': position.type === 'futures',
              'bg-quantum-purple/20 text-quantum-purple': position.type === 'option'
            }">
            {{ typeLabels[position.type] }}
          </span>
        </div>
        <!-- Card Body -->
        <div class="grid grid-cols-2 gap-2 text-xs mb-3">
          <div>
            <p class="text-gray-500">方向</p>
            <p :class="position.side === 'long' ? 'text-quantum-green' : 'text-quantum-red'">
              {{ position.side === 'long' ? '做多' : '做空' }}
              <span v-if="position.leverage" class="text-gray-500 ml-1">{{ position.leverage }}x</span>
            </p>
          </div>
          <div>
            <p class="text-gray-500">数量</p>
            <p class="font-mono text-gray-300">{{ position.quantity }}</p>
          </div>
          <div>
            <p class="text-gray-500">开仓价格</p>
            <p class="font-mono text-gray-300">${{ position.entryPrice.toLocaleString() }}</p>
          </div>
          <div>
            <p class="text-gray-500">当前价格</p>
            <p class="font-mono text-gray-300">${{ position.currentPrice.toLocaleString() }}</p>
          </div>
        </div>
        <!-- Card Footer -->
        <div class="flex items-center justify-between pt-3 border-t border-quantum-border">
          <div>
            <p class="text-gray-500 text-xs">盈亏</p>
            <NumberTicker
              :value="position.pnl"
              :decimals="2"
              prefix="$"
              :show-sign="true"
              :flash-on-change="true"
              :up-color="'#10b981'"
              :down-color="'#ef4444'"
              class="text-base font-mono font-medium"
            />
            <p class="text-xs" :class="position.pnlPercent >= 0 ? 'text-quantum-green' : 'text-quantum-red'">
              {{ position.pnlPercent >= 0 ? '+' : '' }}{{ position.pnlPercent }}%
            </p>
          </div>
          <button @click="closePosition(position.id)" class="text-quantum-red hover:text-red-400 text-sm min-h-[44px] px-3 py-2 border border-quantum-red/30 rounded">
            平仓
          </button>
        </div>
      </div>
      <div v-if="filteredPositions.length === 0" class="quantum-card py-12 text-center text-gray-500">
        <Briefcase class="w-12 h-12 mx-auto mb-3 text-gray-600" />
        <p>暂无持仓</p>
      </div>
    </div>

    <!-- Summary -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="quantum-card">
        <p class="text-gray-500 text-sm mb-1">持仓总数</p>
        <p class="text-2xl font-bold text-gray-200">{{ tradingStore.positions.length }}</p>
      </div>
      <div class="quantum-card">
        <p class="text-gray-500 text-sm mb-1">总盈亏</p>
        <NumberTicker
          :value="tradingStore.totalPnl"
          :decimals="2"
          prefix="$"
          :show-sign="true"
          :flash-on-change="true"
          :up-color="'#10b981'"
          :down-color="'#ef4444'"
          class="text-2xl font-bold font-mono"
        />
      </div>
      <div class="quantum-card">
        <p class="text-gray-500 text-sm mb-1">保证金占用</p>
        <p class="text-2xl font-bold text-gray-200 font-mono">${{ (tradingStore.totalBalance - tradingStore.availableBalance).toLocaleString() }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTradingStore } from '../../stores/trading'
import NumberTicker from '../../components/common/NumberTicker.vue'
import { Briefcase } from 'lucide-vue-next'

const tradingStore = useTradingStore()

const activeTab = ref('all')
const filterType = ref('all')
const searchSymbol = ref('')

const tabs = [
  { label: '全部', value: 'all' },
  { label: '现货', value: 'spot' },
  { label: '合约', value: 'futures' },
  { label: '期权', value: 'option' }
]

const typeLabels: Record<string, string> = {
  spot: '现货',
  futures: '合约',
  option: '期权'
}

const filteredPositions = computed(() => {
  return tradingStore.positions.filter(p => {
    const matchTab = activeTab.value === 'all' || p.type === activeTab.value
    const matchType = filterType.value === 'all' || p.type === filterType.value
    const matchSearch = p.symbol.toLowerCase().includes(searchSymbol.value.toLowerCase())
    return matchTab && matchType && matchSearch
  })
})

function closePosition(id: number) {
  if (confirm('确定要平仓吗？')) {
    const index = tradingStore.positions.findIndex(p => p.id === id)
    if (index > -1) {
      tradingStore.positions.splice(index, 1)
    }
  }
}
</script>

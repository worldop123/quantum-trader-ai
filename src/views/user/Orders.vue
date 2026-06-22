<template>
  <div class="space-y-6">
    <!-- Filter Bar -->
    <div class="quantum-card flex flex-wrap items-center gap-4">
      <div class="flex gap-2">
        <button v-for="tab in tabs" :key="tab.value"
          @click="activeTab = tab.value"
          class="px-4 py-2 rounded text-sm font-medium transition-colors"
          :class="activeTab === tab.value ? 'bg-quantum-cyan text-quantum-darker' : 'bg-quantum-border text-gray-400 hover:bg-gray-700'">
          {{ tab.label }}
          <span v-if="tab.count" class="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-quantum-cyan/20 text-quantum-cyan">
            {{ tab.count }}
          </span>
        </button>
      </div>
      <div class="flex-1"></div>
      <select v-model="filterSide" class="quantum-input w-28 text-sm">
        <option value="all">全部方向</option>
        <option value="buy">买入</option>
        <option value="sell">卖出</option>
      </select>
      <input v-model="searchSymbol" type="text" class="quantum-input w-40 text-sm" placeholder="搜索交易对..." />
      <button @click="cancelAllPending" class="quantum-btn-danger text-sm" v-if="activeTab === 'pending'">
        全部取消
      </button>
    </div>

    <!-- Orders Table -->
    <div class="quantum-card overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-quantum-border text-gray-500 text-left">
            <th class="py-3 px-4 font-medium">订单ID</th>
            <th class="py-3 px-4 font-medium">交易对</th>
            <th class="py-3 px-4 font-medium">类型</th>
            <th class="py-3 px-4 font-medium">方向</th>
            <th class="py-3 px-4 font-medium text-right">价格</th>
            <th class="py-3 px-4 font-medium text-right">数量</th>
            <th class="py-3 px-4 font-medium text-right">已成交</th>
            <th class="py-3 px-4 font-medium">状态</th>
            <th class="py-3 px-4 font-medium">时间</th>
            <th class="py-3 px-4 font-medium text-center">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in filteredOrders" :key="order.id" 
            class="border-b border-quantum-border/50 hover:bg-quantum-darker/50 transition-colors">
            <td class="py-3 px-4 font-mono text-gray-500 text-xs">#{{ order.id }}</td>
            <td class="py-3 px-4 font-medium text-gray-200">{{ order.symbol }}</td>
            <td class="py-3 px-4">
              <span class="px-2 py-1 text-xs rounded bg-quantum-border text-gray-400">
                {{ order.type === 'market' ? '市价' : '限价' }}
              </span>
            </td>
            <td class="py-3 px-4">
              <span :class="order.side === 'buy' ? 'text-quantum-green' : 'text-quantum-red'">
                {{ order.side === 'buy' ? '买入' : '卖出' }}
              </span>
            </td>
            <td class="py-3 px-4 text-right font-mono text-gray-300">
              {{ order.type === 'market' ? '市价' : '$' + order.price.toLocaleString() }}
            </td>
            <td class="py-3 px-4 text-right font-mono text-gray-300">{{ order.quantity }}</td>
            <td class="py-3 px-4 text-right font-mono text-gray-400">{{ order.filledQuantity }}</td>
            <td class="py-3 px-4">
              <span class="px-2 py-1 text-xs rounded"
                :class="{
                  'bg-quantum-green/20 text-quantum-green': order.status === 'filled',
                  'bg-quantum-yellow/20 text-quantum-yellow': order.status === 'pending',
                  'bg-gray-500/20 text-gray-400': order.status === 'cancelled',
                  'bg-quantum-red/20 text-quantum-red': order.status === 'rejected'
                }">
                {{ statusLabels[order.status] }}
              </span>
            </td>
            <td class="py-3 px-4 text-gray-500 text-xs">{{ order.timestamp }}</td>
            <td class="py-3 px-4 text-center">
              <button v-if="order.status === 'pending'" 
                @click="cancelOrder(order.id)" 
                class="text-quantum-red hover:text-red-400 text-sm">
                取消
              </button>
              <span v-else class="text-gray-600 text-sm">-</span>
            </td>
          </tr>
          <tr v-if="filteredOrders.length === 0">
            <td colspan="10" class="py-12 text-center text-gray-500">
              <FileText class="w-12 h-12 mx-auto mb-3 text-gray-600" />
              <p>暂无订单</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between">
      <p class="text-sm text-gray-500">共 {{ filteredOrders.length }} 条记录</p>
      <div class="flex gap-2">
        <button class="px-3 py-1 rounded bg-quantum-border text-gray-400 hover:bg-gray-700 text-sm disabled:opacity-50" disabled>
          上一页
        </button>
        <button class="px-3 py-1 rounded bg-quantum-cyan text-quantum-darker text-sm">
          1
        </button>
        <button class="px-3 py-1 rounded bg-quantum-border text-gray-400 hover:bg-gray-700 text-sm">
          2
        </button>
        <button class="px-3 py-1 rounded bg-quantum-border text-gray-400 hover:bg-gray-700 text-sm">
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTradingStore } from '../../stores/trading'
import { FileText } from 'lucide-vue-next'

const tradingStore = useTradingStore()

const activeTab = ref('all')
const filterSide = ref('all')
const searchSymbol = ref('')

const pendingCount = computed(() => 
  tradingStore.orders.filter(o => o.status === 'pending').length
)

const tabs = [
  { label: '全部', value: 'all', count: null },
  { label: '进行中', value: 'pending', count: pendingCount.value },
  { label: '已成交', value: 'filled', count: null },
  { label: '已取消', value: 'cancelled', count: null }
]

const statusLabels: Record<string, string> = {
  filled: '已成交',
  pending: '进行中',
  cancelled: '已取消',
  rejected: '已拒绝'
}

const filteredOrders = computed(() => {
  return tradingStore.orders.filter(o => {
    const matchTab = activeTab.value === 'all' || o.status === activeTab.value
    const matchSide = filterSide.value === 'all' || o.side === filterSide.value
    const matchSearch = o.symbol.toLowerCase().includes(searchSymbol.value.toLowerCase())
    return matchTab && matchSide && matchSearch
  })
})

function cancelOrder(orderId: number) {
  if (confirm('确定要取消此订单吗？')) {
    tradingStore.cancelOrder(orderId)
  }
}

function cancelAllPending() {
  if (confirm('确定要取消所有进行中的订单吗？')) {
    filteredOrders.value.forEach(o => {
      if (o.status === 'pending') {
        tradingStore.cancelOrder(o.id)
      }
    })
  }
}
</script>

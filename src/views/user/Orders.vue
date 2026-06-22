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
          <span v-if="tab.count" class="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-quantum-cyan/20 text-quantum-cyan">
            {{ tab.count }}
          </span>
        </button>
      </div>
      <div class="flex-1"></div>
      <select v-model="filterSide" class="quantum-input w-24 md:w-28 text-sm">
        <option value="all">全部方向</option>
        <option value="buy">买入</option>
        <option value="sell">卖出</option>
      </select>
      <input v-model="searchSymbol" type="text" class="quantum-input w-32 md:w-40 text-sm" placeholder="搜索交易对..." />
      <button @click="cancelAllPending" class="quantum-btn-danger text-sm min-h-[44px]" v-if="activeTab === 'pending'">
        全部取消
      </button>
    </div>

    <!-- Orders Table (PC端) -->
    <div class="quantum-card overflow-hidden hidden md:block">
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
                @click="handleCancelOrder(order.id)" 
                class="text-quantum-red hover:text-red-400 text-sm min-h-[44px]">
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

    <!-- Orders VirtualList (移动端) -->
    <div class="block md:hidden">
      <VirtualList
        v-if="filteredOrders.length > 0"
        :items="filteredOrders"
        :estimated-item-height="180"
        :buffer-size="3"
        :get-item-key="(item: any) => item.id"
        class="orders-virtual-list"
      >
        <template #default="{ item }">
          <div class="quantum-card mb-3">
            <!-- Card Header -->
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2 min-w-0">
                <span class="font-medium text-gray-200 truncate">{{ item.symbol }}</span>
                <span :class="item.side === 'buy' ? 'text-quantum-green text-xs' : 'text-quantum-red text-xs'">
                  {{ item.side === 'buy' ? '买入' : '卖出' }}
                </span>
              </div>
              <span class="px-2 py-1 text-xs rounded flex-shrink-0"
                :class="{
                  'bg-quantum-green/20 text-quantum-green': item.status === 'filled',
                  'bg-quantum-yellow/20 text-quantum-yellow': item.status === 'pending',
                  'bg-gray-500/20 text-gray-400': item.status === 'cancelled',
                  'bg-quantum-red/20 text-quantum-red': item.status === 'rejected'
                }">
                {{ statusLabels[item.status] }}
              </span>
            </div>
            <!-- Card Body -->
            <div class="grid grid-cols-2 gap-2 text-xs mb-3">
              <div>
                <p class="text-gray-500">订单ID</p>
                <p class="font-mono text-gray-400">#{{ item.id }}</p>
              </div>
              <div>
                <p class="text-gray-500">类型</p>
                <p class="text-gray-300">{{ item.type === 'market' ? '市价' : '限价' }}</p>
              </div>
              <div>
                <p class="text-gray-500">价格</p>
                <p class="font-mono text-gray-300">
                  {{ item.type === 'market' ? '市价' : '$' + item.price.toLocaleString() }}
                </p>
              </div>
              <div>
                <p class="text-gray-500">数量</p>
                <p class="font-mono text-gray-300">{{ item.quantity }}</p>
              </div>
              <div>
                <p class="text-gray-500">已成交</p>
                <p class="font-mono text-gray-400">{{ item.filledQuantity }}</p>
              </div>
              <div>
                <p class="text-gray-500">时间</p>
                <p class="text-gray-500 text-xs">{{ item.timestamp }}</p>
              </div>
            </div>
            <!-- Card Footer -->
            <div v-if="item.status === 'pending'" class="pt-3 border-t border-quantum-border">
              <button @click="handleCancelOrder(item.id)" 
                class="w-full text-quantum-red hover:text-red-400 text-sm min-h-[44px] py-2 border border-quantum-red/30 rounded">
                取消订单
              </button>
            </div>
          </div>
        </template>
        <template #empty>
          <div class="py-12 text-center text-gray-500">
            <FileText class="w-12 h-12 mx-auto mb-3 text-gray-600" />
            <p>暂无订单</p>
          </div>
        </template>
      </VirtualList>
      <div v-else class="quantum-card py-12 text-center text-gray-500">
        <FileText class="w-12 h-12 mx-auto mb-3 text-gray-600" />
        <p>暂无订单</p>
      </div>
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
import VirtualList from '../../components/common/VirtualList.vue'
import { FileText } from 'lucide-vue-next'

const tradingStore = useTradingStore()

const activeTab = ref('all')
const filterSide = ref('all')
const searchSymbol = ref('')

const pendingCount = computed(() => 
  tradingStore.orders.filter(o => o.status === 'pending').length
)

const tabs = computed(() => [
  { label: '全部', value: 'all', count: null },
  { label: '进行中', value: 'pending', count: pendingCount.value },
  { label: '已成交', value: 'filled', count: null },
  { label: '已取消', value: 'cancelled', count: null }
])

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

async function handleCancelOrder(orderId: number) {
  if (confirm('确定要取消此订单吗？')) {
    await tradingStore.cancelOrder(orderId)
  }
}

async function cancelAllPending() {
  if (confirm('确定要取消所有进行中的订单吗？')) {
    const pendingOrders = filteredOrders.value.filter(o => o.status === 'pending')
    await Promise.all(pendingOrders.map(o => tradingStore.cancelOrder(o.id)))
  }
}
</script>

<style scoped>
.orders-virtual-list {
  height: calc(100vh - 280px);
  min-height: 300px;
  padding-right: 4px;
}
</style>

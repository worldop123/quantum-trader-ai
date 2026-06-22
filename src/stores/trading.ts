import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as tradingApi from '../api/trading'
import * as strategyApi from '../api/strategy'

export interface Position {
  id: number
  symbol: string
  type: 'spot' | 'futures' | 'option'
  side: 'long' | 'short'
  quantity: number
  entryPrice: number
  currentPrice: number
  pnl: number
  pnlPercent: number
  leverage?: number
  timestamp: string
}

export interface Order {
  id: number
  symbol: string
  type: 'market' | 'limit'
  side: 'buy' | 'sell'
  quantity: number
  price: number
  status: 'filled' | 'pending' | 'partial' | 'cancelled' | 'rejected'
  filledQuantity: number
  timestamp: string
}

export interface AIStrategy {
  id: number
  name: string
  type: string
  status: 'running' | 'stopped' | 'error'
  winRate: number
  totalTrades: number
  profit: number
  description: string
}

// ============ Mock 数据 (作为 fallback) ============
const mockPositions: Position[] = [
  {
    id: 1,
    symbol: 'BTC/USDT',
    type: 'spot',
    side: 'long',
    quantity: 0.5,
    entryPrice: 65000,
    currentPrice: 67500,
    pnl: 1250,
    pnlPercent: 3.85,
    timestamp: '2026-06-20 10:30:00'
  },
  {
    id: 2,
    symbol: 'ETH/USDT',
    type: 'futures',
    side: 'long',
    quantity: 10,
    entryPrice: 3400,
    currentPrice: 3520,
    pnl: 1200,
    pnlPercent: 3.53,
    leverage: 5,
    timestamp: '2026-06-21 14:20:00'
  },
  {
    id: 3,
    symbol: 'SOL/USDT',
    type: 'spot',
    side: 'long',
    quantity: 100,
    entryPrice: 150,
    currentPrice: 142,
    pnl: -800,
    pnlPercent: -5.33,
    timestamp: '2026-06-19 09:15:00'
  }
]

const mockOrders: Order[] = [
  {
    id: 1001,
    symbol: 'BTC/USDT',
    type: 'limit',
    side: 'buy',
    quantity: 0.2,
    price: 66000,
    status: 'pending',
    filledQuantity: 0,
    timestamp: '2026-06-22 08:00:00'
  },
  {
    id: 1002,
    symbol: 'ETH/USDT',
    type: 'market',
    side: 'sell',
    quantity: 5,
    price: 3510,
    status: 'filled',
    filledQuantity: 5,
    timestamp: '2026-06-22 07:45:00'
  },
  {
    id: 1003,
    symbol: 'BNB/USDT',
    type: 'limit',
    side: 'buy',
    quantity: 10,
    price: 580,
    status: 'cancelled',
    filledQuantity: 0,
    timestamp: '2026-06-21 16:30:00'
  }
]

const mockStrategies: AIStrategy[] = [
  {
    id: 1,
    name: 'Quantum Grid Pro',
    type: 'Grid Trading',
    status: 'running',
    winRate: 68.5,
    totalTrades: 1247,
    profit: 12580.5,
    description: 'AI驱动的网格交易策略，自动调整网格参数'
  },
  {
    id: 2,
    name: 'Neural Trend Hunter',
    type: 'Trend Following',
    status: 'running',
    winRate: 62.3,
    totalTrades: 856,
    profit: 8920.0,
    description: '基于神经网络的趋势追踪策略'
  },
  {
    id: 3,
    name: 'Mean Reversion Elite',
    type: 'Mean Reversion',
    status: 'stopped',
    winRate: 71.2,
    totalTrades: 2341,
    profit: 15670.8,
    description: '均值回归策略，捕捉价格偏离后的回归机会'
  }
]

// 状态映射辅助函数
function mapOrderStatus(status: string): Order['status'] {
  const s = status.toLowerCase()
  if (s === 'filled' || s === 'completed' || s === 'success') return 'filled'
  if (s === 'pending' || s === 'open' || s === 'active' || s === 'processing') return 'pending'
  if (s === 'cancelled' || s === 'canceled') return 'cancelled'
  if (s === 'rejected' || s === 'failed') return 'rejected'
  return 'pending'
}

function mapOrderType(orderType: string): Order['type'] {
  const t = orderType.toLowerCase()
  if (t === 'market') return 'market'
  return 'limit'
}

function mapStrategyStatus(status: string): AIStrategy['status'] {
  const s = status.toLowerCase()
  if (s === 'running' || s === 'active') return 'running'
  if (s === 'stopped' || s === 'paused' || s === 'inactive') return 'stopped'
  if (s === 'error' || s === 'failed') return 'error'
  return 'stopped'
}

export const useTradingStore = defineStore('trading', () => {
  const positions = ref<Position[]>([])
  const orders = ref<Order[]>([])
  const aiStrategies = ref<AIStrategy[]>([])

  const totalBalance = ref(100000)
  const availableBalance = ref(75000)

  // 状态标记
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isMock = ref(false)
  const initialized = ref(false)

  // 各部分独立 loading 状态
  const balanceLoading = ref(false)
  const positionsLoading = ref(false)
  const ordersLoading = ref(false)
  const strategiesLoading = ref(false)

  const totalPnl = computed(() => {
    return positions.value.reduce((sum, p) => sum + p.pnl, 0)
  })

  // ============ 获取账户余额 ============
  async function fetchBalance(): Promise<void> {
    balanceLoading.value = true
    try {
      const balances = await tradingApi.getBalance()
      if (Array.isArray(balances) && balances.length > 0) {
        // 汇总所有币种的 USD 价值
        const total = balances.reduce((sum, b) => sum + (b.usd_value || b.total * 1), 0)
        const available = balances.reduce((sum, b) => sum + (b.usd_value ? b.usd_value * (b.available / (b.total || 1)) : b.available), 0)
        totalBalance.value = total || 100000
        availableBalance.value = available || 75000
        isMock.value = false
      } else {
        // 空数据，使用 mock
        totalBalance.value = 100000
        availableBalance.value = 75000
        isMock.value = true
      }
    } catch (err) {
      console.warn('fetchBalance failed, using mock data:', err)
      totalBalance.value = 100000
      availableBalance.value = 75000
      isMock.value = true
    } finally {
      balanceLoading.value = false
    }
  }

  // ============ 获取持仓 ============
  async function fetchPositions(): Promise<void> {
    positionsLoading.value = true
    try {
      const apiPositions = await tradingApi.getPositions('SPOT')
      if (Array.isArray(apiPositions) && apiPositions.length > 0) {
        positions.value = apiPositions.map((p, idx) => ({
          id: idx + 1,
          symbol: p.symbol,
          type: 'spot' as const,
          side: (p.quantity >= 0 ? 'long' : 'short') as 'long' | 'short',
          quantity: Math.abs(p.quantity),
          entryPrice: p.avg_price,
          currentPrice: p.current_price,
          pnl: p.unrealized_pnl,
          pnlPercent: p.unrealized_pnl_percent,
          timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19)
        }))
        isMock.value = false
      } else {
        positions.value = [...mockPositions]
        isMock.value = true
      }
    } catch (err) {
      console.warn('fetchPositions failed, using mock data:', err)
      positions.value = [...mockPositions]
      isMock.value = true
    } finally {
      positionsLoading.value = false
    }
  }

  // ============ 获取订单 ============
  async function fetchOrders(): Promise<void> {
    ordersLoading.value = true
    try {
      const response = await tradingApi.getOrders({ page: 1, page_size: 50 })
      const items = (response as any)?.items || []
      if (Array.isArray(items) && items.length > 0) {
        orders.value = items.map((o: any) => ({
          id: o.id,
          symbol: o.symbol,
          type: mapOrderType(o.order_type),
          side: o.side === 'buy' ? 'buy' : 'sell',
          quantity: o.quantity,
          price: o.price || 0,
          status: mapOrderStatus(o.status),
          filledQuantity: o.filled_quantity || 0,
          timestamp: (o.created_at || new Date().toISOString()).replace('T', ' ').substring(0, 19)
        }))
        isMock.value = false
      } else {
        orders.value = [...mockOrders]
        isMock.value = true
      }
    } catch (err) {
      console.warn('fetchOrders failed, using mock data:', err)
      orders.value = [...mockOrders]
      isMock.value = true
    } finally {
      ordersLoading.value = false
    }
  }

  // ============ 获取策略列表 ============
  async function fetchStrategies(): Promise<void> {
    strategiesLoading.value = true
    try {
      const response = await strategyApi.getStrategies({ page: 1, page_size: 50 })
      const items = (response as any)?.items || (Array.isArray(response) ? response : [])
      if (Array.isArray(items) && items.length > 0) {
        aiStrategies.value = items.map((s: any) => ({
          id: s.id,
          name: s.name,
          type: s.strategy_type || 'Unknown',
          status: mapStrategyStatus(s.status),
          winRate: s.win_rate || 0,
          totalTrades: s.total_trades || 0,
          profit: s.total_pnl || 0,
          description: s.description || ''
        }))
        isMock.value = false
      } else {
        aiStrategies.value = [...mockStrategies]
        isMock.value = true
      }
    } catch (err) {
      console.warn('fetchStrategies failed, using mock data:', err)
      aiStrategies.value = [...mockStrategies]
      isMock.value = true
    } finally {
      strategiesLoading.value = false
    }
  }

  // ============ 初始化方法 (在布局组件 onMounted 时调用) ============
  async function init(): Promise<void> {
    if (initialized.value) return
    loading.value = true
    error.value = null
    try {
      await Promise.all([
        fetchBalance(),
        fetchPositions(),
        fetchOrders(),
        fetchStrategies()
      ])
      initialized.value = true
    } catch (err: any) {
      error.value = err?.message || '初始化数据失败'
      console.error('Trading store init failed:', err)
    } finally {
      loading.value = false
    }
  }

  // ============ 下单 ============
  async function placeOrder(
    symbol: string,
    side: 'buy' | 'sell',
    type: 'market' | 'limit',
    quantity: number,
    price?: number
  ): Promise<Order> {
    try {
      const response = await tradingApi.placeOrder({
        symbol,
        side,
        order_type: type,
        quantity,
        price: type === 'limit' ? price : undefined
      })
      const newOrder: Order = {
        id: response.id,
        symbol: response.symbol,
        type: mapOrderType(response.order_type),
        side: response.side === 'buy' ? 'buy' : 'sell',
        quantity: response.quantity,
        price: response.price || 0,
        status: mapOrderStatus(response.status),
        filledQuantity: response.filled_quantity || 0,
        timestamp: (response.created_at || new Date().toISOString()).replace('T', ' ').substring(0, 19)
      }
      orders.value.unshift(newOrder)
      return newOrder
    } catch (err) {
      console.warn('placeOrder API failed, using local mock:', err)
      // fallback: 本地创建订单
      const newOrder: Order = {
        id: Date.now(),
        symbol,
        type,
        side,
        quantity,
        price: price || 0,
        status: type === 'market' ? 'filled' : 'pending',
        filledQuantity: type === 'market' ? quantity : 0,
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19)
      }
      orders.value.unshift(newOrder)
      isMock.value = true
      return newOrder
    }
  }

  // ============ 撤单 ============
  async function cancelOrder(orderId: number): Promise<boolean> {
    try {
      await tradingApi.cancelOrder(orderId)
      const order = orders.value.find(o => o.id === orderId)
      if (order && order.status === 'pending') {
        order.status = 'cancelled'
      }
      return true
    } catch (err) {
      console.warn('cancelOrder API failed, using local update:', err)
      const order = orders.value.find(o => o.id === orderId)
      if (order && order.status === 'pending') {
        order.status = 'cancelled'
        return true
      }
      return false
    }
  }

  // ============ 切换策略状态 ============
  async function toggleStrategy(strategyId: number): Promise<boolean> {
    const strategy = aiStrategies.value.find(s => s.id === strategyId)
    if (!strategy) return false

    const newStatus = strategy.status === 'running' ? 'stopped' : 'running'
    try {
      await strategyApi.updateStrategy(strategyId, {
        status: newStatus === 'running' ? 'active' : 'paused'
      })
      strategy.status = newStatus
      return true
    } catch (err) {
      console.warn('toggleStrategy API failed, using local update:', err)
      strategy.status = newStatus
      return true
    }
  }

  return {
    // state
    positions,
    orders,
    aiStrategies,
    totalBalance,
    availableBalance,
    totalPnl,
    // status
    loading,
    error,
    isMock,
    initialized,
    balanceLoading,
    positionsLoading,
    ordersLoading,
    strategiesLoading,
    // actions
    init,
    fetchBalance,
    fetchPositions,
    fetchOrders,
    fetchStrategies,
    placeOrder,
    cancelOrder,
    toggleStrategy
  }
})

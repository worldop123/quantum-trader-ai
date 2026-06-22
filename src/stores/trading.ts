import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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
  status: 'filled' | 'pending' | 'cancelled' | 'rejected'
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

export const useTradingStore = defineStore('trading', () => {
  const positions = ref<Position[]>([
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
  ])

  const orders = ref<Order[]>([
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
  ])

  const aiStrategies = ref<AIStrategy[]>([
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
  ])

  const totalBalance = ref(100000)
  const availableBalance = ref(75000)
  const totalPnl = computed(() => {
    return positions.value.reduce((sum, p) => sum + p.pnl, 0)
  })

  function placeOrder(symbol: string, side: 'buy' | 'sell', type: 'market' | 'limit', quantity: number, price?: number): Order {
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
    return newOrder
  }

  function cancelOrder(orderId: number): boolean {
    const order = orders.value.find(o => o.id === orderId)
    if (order && order.status === 'pending') {
      order.status = 'cancelled'
      return true
    }
    return false
  }

  function toggleStrategy(strategyId: number): boolean {
    const strategy = aiStrategies.value.find(s => s.id === strategyId)
    if (strategy) {
      strategy.status = strategy.status === 'running' ? 'stopped' : 'running'
      return true
    }
    return false
  }

  return {
    positions,
    orders,
    aiStrategies,
    totalBalance,
    availableBalance,
    totalPnl,
    placeOrder,
    cancelOrder,
    toggleStrategy
  }
})

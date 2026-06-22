import apiClient from './request'

export interface OrderCreate {
  symbol: string
  side: 'buy' | 'sell'
  order_type: 'limit' | 'market'
  quantity: number
  price?: number
  api_key_id?: number
}

export interface OrderResponse {
  id: number
  exchange_order_id?: string
  symbol: string
  side: string
  order_type: string
  price?: number
  quantity: number
  filled_quantity: number
  total_amount?: number
  filled_amount: number
  status: string
  created_at: string
  updated_at?: string
  filled_at?: string
}

export interface TradeRecord {
  id: string
  symbol: string
  side: string
  price: number
  quantity: number
  amount: number
  fee: number
  fee_currency: string
  pnl?: number
  pnl_percent?: number
  traded_at: string
}

export interface Position {
  symbol: string
  quantity: number
  avg_price: number
  current_price: number
  unrealized_pnl: number
  unrealized_pnl_percent: number
  market_value: number
}

export interface Balance {
  currency: string
  available: number
  frozen: number
  total: number
  usd_value?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 获取账户余额
export function getBalance(apiKeyId?: number): Promise<Balance[]> {
  return apiClient.get('/trading/balance', {
    params: { api_key_id: apiKeyId }
  })
}

// 获取持仓
export function getPositions(instType = 'SPOT', apiKeyId?: number): Promise<Position[]> {
  return apiClient.get('/trading/positions', {
    params: { inst_type: instType, api_key_id: apiKeyId }
  })
}

// 下单
export function placeOrder(data: OrderCreate): Promise<OrderResponse> {
  return apiClient.post('/trading/orders', data)
}

// 撤单
export function cancelOrder(orderId: number, apiKeyId?: number): Promise<{ success: boolean; message: string; order_id?: number }> {
  return apiClient.delete(`/trading/orders/${orderId}`, {
    params: { api_key_id: apiKeyId }
  })
}

// 获取订单列表（分页）
export function getOrders(params: {
  page?: number
  page_size?: number
  symbol?: string
  status?: string
  side?: string
}): Promise<PaginatedResponse<OrderResponse>> {
  return apiClient.get('/trading/orders', { params })
}

// 获取订单详情
export function getOrderDetail(orderId: number, apiKeyId?: number): Promise<OrderResponse> {
  return apiClient.get(`/trading/orders/${orderId}`, {
    params: { api_key_id: apiKeyId }
  })
}

// 获取成交记录（分页）
export function getTrades(params: {
  page?: number
  page_size?: number
  symbol?: string
  side?: string
  start_date?: string
  end_date?: string
  api_key_id?: number
}): Promise<PaginatedResponse<TradeRecord>> {
  return apiClient.get('/trading/trades', { params })
}

// 获取历史订单（交易所）
export function getOrderHistory(params: {
  page?: number
  page_size?: number
  inst_type?: string
  state?: string
  api_key_id?: number
}): Promise<PaginatedResponse<any>> {
  return apiClient.get('/trading/orders/history', { params })
}

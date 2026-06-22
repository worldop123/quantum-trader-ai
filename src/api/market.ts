import apiClient from './request'

export interface TickerData {
  symbol: string
  last_price: number
  price_change_percent: number
  high_24h: number
  low_24h: number
  volume_24h: number
  turnover_24h: number
}

export interface KlineData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
  volume_ccy?: number
}

export interface DepthData {
  asks: number[][]
  bids: number[][]
  timestamp: number
}

export interface Instrument {
  symbol: string
  base_ccy: string
  quote_ccy: string
  min_size: string
  lot_size: string
  tick_size: string
  state: string
}

// 获取单个交易对行情
export function getTicker(symbol: string, apiKeyId?: number): Promise<TickerData> {
  return apiClient.get(`/market/ticker/${symbol}`, {
    params: { api_key_id: apiKeyId }
  })
}

// 获取所有交易对行情
export function getTickers(instType = 'SPOT', apiKeyId?: number): Promise<TickerData[]> {
  return apiClient.get('/market/tickers', {
    params: { inst_type: instType, api_key_id: apiKeyId }
  })
}

// 获取K线数据
export function getKlines(
  symbol: string,
  bar = '1H',
  limit = 100,
  apiKeyId?: number
): Promise<KlineData[]> {
  return apiClient.get(`/market/klines/${symbol}`, {
    params: { bar, limit, api_key_id: apiKeyId }
  })
}

// 获取深度数据
export function getDepth(symbol: string, sz = 20, apiKeyId?: number): Promise<DepthData> {
  return apiClient.get(`/market/depth/${symbol}`, {
    params: { sz, api_key_id: apiKeyId }
  })
}

// 获取交易对列表
export function getInstruments(instType = 'SPOT', apiKeyId?: number): Promise<Instrument[]> {
  return apiClient.get('/market/instruments', {
    params: { inst_type: instType, api_key_id: apiKeyId }
  })
}

// 搜索交易对
export function searchInstruments(
  keyword: string,
  instType = 'SPOT',
  apiKeyId?: number
): Promise<Instrument[]> {
  return apiClient.get('/market/instruments/search', {
    params: { keyword, inst_type: instType, api_key_id: apiKeyId }
  })
}

import apiClient from './request'

export interface Strategy {
  id: number
  name: string
  description?: string
  strategy_type: string
  symbol: string
  params?: Record<string, any>
  status: string
  is_backtest: boolean
  total_pnl: number
  total_trades: number
  win_rate: number
  max_drawdown: number
  created_at: string
  updated_at?: string
}

export interface StrategyCreate {
  name: string
  description?: string
  strategy_type: string
  symbol: string
  params?: Record<string, any>
}

export interface StrategyUpdate {
  name?: string
  description?: string
  params?: Record<string, any>
  status?: string
}

export interface BacktestRequest {
  strategy_type: string
  symbol: string
  params: Record<string, any>
  start_date: string
  end_date: string
  initial_capital?: number
}

export interface BacktestResult {
  success: boolean
  total_return: number
  total_return_percent: number
  max_drawdown: number
  max_drawdown_percent: number
  win_rate: number
  total_trades: number
  winning_trades: number
  losing_trades: number
  profit_factor: number
  sharpe_ratio: number
  equity_curve: Array<{ timestamp: number; equity: number; price: number }>
  trades: any[]
  warning?: string
}

export interface StrategyType {
  type: string
  name: string
  description: string
  params: Record<string, { type: string; default: number; min?: number; max?: number; label: string }>
  warning?: string
}

export interface AIAnalysisRequest {
  symbol: string
  timeframe?: string
  analysis_type?: string
}

export interface AIAnalysisResponse {
  analysis: string
  summary: string
  signals: string[]
}

// 获取策略列表（分页+搜索）
export function getStrategies(params: {
  page?: number
  page_size?: number
  keyword?: string
  strategy_type?: string
  status?: string
}): Promise<any> {
  return apiClient.get('/strategy', { params })
}

// 创建策略
export function createStrategy(data: StrategyCreate): Promise<Strategy> {
  return apiClient.post('/strategy', data)
}

// 获取策略详情
export function getStrategyDetail(strategyId: number): Promise<Strategy> {
  return apiClient.get(`/strategy/${strategyId}`)
}

// 更新策略
export function updateStrategy(strategyId: number, data: StrategyUpdate): Promise<Strategy> {
  return apiClient.put(`/strategy/${strategyId}`, data)
}

// 删除策略
export function deleteStrategy(strategyId: number): Promise<{ success: boolean; message: string }> {
  return apiClient.delete(`/strategy/${strategyId}`)
}

// 运行回测
export function runBacktest(data: BacktestRequest): Promise<BacktestResult> {
  return apiClient.post('/strategy/backtest', data)
}

// AI行情分析
export function aiAnalyzeMarket(data: AIAnalysisRequest): Promise<AIAnalysisResponse> {
  return apiClient.post('/strategy/ai/analyze', data)
}

// AI策略解释
export function aiExplainStrategy(strategyType: string, params: Record<string, any>): Promise<{ explanation: string }> {
  return apiClient.post('/strategy/ai/explain', { strategy_type: strategyType, params })
}

// 获取策略类型列表
export function getStrategyTypes(): Promise<StrategyType[]> {
  return apiClient.get('/strategy/types/list')
}

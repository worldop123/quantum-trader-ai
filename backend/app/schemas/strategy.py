from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class StrategyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    strategy_type: str = Field(..., description="策略类型: ma_cross/grid/martingale/...")
    symbol: str = Field(..., description="交易对，如 BTC-USDT")
    params: Optional[Dict[str, Any]] = None


class StrategyCreate(StrategyBase):
    pass


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class StrategyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    strategy_type: str
    symbol: str
    params: Optional[Dict[str, Any]]
    status: str
    is_backtest: bool
    total_pnl: float
    total_trades: int
    win_rate: float
    max_drawdown: float
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class StrategyListResponse(BaseModel):
    """策略列表分页响应"""
    items: List[StrategyResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BacktestRequest(BaseModel):
    strategy_type: str
    symbol: str
    params: Dict[str, Any]
    start_date: str
    end_date: str
    initial_capital: float = 10000.0


class BacktestResult(BaseModel):
    total_return: float
    total_return_percent: float
    max_drawdown: float
    max_drawdown_percent: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    profit_factor: float
    sharpe_ratio: float
    equity_curve: List[Dict[str, Any]]
    trades: List[Dict[str, Any]]


class AIAnalysisRequest(BaseModel):
    symbol: str
    timeframe: str = "1h"
    analysis_type: str = "market"  # market/strategy/risk


class AIAnalysisResponse(BaseModel):
    analysis: str
    summary: str
    signals: List[str]

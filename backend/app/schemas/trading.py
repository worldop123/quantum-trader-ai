from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# 订单相关
class OrderCreate(BaseModel):
    symbol: str = Field(..., description="交易对，如 BTC-USDT")
    side: str = Field(..., description="买卖方向: buy/sell")
    order_type: str = Field(..., description="订单类型: limit/market")
    quantity: float = Field(..., gt=0, description="数量")
    price: Optional[float] = Field(None, gt=0, description="限价单价格")
    api_key_id: Optional[int] = Field(None, description="使用的API密钥ID")


class OrderResponse(BaseModel):
    id: int
    exchange_order_id: Optional[str]
    symbol: str
    side: str
    order_type: str
    price: Optional[float]
    quantity: float
    filled_quantity: float
    total_amount: Optional[float]
    filled_amount: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    filled_at: Optional[datetime]

    class Config:
        from_attributes = True


class OrderCancelResponse(BaseModel):
    success: bool
    message: str
    order_id: Optional[int] = None


# 成交记录相关
class TradeRecordResponse(BaseModel):
    id: int
    symbol: str
    side: str
    price: float
    quantity: float
    amount: float
    fee: float
    fee_currency: Optional[str]
    pnl: Optional[float]
    pnl_percent: Optional[float]
    traded_at: datetime

    class Config:
        from_attributes = True


# 持仓相关
class PositionResponse(BaseModel):
    symbol: str
    quantity: float
    avg_price: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    market_value: float


# 余额相关
class BalanceResponse(BaseModel):
    currency: str
    available: float
    frozen: float
    total: float
    usd_value: Optional[float] = None


# 分页响应
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# K线数据
class KlineData(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


# 深度数据
class DepthData(BaseModel):
    asks: List[List[float]]  # 卖盘 [price, quantity]
    bids: List[List[float]]  # 买盘 [price, quantity]
    timestamp: int


# 行情数据
class TickerData(BaseModel):
    symbol: str
    last_price: float
    price_change_percent: float
    high_24h: float
    low_24h: float
    volume_24h: float
    turnover_24h: float

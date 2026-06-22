from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class TradeOrder(Base):
    """交易订单表"""
    __tablename__ = "trade_orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)

    # 交易所订单ID
    exchange_order_id = Column(String(100), nullable=True)

    # 交易对
    symbol = Column(String(50), nullable=False)  # BTC-USDT

    # 订单类型
    order_type = Column(String(20), nullable=False)  # limit/market
    side = Column(String(10), nullable=False)  # buy/sell

    # 价格和数量
    price = Column(Float, nullable=True)  # 限价单价格
    quantity = Column(Float, nullable=False)  # 数量
    filled_quantity = Column(Float, default=0.0)  # 已成交数量

    # 金额
    total_amount = Column(Float, nullable=True)  # 总金额
    filled_amount = Column(Float, default=0.0)  # 已成交金额

    # 状态
    status = Column(String(20), default="pending")  # pending/partially_filled/filled/canceled/rejected

    # 时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    filled_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", backref="orders")
    strategy = relationship("Strategy", backref="orders")


class TradeRecord(Base):
    """成交记录表"""
    __tablename__ = "trade_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("trade_orders.id"), nullable=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)

    # 交易所成交ID
    exchange_trade_id = Column(String(100), nullable=True)

    # 交易对
    symbol = Column(String(50), nullable=False)

    # 成交信息
    side = Column(String(10), nullable=False)  # buy/sell
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)

    # 手续费
    fee = Column(Float, default=0.0)
    fee_currency = Column(String(20), nullable=True)

    # 盈亏
    pnl = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)

    # 时间
    traded_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="trades")
    order = relationship("TradeOrder", backref="trades")
    strategy = relationship("Strategy", backref="trades")

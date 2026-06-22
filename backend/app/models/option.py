"""
期权数据模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class OptionContract(Base):
    """期权合约模型"""
    __tablename__ = "option_contracts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # 合约信息
    symbol = Column(String(50), index=True)  # 合约代码，如 BTC-USD-240628-50000-C
    underlying = Column(String(50), index=True)  # 标的资产，如 BTC-USDT
    option_type = Column(String(10))  # call / put
    strike_price = Column(Float)  # 行权价
    expiry_date = Column(DateTime)  # 到期日

    # 市场数据
    last_price = Column(Float, default=0)  # 最新价
    bid_price = Column(Float, default=0)  # 买一价
    ask_price = Column(Float, default=0)  # 卖一价
    volume_24h = Column(Float, default=0)  # 24h成交量
    open_interest = Column(Float, default=0)  # 持仓量

    # 希腊字母
    delta = Column(Float, default=0)
    gamma = Column(Float, default=0)
    theta = Column(Float, default=0)
    vega = Column(Float, default=0)
    rho = Column(Float, default=0)

    # 隐含波动率
    implied_volatility = Column(Float, default=0)

    # 时间价值/内在价值
    intrinsic_value = Column(Float, default=0)
    time_value = Column(Float, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="option_contracts")


class OptionPosition(Base):
    """期权持仓模型"""
    __tablename__ = "option_positions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    symbol = Column(String(50), index=True)
    option_type = Column(String(10))  # call / put
    strike_price = Column(Float)
    expiry_date = Column(DateTime)

    quantity = Column(Float, default=0)  # 持仓数量
    avg_cost = Column(Float, default=0)  # 平均成本
    current_price = Column(Float, default=0)  # 当前价格

    unrealized_pnl = Column(Float, default=0)  # 未实现盈亏
    unrealized_pnl_percent = Column(Float, default=0)  # 未实现盈亏百分比

    # 希腊字母
    delta = Column(Float, default=0)
    gamma = Column(Float, default=0)
    theta = Column(Float, default=0)
    vega = Column(Float, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="option_positions")


class OptionOrder(Base):
    """期权订单模型"""
    __tablename__ = "option_orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    symbol = Column(String(50), index=True)
    option_type = Column(String(10))  # call / put
    strike_price = Column(Float)
    expiry_date = Column(DateTime)

    side = Column(String(10))  # buy / sell
    order_type = Column(String(20))  # limit / market
    price = Column(Float)  # 下单价格
    quantity = Column(Float)  # 下单数量

    filled_quantity = Column(Float, default=0)  # 已成交数量
    avg_fill_price = Column(Float, default=0)  # 平均成交价

    status = Column(String(20), default="pending")  # pending / filled / canceled / rejected

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="option_orders")

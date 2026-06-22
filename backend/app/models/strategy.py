from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # 策略类型
    strategy_type = Column(String(50), nullable=False)  # ma_cross/grid/martingale/...

    # 交易对
    symbol = Column(String(50), nullable=False)  # BTC-USDT

    # 策略参数（JSON格式存储）
    params = Column(JSON, nullable=True)

    # 状态
    status = Column(String(20), default="stopped")  # running/stopped/paused/error

    # 回测相关
    is_backtest = Column(Boolean, default=False)
    backtest_start_date = Column(DateTime(timezone=True), nullable=True)
    backtest_end_date = Column(DateTime(timezone=True), nullable=True)
    backtest_result = Column(JSON, nullable=True)

    # 收益统计
    total_pnl = Column(Float, default=0.0)  # 总盈亏
    total_trades = Column(Integer, default=0)  # 总交易次数
    win_rate = Column(Float, default=0.0)  # 胜率
    max_drawdown = Column(Float, default=0.0)  # 最大回撤

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="strategies")
    risk_status = relationship("StrategyRiskStatus", back_populates="strategy", uselist=False, cascade="all, delete-orphan")
    logs = relationship("StrategyLog", back_populates="strategy", cascade="all, delete-orphan")


class StrategyLog(Base):
    """策略运行日志表"""
    __tablename__ = "strategy_logs"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)

    # 日志级别：info, warning, error, success
    level = Column(String(20), nullable=False, default="info")
    # 日志类型：signal, order, trade, stop_loss, take_profit, error, status
    log_type = Column(String(50), nullable=False)
    # 日志内容
    message = Column(String(500), nullable=False)
    # 相关数据（JSON格式）
    details = Column(JSON, nullable=True)

    # 相关订单ID
    order_id = Column(String(100), nullable=True)
    # 交易对
    symbol = Column(String(50), nullable=True)
    # 价格
    price = Column(Float, nullable=True)
    # 数量
    quantity = Column(Float, nullable=True)
    # 盈亏
    pnl = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    strategy = relationship("Strategy", back_populates="logs")

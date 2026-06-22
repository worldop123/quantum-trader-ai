"""
风控数据模型
"""
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class RiskSettings(Base):
    """风控设置表"""
    __tablename__ = "risk_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # ========== 系统级风控 ==========
    # 单笔最大亏损（USDT）
    max_single_loss = Column(Float, default=100.0)
    # 单日最大亏损（USDT）
    max_daily_loss = Column(Float, default=500.0)
    # 单品种最大持仓量
    max_position_per_symbol = Column(Float, default=1000.0)
    # 单品种最大持仓金额（USDT）
    max_position_value_per_symbol = Column(Float, default=5000.0)
    # 总仓位上限（占总资金比例，0-1）
    max_total_position_ratio = Column(Float, default=0.8)
    # 连续亏损次数限制
    max_consecutive_losses = Column(Integer, default=5)

    # ========== 策略级风控 ==========
    # 策略最大回撤限制（比例，0-1）
    strategy_max_drawdown = Column(Float, default=0.2)
    # 策略单日亏损上限（USDT）
    strategy_daily_loss_limit = Column(Float, default=200.0)
    # 策略连续亏损次数限制
    strategy_consecutive_losses = Column(Integer, default=3)

    # ========== 单交易级风控 ==========
    # 是否强制止损
    force_stop_loss = Column(Boolean, default=True)
    # 最小盈亏比
    min_risk_reward_ratio = Column(Float, default=1.5)
    # 最大滑点（比例，0-1）
    max_slippage = Column(Float, default=0.005)
    # 单笔最大下单量
    max_order_quantity = Column(Float, default=100.0)

    # ========== 熔断机制 ==========
    # 一级熔断阈值（单日亏损比例，0-1）
    circuit_breaker_level1 = Column(Float, default=0.05)
    # 二级熔断阈值
    circuit_breaker_level2 = Column(Float, default=0.10)
    # 三级熔断阈值
    circuit_breaker_level3 = Column(Float, default=0.15)

    # ========== 其他设置 ==========
    # 是否启用风控
    enabled = Column(Boolean, default=True)
    # 通知开关
    notification_enabled = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="risk_settings")


class RiskStatus(Base):
    """风控状态表（实时状态）"""
    __tablename__ = "risk_status"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # 当前熔断等级（0=正常，1=一级，2=二级，3=三级）
    circuit_breaker_level = Column(Integer, default=0)
    # 今日盈亏
    today_pnl = Column(Float, default=0.0)
    # 今日起始资金
    today_start_balance = Column(Float, default=0.0)
    # 连续亏损次数
    consecutive_losses = Column(Integer, default=0)
    # 总持仓价值
    total_position_value = Column(Float, default=0.0)
    # 账户总权益
    total_equity = Column(Float, default=0.0)

    # 是否暂停交易
    trading_paused = Column(Boolean, default=False)
    # 暂停原因
    pause_reason = Column(String(255), nullable=True)

    # 今日交易次数
    today_trades = Column(Integer, default=0)
    # 今日盈利次数
    today_wins = Column(Integer, default=0)
    # 今日亏损次数
    today_losses = Column(Integer, default=0)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="risk_status")


class RiskLog(Base):
    """风控日志表"""
    __tablename__ = "risk_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 风控类型：system, strategy, trade, circuit_breaker
    risk_type = Column(String(50), nullable=False)
    # 风险等级：info, warning, danger
    level = Column(String(20), nullable=False)
    # 触发原因
    reason = Column(String(500), nullable=False)
    # 执行动作
    action = Column(String(255), nullable=False)
    # 相关数据（JSON格式）
    details = Column(Text, nullable=True)

    # 相关订单ID
    order_id = Column(String(100), nullable=True)
    # 相关策略ID
    strategy_id = Column(Integer, nullable=True)
    # 相关交易对
    symbol = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="risk_logs")


class StrategyRiskStatus(Base):
    """策略风控状态"""
    __tablename__ = "strategy_risk_status"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), unique=True, nullable=False)

    # 策略连续亏损次数
    consecutive_losses = Column(Integer, default=0)
    # 策略最大回撤
    max_drawdown = Column(Float, default=0.0)
    # 策略今日盈亏
    today_pnl = Column(Float, default=0.0)
    # 策略总盈亏
    total_pnl = Column(Float, default=0.0)

    # 是否暂停
    paused = Column(Boolean, default=False)
    # 暂停原因
    pause_reason = Column(String(255), nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    strategy = relationship("Strategy", back_populates="risk_status")

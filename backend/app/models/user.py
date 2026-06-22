from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 用户设置
    theme = Column(String(20), default="dark")  # dark/light
    language = Column(String(10), default="zh")  # zh/en
    rise_color = Column(String(20), default="#00ff88")  # 涨颜色
    fall_color = Column(String(20), default="#ff4757")  # 跌颜色
    notification_enabled = Column(Boolean, default=True)

    # PushPlus
    pushplus_token = Column(String(255), nullable=True)

    # 风控相关关系
    risk_settings = relationship("RiskSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    risk_status = relationship("RiskStatus", back_populates="user", uselist=False, cascade="all, delete-orphan")
    risk_logs = relationship("RiskLog", back_populates="user", cascade="all, delete-orphan")

    # 期权相关关系
    option_contracts = relationship("OptionContract", back_populates="user")
    option_positions = relationship("OptionPosition", back_populates="user")
    option_orders = relationship("OptionOrder", back_populates="user")

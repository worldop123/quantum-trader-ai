from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)  # 密钥名称，如"OKX模拟盘"

    # 交易所类型
    exchange = Column(String(50), nullable=False)  # okx/binance/...

    # 加密存储的密钥信息
    encrypted_api_key = Column(Text, nullable=False)
    encrypted_api_secret = Column(Text, nullable=False)
    encrypted_passphrase = Column(Text, nullable=True)  # OKX需要

    # 环境
    is_demo = Column(Boolean, default=True)  # 是否模拟盘

    # 状态
    is_active = Column(Boolean, default=True)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="api_keys")

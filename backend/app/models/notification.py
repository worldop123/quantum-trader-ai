"""
通知数据模型
用于存储站内通知消息（策略通知、风控预警、订单通知、系统通知等）
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Notification(Base):
    """站内通知表"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 通知类型：strategy / risk / order / system / trade
    type = Column(String(50), nullable=False, default="system")
    # 通知级别：info / warning / danger / success
    level = Column(String(20), nullable=False, default="info")
    # 通知标题
    title = Column(String(255), nullable=False)
    # 通知内容
    message = Column(Text, nullable=False)
    # 附加数据（JSON格式）
    data = Column(JSON, nullable=True)

    # 是否已读
    is_read = Column(Boolean, default=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", backref="notifications")

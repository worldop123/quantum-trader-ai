"""
通知相关API接口
提供站内通知的查询、已读标记、删除等功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import User, Notification
from app.services import get_current_user

router = APIRouter(prefix="/notifications", tags=["通知"])


@router.get("")
async def get_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_read: Optional[bool] = None,
    type: Optional[str] = None,
    level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取通知列表（分页，支持 is_read 筛选）

    Args:
        page: 页码（从1开始）
        page_size: 每页数量
        is_read: 是否已读筛选（True=已读，False=未读，None=全部）
        type: 通知类型筛选（strategy/risk/order/system/trade）
        level: 通知级别筛选（info/warning/danger/success）
    """
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)

    if type:
        query = query.filter(Notification.type == type)

    if level:
        query = query.filter(Notification.level == level)

    total = query.count()
    notifications = query.order_by(Notification.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": [
                {
                    "id": n.id,
                    "type": n.type,
                    "level": n.level,
                    "title": n.title,
                    "message": n.message,
                    "data": n.data,
                    "is_read": n.is_read,
                    "created_at": n.created_at.isoformat() if n.created_at else None,
                    "read_at": n.read_at.isoformat() if n.read_at else None,
                }
                for n in notifications
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
        }
    }


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取未读通知数量"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).count()

    return {
        "code": 0,
        "message": "success",
        "data": {
            "unread_count": count,
        }
    }


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """标记单条通知为已读"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.commit()

    return {
        "code": 0,
        "message": "已标记为已读",
        "data": {
            "id": notification.id,
            "is_read": notification.is_read,
        }
    }


@router.put("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """将当前用户所有未读通知标记为已读"""
    unread_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).all()

    now = datetime.utcnow()
    for notification in unread_notifications:
        notification.is_read = True
        notification.read_at = now

    db.commit()

    return {
        "code": 0,
        "message": "全部已标记为已读",
        "data": {
            "marked_count": len(unread_notifications),
        }
    }


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除单条通知"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    db.delete(notification)
    db.commit()

    return {
        "code": 0,
        "message": "通知已删除",
    }

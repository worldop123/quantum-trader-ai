"""
风控相关API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import User
from app.services import get_current_user, risk_service

router = APIRouter(prefix="/risk", tags=["风控"])


# ========== Schema ==========

class RiskSettingsUpdate(BaseModel):
    """风控设置更新"""
    # 系统级风控
    max_single_loss: Optional[float] = None
    max_daily_loss: Optional[float] = None
    max_position_per_symbol: Optional[float] = None
    max_position_value_per_symbol: Optional[float] = None
    max_total_position_ratio: Optional[float] = None
    max_consecutive_losses: Optional[int] = None

    # 策略级风控
    strategy_max_drawdown: Optional[float] = None
    strategy_daily_loss_limit: Optional[float] = None
    strategy_consecutive_losses: Optional[int] = None

    # 单交易级风控
    force_stop_loss: Optional[bool] = None
    min_risk_reward_ratio: Optional[float] = None
    max_slippage: Optional[float] = None
    max_order_quantity: Optional[float] = None

    # 熔断机制
    circuit_breaker_level1: Optional[float] = None
    circuit_breaker_level2: Optional[float] = None
    circuit_breaker_level3: Optional[float] = None

    # 其他
    enabled: Optional[bool] = None
    notification_enabled: Optional[bool] = None


# ========== API接口 ==========

@router.get("/settings")
async def get_risk_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取风控设置"""
    settings = risk_service.get_settings(db, current_user.id)

    return {
        "code": 0,
        "message": "success",
        "data": {
            "id": settings.id,
            # 系统级风控
            "max_single_loss": settings.max_single_loss,
            "max_daily_loss": settings.max_daily_loss,
            "max_position_per_symbol": settings.max_position_per_symbol,
            "max_position_value_per_symbol": settings.max_position_value_per_symbol,
            "max_total_position_ratio": settings.max_total_position_ratio,
            "max_consecutive_losses": settings.max_consecutive_losses,
            # 策略级风控
            "strategy_max_drawdown": settings.strategy_max_drawdown,
            "strategy_daily_loss_limit": settings.strategy_daily_loss_limit,
            "strategy_consecutive_losses": settings.strategy_consecutive_losses,
            # 单交易级风控
            "force_stop_loss": settings.force_stop_loss,
            "min_risk_reward_ratio": settings.min_risk_reward_ratio,
            "max_slippage": settings.max_slippage,
            "max_order_quantity": settings.max_order_quantity,
            # 熔断机制
            "circuit_breaker_level1": settings.circuit_breaker_level1,
            "circuit_breaker_level2": settings.circuit_breaker_level2,
            "circuit_breaker_level3": settings.circuit_breaker_level3,
            # 其他
            "enabled": settings.enabled,
            "notification_enabled": settings.notification_enabled,
            "updated_at": settings.updated_at.isoformat() if settings.updated_at else None,
        }
    }


@router.put("/settings")
async def update_risk_settings(
    settings_update: RiskSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新风控设置"""
    # 过滤掉None值
    update_data = {k: v for k, v in settings_update.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")

    settings = risk_service.update_settings(db, current_user.id, update_data)

    return {
        "code": 0,
        "message": "设置更新成功",
        "data": {
            "id": settings.id,
            "enabled": settings.enabled,
            "updated_at": settings.updated_at.isoformat() if settings.updated_at else None,
        }
    }


@router.get("/status")
async def get_risk_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取风控状态"""
    status = risk_service.get_status(db, current_user.id)

    return {
        "code": 0,
        "message": "success",
        "data": {
            "circuit_breaker_level": status.circuit_breaker_level,
            "today_pnl": status.today_pnl,
            "today_start_balance": status.today_start_balance,
            "consecutive_losses": status.consecutive_losses,
            "total_position_value": status.total_position_value,
            "total_equity": status.total_equity,
            "trading_paused": status.trading_paused,
            "pause_reason": status.pause_reason,
            "today_trades": status.today_trades,
            "today_wins": status.today_wins,
            "today_losses": status.today_losses,
            "updated_at": status.updated_at.isoformat() if status.updated_at else None,
        }
    }


@router.get("/logs")
async def get_risk_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    risk_type: Optional[str] = None,
    level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取风控日志列表"""
    logs, total = risk_service.get_risk_logs(
        db, current_user.id,
        page=page,
        page_size=page_size,
        risk_type=risk_type,
        level=level,
    )

    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": [
                {
                    "id": log.id,
                    "risk_type": log.risk_type,
                    "level": log.level,
                    "reason": log.reason,
                    "action": log.action,
                    "symbol": log.symbol,
                    "order_id": log.order_id,
                    "strategy_id": log.strategy_id,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in logs
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    }


@router.post("/reset-daily")
async def reset_daily_risk(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """重置每日风控状态（手动触发，测试用）"""
    risk_service.reset_daily_status(db, current_user.id)

    return {
        "code": 0,
        "message": "每日风控状态已重置",
    }


@router.post("/check")
async def test_risk_check(
    symbol: str,
    side: str,
    quantity: float,
    price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """测试风控检查（调试用）"""
    passed, reason = risk_service.check_before_order(
        db, current_user.id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        stop_loss=stop_loss,
        take_profit=take_profit,
    )

    return {
        "code": 0,
        "message": "success",
        "data": {
            "passed": passed,
            "reason": reason,
        }
    }

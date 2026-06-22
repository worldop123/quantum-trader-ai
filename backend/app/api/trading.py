from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import User, TradeOrder, TradeRecord, APIKey
from app.schemas import (
    OrderCreate,
    OrderResponse,
    OrderCancelResponse,
    TradeRecordResponse,
    PositionResponse,
    BalanceResponse,
)
from app.services import get_current_user, okx_service, OKXService, notification_service, risk_service
from app.utils.encryption import decrypt

router = APIRouter(prefix="/trading", tags=["交易"])


def get_okx_service_for_user(
    current_user: User,
    db: Session,
    api_key_id: Optional[int] = None
) -> OKXService:
    """获取用户的OKX服务实例"""
    if api_key_id:
        api_key = db.query(APIKey).filter(
            APIKey.id == api_key_id,
            APIKey.user_id == current_user.id
        ).first()

        if api_key:
            decrypted_api_key = decrypt(api_key.encrypted_api_key)
            decrypted_api_secret = decrypt(api_key.encrypted_api_secret)
            decrypted_passphrase = decrypt(api_key.encrypted_passphrase) if api_key.encrypted_passphrase else None

            return OKXService(
                api_key=decrypted_api_key,
                api_secret=decrypted_api_secret,
                passphrase=decrypted_passphrase,
                is_demo=api_key.is_demo
            )

    # 使用默认配置
    return okx_service


# ========== 账户相关 ==========

@router.get("/balance")
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    api_key_id: Optional[int] = None
):
    """获取账户余额"""
    service = get_okx_service_for_user(current_user, db, api_key_id)
    result = await service.get_balance()

    if result.get("code") != "0":
        raise HTTPException(status_code=400, detail=result.get("msg", "获取余额失败"))

    balances = []
    for data in result.get("data", []):
        for detail in data.get("details", []):
            balances.append(BalanceResponse(
                currency=detail["ccy"],
                available=float(detail["availBal"]),
                frozen=float(detail["frozenBal"]),
                total=float(detail["cashBal"]),
                usd_value=float(detail.get("eqUsd", 0))
            ))

    # WebSocket推送余额更新
    from app.websocket import manager
    await manager.send_balance_update(current_user.id, {
        "balances": [b.model_dump() for b in balances],
        "action": "refresh",
    })

    return balances


@router.get("/positions")
async def get_positions(
    inst_type: str = "SPOT",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    api_key_id: Optional[int] = None
):
    """获取持仓"""
    service = get_okx_service_for_user(current_user, db, api_key_id)
    result = await service.get_positions(inst_type)

    if result.get("code") != "0":
        raise HTTPException(status_code=400, detail=result.get("msg", "获取持仓失败"))

    positions = []
    for data in result.get("data", []):
        positions.append(PositionResponse(
            symbol=data["instId"],
            quantity=float(data["pos"]),
            avg_price=float(data.get("avgPx", 0)),
            current_price=float(data.get("markPx", 0)),
            unrealized_pnl=float(data.get("upl", 0)),
            unrealized_pnl_percent=float(data.get("uplRatio", 0)) * 100,
            market_value=float(data.get("notionalUsd", 0))
        ))

    # WebSocket推送持仓更新
    from app.websocket import manager
    await manager.send_position_update(current_user.id, {
        "positions": [p.model_dump() for p in positions],
        "action": "refresh",
    })

    return positions


# ========== 订单相关 ==========

@router.post("/orders", response_model=OrderResponse)
async def place_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """下单"""
    # ========== 风控检查 ==========
    # 获取当前价格用于风控计算
    current_price = None
    if order_data.order_type == "market":
        # 市价单获取当前行情
        ticker_result = await okx_service.get_ticker(order_data.symbol)
        if ticker_result.get("code") == "0" and ticker_result.get("data"):
            current_price = float(ticker_result["data"][0]["last"])
    else:
        current_price = order_data.price

    # 执行风控检查
    passed, reason = risk_service.check_before_order(
        db, current_user.id,
        symbol=order_data.symbol,
        side=order_data.side,
        quantity=float(order_data.quantity),
        price=current_price,
        stop_loss=getattr(order_data, 'stop_loss', None),
        take_profit=getattr(order_data, 'take_profit', None),
    )

    if not passed:
        raise HTTPException(status_code=403, detail=f"风控拦截: {reason}")

    # ========== 执行下单 ==========
    service = get_okx_service_for_user(current_user, db, order_data.api_key_id)

    # 调用交易所API
    result = await service.place_order(
        inst_id=order_data.symbol,
        side=order_data.side,
        ord_type=order_data.order_type,
        sz=order_data.quantity,
        px=order_data.price
    )

    if result.get("code") != "0":
        raise HTTPException(status_code=400, detail=result.get("msg", "下单失败"))

    # 保存订单到数据库
    exchange_order_id = result["data"][0]["ordId"] if result.get("data") else None

    total_amount = None
    if order_data.price and order_data.order_type == "limit":
        total_amount = order_data.price * order_data.quantity

    new_order = TradeOrder(
        user_id=current_user.id,
        exchange_order_id=exchange_order_id,
        symbol=order_data.symbol,
        side=order_data.side,
        order_type=order_data.order_type,
        price=order_data.price,
        quantity=order_data.quantity,
        total_amount=total_amount,
        status="pending",
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # 发送通知
    if current_user.notification_enabled and current_user.pushplus_token:
        await notification_service.send_order_notification(
            symbol=order_data.symbol,
            side=order_data.side,
            order_type=order_data.order_type,
            price=order_data.price or 0,
            quantity=order_data.quantity,
            status="pending",
            custom_token=current_user.pushplus_token
        )

    # WebSocket推送订单状态更新
    from app.websocket import manager
    await manager.send_order_update(current_user.id, {
        "order_id": new_order.id,
        "exchange_order_id": new_order.exchange_order_id,
        "symbol": new_order.symbol,
        "side": new_order.side,
        "order_type": new_order.order_type,
        "price": new_order.price,
        "quantity": new_order.quantity,
        "status": new_order.status,
        "action": "created",
    })

    return new_order


@router.delete("/orders/{order_id}", response_model=OrderCancelResponse)
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    api_key_id: Optional[int] = None
):
    """撤单"""
    order = db.query(TradeOrder).filter(
        TradeOrder.id == order_id,
        TradeOrder.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if not order.exchange_order_id:
        # 本地订单直接取消
        order.status = "canceled"
        db.commit()
        return OrderCancelResponse(success=True, message="撤单成功", order_id=order.id)

    service = get_okx_service_for_user(current_user, db, api_key_id)
    result = await service.cancel_order(order.symbol, order.exchange_order_id)

    if result.get("code") != "0":
        raise HTTPException(status_code=400, detail=result.get("msg", "撤单失败"))

    order.status = "canceled"
    db.commit()

    # WebSocket推送订单状态更新
    from app.websocket import manager
    await manager.send_order_update(current_user.id, {
        "order_id": order.id,
        "exchange_order_id": order.exchange_order_id,
        "symbol": order.symbol,
        "side": order.side,
        "order_type": order.order_type,
        "price": order.price,
        "quantity": order.quantity,
        "status": "canceled",
        "action": "canceled",
    })

    return OrderCancelResponse(success=True, message="撤单成功", order_id=order.id)


@router.get("/orders")
async def get_orders(
    page: int = 1,
    page_size: int = 20,
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    side: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取订单列表（分页）"""
    query = db.query(TradeOrder).filter(TradeOrder.user_id == current_user.id)

    if symbol:
        query = query.filter(TradeOrder.symbol.contains(symbol.upper()))
    if status:
        query = query.filter(TradeOrder.status == status)
    if side:
        query = query.filter(TradeOrder.side == side)

    total = query.count()
    orders = query.order_by(TradeOrder.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return {
        "items": [OrderResponse.model_validate(o) for o in orders],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    api_key_id: Optional[int] = None
):
    """获取订单详情"""
    order = db.query(TradeOrder).filter(
        TradeOrder.id == order_id,
        TradeOrder.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 如果有交易所订单ID，同步最新状态
    if order.exchange_order_id and order.status in ["pending", "partially_filled"]:
        service = get_okx_service_for_user(current_user, db, api_key_id)
        result = await service.get_order(order.symbol, order.exchange_order_id)

        if result.get("code") == "0" and result.get("data"):
            data = result["data"][0]
            order.status = data["state"]
            order.filled_quantity = float(data.get("fillSz", 0))
            order.filled_amount = float(data.get("fillNotionalUsd", 0))
            if data["state"] == "filled":
                order.filled_at = datetime.utcnow()
            db.commit()
            db.refresh(order)

    return order


# ========== 成交记录相关 ==========

@router.get("/trades")
async def get_trades(
    page: int = 1,
    page_size: int = 20,
    symbol: Optional[str] = None,
    side: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    api_key_id: Optional[int] = None
):
    """获取成交记录（分页）"""
    # 优先从交易所获取
    service = get_okx_service_for_user(current_user, db, api_key_id)
    result = await service.get_trade_history(limit=100)

    trades = []
    if result.get("code") == "0":
        for data in result.get("data", []):
            trades.append({
                "id": data["tradeId"],
                "symbol": data["instId"],
                "side": data["side"],
                "price": float(data["fillPx"]),
                "quantity": float(data["fillSz"]),
                "amount": float(data.get("fillNotionalUsd", 0)),
                "fee": float(data.get("fee", 0)),
                "fee_currency": data.get("feeCcy", ""),
                "pnl": float(data.get("pnl", 0)) if data.get("pnl") else None,
                "pnl_percent": None,
                "traded_at": datetime.fromtimestamp(int(data["ts"]) / 1000),
            })

    # 筛选
    if symbol:
        trades = [t for t in trades if symbol.upper() in t["symbol"]]
    if side:
        trades = [t for t in trades if t["side"] == side]

    # 分页
    total = len(trades)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_trades = trades[start:end]

    return {
        "items": paginated_trades,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


# ========== 订单历史（交易所） ==========

@router.get("/orders/history")
async def get_order_history(
    page: int = 1,
    page_size: int = 20,
    inst_type: str = "SPOT",
    state: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    api_key_id: Optional[int] = None
):
    """获取交易所历史订单"""
    service = get_okx_service_for_user(current_user, db, api_key_id)
    result = await service.get_order_history(inst_type=inst_type, state=state, limit=100)

    if result.get("code") != "0":
        raise HTTPException(status_code=400, detail=result.get("msg", "获取历史订单失败"))

    orders = []
    for data in result.get("data", []):
        orders.append({
            "order_id": data["ordId"],
            "symbol": data["instId"],
            "side": data["side"],
            "order_type": data["ordType"],
            "price": float(data.get("px", 0)),
            "quantity": float(data["sz"]),
            "filled_quantity": float(data.get("fillSz", 0)),
            "total_amount": float(data.get("notionalUsd", 0)),
            "filled_amount": float(data.get("fillNotionalUsd", 0)),
            "status": data["state"],
            "created_at": datetime.fromtimestamp(int(data["cTime"]) / 1000),
            "updated_at": datetime.fromtimestamp(int(data["uTime"]) / 1000),
        })

    # 分页
    total = len(orders)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_orders = orders[start:end]

    return {
        "items": paginated_orders,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }

"""
期权相关API接口

注意：当前期权数据优先尝试通过 okx_service 获取真实行情数据。
当 OKX API 不可用（网络异常、未配置API密钥、无期权权限等）时，
会自动降级到模拟数据，以保证接口可用性。

期权订单会持久化到数据库 OptionOrder 表，期权持仓从 OptionPosition 表查询。
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
import traceback

from app.database import get_db
from app.models import User, OptionOrder, OptionPosition
from app.services import get_current_user, okx_service

router = APIRouter(prefix="/options", tags=["期权"])


# ========== 模拟数据生成（降级方案） ==========

def generate_mock_option_chain(underlying: str, expiry_date: datetime, current_price: float):
    """生成模拟期权链数据（当真实数据不可用时使用）"""
    options = []

    # 生成不同行权价的期权
    strike_prices = []
    base_strike = round(current_price / 1000) * 1000  # 取整到千位
    for i in range(-5, 6):
        strike_prices.append(base_strike + i * 1000)

    for strike in strike_prices:
        # 计算期权价格（简化的Black-Scholes模型模拟）
        moneyness = current_price / strike

        # Call期权
        call_price = max(0, current_price - strike) + random.uniform(50, 200)
        call_delta = min(1, max(0, 0.5 + (moneyness - 1) * 0.3))
        call_gamma = random.uniform(0.0001, 0.001)
        call_theta = random.uniform(-50, -10)
        call_vega = random.uniform(10, 50)

        options.append({
            "symbol": f"{underlying.split('-')[0]}-USD-{expiry_date.strftime('%y%m%d')}-{int(strike)}-C",
            "underlying": underlying,
            "option_type": "call",
            "strike_price": strike,
            "expiry_date": expiry_date.isoformat(),
            "last_price": round(call_price, 2),
            "bid_price": round(call_price - 5, 2),
            "ask_price": round(call_price + 5, 2),
            "volume_24h": random.randint(100, 1000),
            "open_interest": random.randint(500, 5000),
            "delta": round(call_delta, 4),
            "gamma": round(call_gamma, 6),
            "theta": round(call_theta, 2),
            "vega": round(call_vega, 2),
            "implied_volatility": round(random.uniform(0.3, 0.8), 4),
            "intrinsic_value": round(max(0, current_price - strike), 2),
            "time_value": round(max(0, call_price - max(0, current_price - strike)), 2),
        })

        # Put期权
        put_price = max(0, strike - current_price) + random.uniform(50, 200)
        put_delta = min(0, max(-1, -0.5 + (moneyness - 1) * 0.3))
        put_gamma = random.uniform(0.0001, 0.001)
        put_theta = random.uniform(-50, -10)
        put_vega = random.uniform(10, 50)

        options.append({
            "symbol": f"{underlying.split('-')[0]}-USD-{expiry_date.strftime('%y%m%d')}-{int(strike)}-P",
            "underlying": underlying,
            "option_type": "put",
            "strike_price": strike,
            "expiry_date": expiry_date.isoformat(),
            "last_price": round(put_price, 2),
            "bid_price": round(put_price - 5, 2),
            "ask_price": round(put_price + 5, 2),
            "volume_24h": random.randint(100, 1000),
            "open_interest": random.randint(500, 5000),
            "delta": round(put_delta, 4),
            "gamma": round(put_gamma, 6),
            "theta": round(put_theta, 2),
            "vega": round(put_vega, 2),
            "implied_volatility": round(random.uniform(0.3, 0.8), 4),
            "intrinsic_value": round(max(0, strike - current_price), 2),
            "time_value": round(max(0, put_price - max(0, strike - current_price)), 2),
        })

    return options


async def _try_get_real_underlying_price(underlying: str) -> Optional[float]:
    """尝试从OKX获取标的真实价格，失败返回None（3秒超时快速降级）"""
    try:
        import asyncio
        result = await asyncio.wait_for(okx_service.get_ticker(underlying), timeout=3.0)
        if result and result.get("code") == "0" and result.get("data"):
            return float(result["data"][0]["last"])
    except Exception:
        pass
    return None


async def _try_get_real_option_instruments(underlying: str) -> Optional[List[dict]]:
    """尝试从OKX获取真实期权合约列表，失败返回None（3秒超时快速降级）"""
    try:
        import asyncio
        uly = underlying.split("-")[0] + "-USD"
        result = await asyncio.wait_for(okx_service.get_instruments(inst_type="OPTION"), timeout=3.0)
        if result and result.get("code") == "0" and result.get("data"):
            instruments = [
                inst for inst in result["data"]
                if inst.get("uly") == uly
            ]
            if instruments:
                return instruments
    except Exception:
        pass
    return None


# ========== API接口 ==========

@router.get("/expiries")
async def get_option_expiries(
    underlying: str = "BTC-USDT",
    current_user: User = Depends(get_current_user),
):
    """获取期权到期日列表

    优先尝试从OKX获取真实到期日，失败时降级到模拟数据。
    """
    # 尝试获取真实期权合约列表
    real_instruments = await _try_get_real_option_instruments(underlying)

    if real_instruments:
        # 从真实合约中提取到期日
        expiries_map = {}
        for inst in real_instruments:
            expiry = inst.get("expTime")
            if expiry:
                # OKX返回毫秒时间戳
                expiry_dt = datetime.utcfromtimestamp(int(expiry) / 1000)
                date_str = expiry_dt.strftime("%Y-%m-%d")
                if date_str not in expiries_map:
                    expiries_map[date_str] = {
                        "date": date_str,
                        "days_to_expiry": (expiry_dt - datetime.utcnow()).days,
                        "volume_24h": 0,
                        "open_interest": 0,
                    }
                expiries_map[date_str]["volume_24h"] += 1
                expiries_map[date_str]["open_interest"] += 1

        if expiries_map:
            return list(expiries_map.values())

    # 降级到模拟数据
    now = datetime.utcnow()
    expiries = []
    for days in [7, 14, 30, 60, 90]:
        expiry = now + timedelta(days=days)
        expiries.append({
            "date": expiry.strftime("%Y-%m-%d"),
            "days_to_expiry": days,
            "volume_24h": random.randint(1000, 10000),
            "open_interest": random.randint(5000, 50000),
        })

    return expiries


@router.get("/chain")
async def get_option_chain(
    underlying: str = "BTC-USDT",
    expiry_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """获取期权链（T型报价）

    优先尝试从OKX获取真实期权链数据，失败时降级到模拟数据。
    """
    # 尝试获取真实标的价格
    real_price = await _try_get_real_underlying_price(underlying)
    using_mock = real_price is None

    if using_mock:
        # 降级到模拟价格
        current_prices = {
            "BTC-USDT": 65000.0,
            "ETH-USDT": 3500.0,
            "SOL-USDT": 150.0,
        }
        current_price = current_prices.get(underlying, 65000.0)
    else:
        current_price = real_price

    # 解析到期日
    if expiry_date:
        expiry = datetime.fromisoformat(expiry_date)
    else:
        expiry = datetime.utcnow() + timedelta(days=30)

    # 尝试获取真实期权合约
    real_instruments = await _try_get_real_option_instruments(underlying)

    if real_instruments and not using_mock:
        # 使用真实数据构建期权链
        options = []
        for inst in real_instruments:
            inst_expiry = inst.get("expTime")
            if inst_expiry:
                inst_expiry_dt = datetime.utcfromtimestamp(int(inst_expiry) / 1000)
                # 筛选到期日匹配的合约（同一天）
                if inst_expiry_dt.strftime("%Y-%m-%d") != expiry.strftime("%Y-%m-%d"):
                    continue
            else:
                continue

            strike = float(inst.get("stk", 0))
            opt_type = "call" if inst.get("optType") == "C" else "put"
            symbol = inst.get("instId", "")

            # 尝试获取该期权的真实行情
            last_price = 0.0
            try:
                ticker_result = await okx_service.get_ticker(symbol)
                if ticker_result and ticker_result.get("code") == "0" and ticker_result.get("data"):
                    last_price = float(ticker_result["data"][0].get("last", 0))
            except Exception:
                pass

            options.append({
                "symbol": symbol,
                "underlying": underlying,
                "option_type": opt_type,
                "strike_price": strike,
                "expiry_date": inst_expiry_dt.isoformat(),
                "last_price": last_price,
                "bid_price": round(last_price * 0.98, 2) if last_price else 0,
                "ask_price": round(last_price * 1.02, 2) if last_price else 0,
                "volume_24h": 0,
                "open_interest": 0,
                "delta": 0,
                "gamma": 0,
                "theta": 0,
                "vega": 0,
                "implied_volatility": 0,
                "intrinsic_value": round(max(0, current_price - strike) if opt_type == "call" else max(0, strike - current_price), 2),
                "time_value": 0,
            })

        if options:
            calls = [o for o in options if o["option_type"] == "call"]
            puts = [o for o in options if o["option_type"] == "put"]
            calls.sort(key=lambda x: x["strike_price"])
            puts.sort(key=lambda x: x["strike_price"])

            return {
                "underlying": underlying,
                "current_price": current_price,
                "expiry_date": expiry.isoformat(),
                "data_source": "okx",
                "calls": calls,
                "puts": puts,
            }

    # 降级到模拟数据
    options = generate_mock_option_chain(underlying, expiry, current_price)
    calls = [o for o in options if o["option_type"] == "call"]
    puts = [o for o in options if o["option_type"] == "put"]
    calls.sort(key=lambda x: x["strike_price"])
    puts.sort(key=lambda x: x["strike_price"])

    return {
        "underlying": underlying,
        "current_price": current_price,
        "expiry_date": expiry.isoformat(),
        "data_source": "mock",
        "calls": calls,
        "puts": puts,
    }


@router.get("/positions")
async def get_option_positions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取期权持仓（从数据库 OptionPosition 表查询）"""
    positions = db.query(OptionPosition).filter(
        OptionPosition.user_id == current_user.id
    ).order_by(OptionPosition.created_at.desc()).all()

    return [
        {
            "id": p.id,
            "symbol": p.symbol,
            "option_type": p.option_type,
            "strike_price": p.strike_price,
            "expiry_date": p.expiry_date.isoformat() if p.expiry_date else None,
            "quantity": p.quantity,
            "avg_cost": p.avg_cost,
            "current_price": p.current_price,
            "unrealized_pnl": p.unrealized_pnl,
            "unrealized_pnl_percent": p.unrealized_pnl_percent,
            "delta": p.delta,
            "gamma": p.gamma,
            "theta": p.theta,
            "vega": p.vega,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }
        for p in positions
    ]


@router.post("/orders")
async def place_option_order(
    symbol: str,
    side: str,
    order_type: str = "market",
    quantity: float = 1,
    price: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """期权下单

    将订单保存到数据库 OptionOrder 表。
    市价单立即标记为已成交，限价单标记为挂单中。
    """
    # 从合约代码解析期权信息（格式: BTC-USD-240628-65000-C）
    parts = symbol.split("-")
    option_type = "call"
    strike_price = 0.0
    expiry_date = None

    if len(parts) >= 5:
        # parts[0]=BTC, parts[1]=USD, parts[2]=240628, parts[3]=65000, parts[4]=C/P
        option_type = "call" if parts[4] == "C" else "put"
        try:
            strike_price = float(parts[3])
        except ValueError:
            strike_price = 0.0
        try:
            expiry_date = datetime.strptime(parts[2], "%y%m%d")
        except ValueError:
            expiry_date = None

    # 确定成交状态
    is_filled = (order_type == "market")
    fill_price = price or 2500.0

    # 创建订单记录并保存到数据库
    order = OptionOrder(
        user_id=current_user.id,
        symbol=symbol,
        option_type=option_type,
        strike_price=strike_price,
        expiry_date=expiry_date,
        side=side,
        order_type=order_type,
        price=price or fill_price,
        quantity=quantity,
        filled_quantity=quantity if is_filled else 0,
        avg_fill_price=fill_price if is_filled else 0,
        status="filled" if is_filled else "pending",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # 如果市价单成交，更新或创建持仓
    if is_filled:
        _update_or_create_position(
            db,
            user_id=current_user.id,
            symbol=symbol,
            option_type=option_type,
            strike_price=strike_price,
            expiry_date=expiry_date,
            side=side,
            quantity=quantity,
            price=fill_price,
        )
        db.commit()

    return {
        "id": order.id,
        "symbol": order.symbol,
        "side": order.side,
        "order_type": order.order_type,
        "price": order.price,
        "quantity": order.quantity,
        "filled_quantity": order.filled_quantity,
        "avg_fill_price": order.avg_fill_price,
        "status": order.status,
        "created_at": order.created_at.isoformat() if order.created_at else None,
    }


def _update_or_create_position(
    db: Session,
    user_id: int,
    symbol: str,
    option_type: str,
    strike_price: float,
    expiry_date: Optional[datetime],
    side: str,
    quantity: float,
    price: float,
):
    """更新或创建期权持仓记录"""
    position = db.query(OptionPosition).filter(
        OptionPosition.user_id == user_id,
        OptionPosition.symbol == symbol,
    ).first()

    if side == "buy":
        if position:
            # 增加持仓：计算新的平均成本
            total_cost = position.avg_cost * position.quantity + price * quantity
            new_qty = position.quantity + quantity
            position.quantity = new_qty
            position.avg_cost = total_cost / new_qty if new_qty > 0 else 0
        else:
            # 新建持仓
            position = OptionPosition(
                user_id=user_id,
                symbol=symbol,
                option_type=option_type,
                strike_price=strike_price,
                expiry_date=expiry_date,
                quantity=quantity,
                avg_cost=price,
                current_price=price,
                unrealized_pnl=0.0,
                unrealized_pnl_percent=0.0,
            )
            db.add(position)
    elif side == "sell":
        if position:
            # 减少持仓
            position.quantity -= quantity
            if position.quantity <= 0:
                # 持仓清零，删除记录
                db.delete(position)
            # else: 保留剩余持仓


@router.get("/orders")
async def get_option_orders(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取期权订单列表（分页，从数据库查询）"""
    query = db.query(OptionOrder).filter(OptionOrder.user_id == current_user.id)

    if status:
        query = query.filter(OptionOrder.status == status)

    total = query.count()
    orders = query.order_by(OptionOrder.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "items": [
            {
                "id": o.id,
                "symbol": o.symbol,
                "option_type": o.option_type,
                "strike_price": o.strike_price,
                "expiry_date": o.expiry_date.isoformat() if o.expiry_date else None,
                "side": o.side,
                "order_type": o.order_type,
                "price": o.price,
                "quantity": o.quantity,
                "filled_quantity": o.filled_quantity,
                "avg_fill_price": o.avg_fill_price,
                "status": o.status,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in orders
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
    }

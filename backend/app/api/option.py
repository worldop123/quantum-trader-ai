"""
期权相关API接口
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from app.database import get_db
from app.models import User
from app.services import get_current_user

router = APIRouter(prefix="/options", tags=["期权"])


# 模拟期权链数据
def generate_mock_option_chain(underlying: str, expiry_date: datetime, current_price: float):
    """生成模拟期权链数据"""
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


@router.get("/expiries")
async def get_option_expiries(
    underlying: str = "BTC-USDT",
    current_user: User = Depends(get_current_user),
):
    """获取期权到期日列表"""
    # 生成模拟到期日
    now = datetime.utcnow()
    expiries = []

    # 本周、下周、当月、下月、季度
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
    """获取期权链（T型报价）"""
    # 模拟当前价格
    current_prices = {
        "BTC-USDT": 65000.0,
        "ETH-USDT": 3500.0,
        "SOL-USDT": 150.0,
    }
    current_price = current_prices.get(underlying, 65000.0)

    # 解析到期日
    if expiry_date:
        expiry = datetime.fromisoformat(expiry_date)
    else:
        expiry = datetime.utcnow() + timedelta(days=30)

    # 生成模拟期权链
    options = generate_mock_option_chain(underlying, expiry, current_price)

    # 分离看涨和看跌
    calls = [o for o in options if o["option_type"] == "call"]
    puts = [o for o in options if o["option_type"] == "put"]

    # 按行权价排序
    calls.sort(key=lambda x: x["strike_price"])
    puts.sort(key=lambda x: x["strike_price"])

    return {
        "underlying": underlying,
        "current_price": current_price,
        "expiry_date": expiry.isoformat(),
        "calls": calls,
        "puts": puts,
    }


@router.get("/positions")
async def get_option_positions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取期权持仓"""
    # 模拟持仓数据
    positions = [
        {
            "id": 1,
            "symbol": "BTC-USD-240628-65000-C",
            "option_type": "call",
            "strike_price": 65000,
            "expiry_date": "2024-06-28T08:00:00Z",
            "quantity": 1,
            "avg_cost": 2500.0,
            "current_price": 2800.0,
            "unrealized_pnl": 300.0,
            "unrealized_pnl_percent": 12.0,
            "delta": 0.55,
            "gamma": 0.0002,
            "theta": -25.5,
            "vega": 35.2,
        },
        {
            "id": 2,
            "symbol": "BTC-USD-240628-68000-P",
            "option_type": "put",
            "strike_price": 68000,
            "expiry_date": "2024-06-28T08:00:00Z",
            "quantity": 1,
            "avg_cost": 3200.0,
            "current_price": 3500.0,
            "unrealized_pnl": 300.0,
            "unrealized_pnl_percent": 9.375,
            "delta": -0.45,
            "gamma": 0.00018,
            "theta": -28.3,
            "vega": 38.1,
        },
    ]

    return positions


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
    """期权下单（模拟）"""
    # 模拟下单
    order = {
        "id": random.randint(1000, 9999),
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "price": price or 2500.0,
        "quantity": quantity,
        "filled_quantity": quantity if order_type == "market" else 0,
        "avg_fill_price": price or 2500.0,
        "status": "filled" if order_type == "market" else "pending",
        "created_at": datetime.utcnow().isoformat(),
    }

    return order


@router.get("/orders")
async def get_option_orders(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取期权订单列表（分页）"""
    # 模拟订单数据
    orders = []
    for i in range(15):
        orders.append({
            "id": 1000 + i,
            "symbol": f"BTC-USD-240628-{65000 + i * 500}-C",
            "side": "buy" if i % 2 == 0 else "sell",
            "order_type": "limit" if i % 3 == 0 else "market",
            "price": 2500 + i * 10,
            "quantity": 1,
            "filled_quantity": 1 if i % 3 != 0 else 0,
            "avg_fill_price": 2500 + i * 10,
            "status": "filled" if i % 3 != 0 else "pending",
            "created_at": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
        })

    # 筛选
    if status:
        orders = [o for o in orders if o["status"] == status]

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
        "total_pages": (total + page_size - 1) // page_size,
    }

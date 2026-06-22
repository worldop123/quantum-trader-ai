from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import TickerData, KlineData, DepthData
from app.services import get_current_user, okx_service, OKXService
from app.utils.encryption import decrypt
from app.models import APIKey

router = APIRouter(prefix="/market", tags=["行情"])


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


@router.get("/ticker/{symbol}")
async def get_ticker(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    api_key_id: Optional[int] = None
):
    """获取单个交易对行情"""
    service = get_okx_service_for_user(current_user, db, api_key_id)
    result = await service.get_ticker(symbol)

    if result.get("code") != "0" or not result.get("data"):
        raise HTTPException(status_code=400, detail=result.get("msg", "获取行情失败"))

    data = result["data"][0]
    return TickerData(
        symbol=data["instId"],
        last_price=float(data["last"]),
        price_change_percent=float(data["sodUtc0"]),
        high_24h=float(data["high24h"]),
        low_24h=float(data["low24h"]),
        volume_24h=float(data["vol24h"]),
        turnover_24h=float(data["volCcy24h"])
    )


@router.get("/tickers")
async def get_tickers(
    inst_type: str = "SPOT",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    api_key_id: Optional[int] = None
):
    """获取所有交易对行情"""
    service = get_okx_service_for_user(current_user, db, api_key_id)
    result = await service.get_tickers(inst_type)

    if result.get("code") != "0":
        raise HTTPException(status_code=400, detail=result.get("msg", "获取行情失败"))

    tickers = []
    for data in result.get("data", []):
        tickers.append(TickerData(
            symbol=data["instId"],
            last_price=float(data["last"]),
            price_change_percent=float(data.get("sodUtc0", 0)),
            high_24h=float(data["high24h"]),
            low_24h=float(data["low24h"]),
            volume_24h=float(data["vol24h"]),
            turnover_24h=float(data["volCcy24h"])
        ))

    return tickers


@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str,
    bar: str = "1H",
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    api_key_id: Optional[int] = None
):
    """获取K线数据

    bar可选值: 1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/1W/1M
    """
    service = get_okx_service_for_user(current_user, db, api_key_id)
    result = await service.get_candles(symbol, bar=bar, limit=limit)

    if result.get("code") != "0":
        raise HTTPException(status_code=400, detail=result.get("msg", "获取K线失败"))

    klines = []
    for data in result.get("data", []):
        klines.append({
            "timestamp": int(data[0]),
            "open": float(data[1]),
            "high": float(data[2]),
            "low": float(data[3]),
            "close": float(data[4]),
            "volume": float(data[5]),
            "volume_ccy": float(data[6]),
        })

    # 按时间正序排列
    klines.reverse()

    return klines


@router.get("/depth/{symbol}")
async def get_depth(
    symbol: str,
    sz: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    api_key_id: Optional[int] = None
):
    """获取深度数据"""
    service = get_okx_service_for_user(current_user, db, api_key_id)
    result = await service.get_orderbook(symbol, sz=sz)

    if result.get("code") != "0" or not result.get("data"):
        raise HTTPException(status_code=400, detail=result.get("msg", "获取深度失败"))

    data = result["data"][0]

    asks = []
    for ask in data.get("asks", []):
        asks.append([float(ask[0]), float(ask[1])])

    bids = []
    for bid in data.get("bids", []):
        bids.append([float(bid[0]), float(bid[1])])

    return DepthData(
        asks=asks,
        bids=bids,
        timestamp=int(data["ts"])
    )


@router.get("/instruments")
async def get_instruments(
    inst_type: str = "SPOT",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    api_key_id: Optional[int] = None
):
    """获取交易对列表"""
    service = get_okx_service_for_user(current_user, db, api_key_id)
    result = await service.get_instruments(inst_type)

    if result.get("code") != "0":
        raise HTTPException(status_code=400, detail=result.get("msg", "获取交易对失败"))

    instruments = []
    for data in result.get("data", []):
        instruments.append({
            "symbol": data["instId"],
            "base_ccy": data.get("baseCcy", ""),
            "quote_ccy": data.get("quoteCcy", ""),
            "min_size": data.get("minSz", ""),
            "lot_size": data.get("lotSz", ""),
            "tick_size": data.get("tickSz", ""),
            "state": data.get("state", ""),
        })

    return instruments


@router.get("/instruments/search")
async def search_instruments(
    keyword: str,
    inst_type: str = "SPOT",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    api_key_id: Optional[int] = None
):
    """搜索交易对"""
    service = get_okx_service_for_user(current_user, db, api_key_id)
    result = await service.get_instruments(inst_type)

    if result.get("code") != "0":
        raise HTTPException(status_code=400, detail=result.get("msg", "获取交易对失败"))

    keyword = keyword.upper()
    instruments = []
    for data in result.get("data", []):
        if keyword in data["instId"].upper():
            instruments.append({
                "symbol": data["instId"],
                "base_ccy": data.get("baseCcy", ""),
                "quote_ccy": data.get("quoteCcy", ""),
                "min_size": data.get("minSz", ""),
                "lot_size": data.get("lotSz", ""),
                "tick_size": data.get("tickSz", ""),
                "state": data.get("state", ""),
            })

    return instruments

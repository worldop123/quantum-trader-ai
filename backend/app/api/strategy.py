from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Strategy
from app.schemas import (
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
    BacktestRequest,
    BacktestResult,
    AIAnalysisRequest,
    AIAnalysisResponse,
)
from app.services import get_current_user, backtest_service, ai_service, okx_service

router = APIRouter(prefix="/strategy", tags=["策略"])


# ========== 策略管理 ==========

@router.get("", response_model=List[StrategyResponse])
async def get_strategies(
    page: int = 1,
    page_size: int = 20,
    keyword: Optional[str] = None,
    strategy_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取策略列表（分页+搜索）"""
    query = db.query(Strategy).filter(Strategy.user_id == current_user.id)

    if keyword:
        query = query.filter(Strategy.name.contains(keyword))
    if strategy_type:
        query = query.filter(Strategy.strategy_type == strategy_type)
    if status:
        query = query.filter(Strategy.status == status)

    total = query.count()
    strategies = query.order_by(Strategy.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return {
        "items": [StrategyResponse.model_validate(s) for s in strategies],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.post("", response_model=StrategyResponse)
async def create_strategy(
    strategy_data: StrategyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建策略"""
    new_strategy = Strategy(
        user_id=current_user.id,
        name=strategy_data.name,
        description=strategy_data.description,
        strategy_type=strategy_data.strategy_type,
        symbol=strategy_data.symbol,
        params=strategy_data.params,
    )

    db.add(new_strategy)
    db.commit()
    db.refresh(new_strategy)

    return new_strategy


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取策略详情"""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    return strategy


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: int,
    strategy_data: StrategyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新策略"""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    update_data = strategy_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(strategy, key, value)

    db.commit()
    db.refresh(strategy)

    return strategy


@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除策略"""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    db.delete(strategy)
    db.commit()

    return {"success": True, "message": "删除成功"}


# ========== 策略回测 ==========

@router.post("/backtest")
async def run_backtest(
    backtest_data: BacktestRequest,
    current_user: User = Depends(get_current_user)
):
    """运行策略回测"""
    # 获取K线数据
    kline_result = await okx_service.get_candles(
        inst_id=backtest_data.symbol,
        bar="1H",
        limit=500
    )

    if kline_result.get("code") != "0" or not kline_result.get("data"):
        raise HTTPException(status_code=400, detail="获取K线数据失败")

    # 转换K线数据格式
    kline_data = []
    for data in kline_result.get("data", []):
        kline_data.append({
            "timestamp": int(data[0]),
            "open": float(data[1]),
            "high": float(data[2]),
            "low": float(data[3]),
            "close": float(data[4]),
            "volume": float(data[5]),
        })

    # 按时间正序排列
    kline_data.reverse()

    # 运行回测
    result = backtest_service.run_backtest(
        strategy_type=backtest_data.strategy_type,
        kline_data=kline_data,
        params=backtest_data.params,
        initial_capital=backtest_data.initial_capital
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "回测失败"))

    return result


# ========== AI分析 ==========

@router.post("/ai/analyze")
async def ai_analyze_market(
    analysis_data: AIAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """AI行情分析"""
    # 获取K线数据
    kline_result = await okx_service.get_candles(
        inst_id=analysis_data.symbol,
        bar=analysis_data.timeframe,
        limit=100
    )

    if kline_result.get("code") != "0" or not kline_result.get("data"):
        raise HTTPException(status_code=400, detail="获取K线数据失败")

    # 转换K线数据格式
    kline_data = []
    for data in kline_result.get("data", []):
        kline_data.append({
            "timestamp": int(data[0]),
            "open": float(data[1]),
            "high": float(data[2]),
            "low": float(data[3]),
            "close": float(data[4]),
            "volume": float(data[5]),
        })

    kline_data.reverse()

    # 调用AI分析
    result = await ai_service.analyze_market(
        symbol=analysis_data.symbol,
        kline_data=kline_data,
        timeframe=analysis_data.timeframe
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "AI分析失败"))

    return {
        "analysis": result.get("content", ""),
        "summary": "AI技术分析报告",
        "signals": []
    }


@router.post("/ai/explain")
async def ai_explain_strategy(
    strategy_type: str,
    params: dict,
    current_user: User = Depends(get_current_user)
):
    """AI策略解释"""
    result = await ai_service.explain_strategy(strategy_type, params)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "AI解释失败"))

    return {
        "explanation": result.get("content", "")
    }


# ========== 策略类型列表 ==========

@router.get("/types/list")
async def get_strategy_types():
    """获取支持的策略类型"""
    return [
        {
            "type": "ma_cross",
            "name": "均线交叉策略",
            "description": "基于快慢均线交叉的趋势跟踪策略",
            "params": {
                "fast_period": {"type": "int", "default": 5, "min": 2, "max": 50, "label": "快线周期"},
                "slow_period": {"type": "int", "default": 20, "min": 10, "max": 200, "label": "慢线周期"},
            }
        },
        {
            "type": "grid",
            "name": "网格交易策略",
            description: "在价格区间内自动低买高卖的震荡策略",
            "params": {
                "grid_count": {"type": "int", "default": 10, "min": 3, "max": 100, "label": "网格数量"},
                "grid_spacing": {"type": "float", "default": 0.01, "min": 0.001, "max": 0.1, "label": "网格间距(%)"},
                "base_price": {"type": "float", "default": 0, "min": 0, "label": "基准价格"},
            }
        },
        {
            "type": "martingale",
            "name": "马丁格尔策略",
            "description": "亏损后加倍加仓的高风险策略（仅供学习）",
            "params": {
                "base_order_size": {"type": "float", "default": 100, "min": 10, "label": "基础订单金额"},
                "multiplier": {"type": "float", "default": 2.0, "min": 1.1, "max": 5, "label": "加仓倍数"},
                "max_levels": {"type": "int", "default": 5, "min": 1, "max": 20, "label": "最大加仓层数"},
                "take_profit_percent": {"type": "float", "default": 0.01, "min": 0.001, "max": 0.1, "label": "止盈百分比"},
            },
            "warning": "马丁格尔策略风险极高，实际使用可能导致爆仓，仅供学习研究"
        },
    ]


# ========== 策略实盘运行 ==========

@router.post("/{strategy_id}/start")
async def start_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """启动策略实盘运行"""
    from app.services import strategy_engine

    # 检查策略是否存在且属于当前用户
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    if strategy.is_backtest:
        raise HTTPException(status_code=400, detail="回测策略不能实盘运行")

    # 启动策略
    success = await strategy_engine.start_strategy(db, strategy_id, current_user.id)

    if not success:
        raise HTTPException(status_code=400, detail="策略启动失败，可能已在运行中")

    return {
        "code": 0,
        "message": "策略启动成功",
        "data": {
            "strategy_id": strategy_id,
            "status": "running"
        }
    }


@router.post("/{strategy_id}/stop")
async def stop_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """停止策略实盘运行"""
    from app.services import strategy_engine

    # 检查策略是否存在且属于当前用户
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    # 停止策略
    success = await strategy_engine.stop_strategy(db, strategy_id)

    if not success:
        raise HTTPException(status_code=400, detail="策略停止失败，可能未在运行")

    return {
        "code": 0,
        "message": "策略停止成功",
        "data": {
            "strategy_id": strategy_id,
            "status": "stopped"
        }
    }


@router.post("/{strategy_id}/pause")
async def pause_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """暂停策略"""
    from app.services import strategy_engine

    # 检查策略是否存在且属于当前用户
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    # 暂停策略
    success = await strategy_engine.pause_strategy(db, strategy_id)

    if not success:
        raise HTTPException(status_code=400, detail="策略暂停失败")

    return {
        "code": 0,
        "message": "策略暂停成功",
        "data": {
            "strategy_id": strategy_id,
            "status": "paused"
        }
    }


@router.post("/{strategy_id}/resume")
async def resume_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """继续策略"""
    from app.services import strategy_engine

    # 检查策略是否存在且属于当前用户
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    # 继续策略
    success = await strategy_engine.resume_strategy(db, strategy_id)

    if not success:
        raise HTTPException(status_code=400, detail="策略继续失败")

    return {
        "code": 0,
        "message": "策略继续运行成功",
        "data": {
            "strategy_id": strategy_id,
            "status": "running"
        }
    }


@router.get("/{strategy_id}/runtime")
async def get_strategy_runtime(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取策略运行时状态"""
    from app.services import strategy_engine

    # 检查策略是否存在且属于当前用户
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    # 获取运行时状态
    runtime_status = strategy_engine.get_strategy_status(strategy_id)

    if not runtime_status:
        # 策略未在运行，返回基本信息
        return {
            "code": 0,
            "message": "success",
            "data": {
                "strategy_id": strategy_id,
                "running": False,
                "status": strategy.status,
                "total_trades": strategy.total_trades,
                "total_pnl": strategy.total_pnl,
                "win_rate": strategy.win_rate,
                "max_drawdown": strategy.max_drawdown,
            }
        }

    return {
        "code": 0,
        "message": "success",
        "data": runtime_status
    }


@router.get("/running/list")
async def get_running_strategies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户所有运行中的策略"""
    from app.services import strategy_engine

    running_ids = strategy_engine.get_running_strategies()

    # 查询策略信息
    strategies = db.query(Strategy).filter(
        Strategy.id.in_(running_ids),
        Strategy.user_id == current_user.id
    ).all()

    return {
        "code": 0,
        "message": "success",
        "data": {
            "total": len(strategies),
            "items": [
                {
                    "id": s.id,
                    "name": s.name,
                    "strategy_type": s.strategy_type,
                    "symbol": s.symbol,
                    "status": s.status,
                    "runtime": strategy_engine.get_strategy_status(s.id)
                }
                for s in strategies
            ]
        }
    }


# ========== 策略运行日志 ==========

@router.get("/{strategy_id}/logs")
async def get_strategy_logs(
    strategy_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    level: Optional[str] = None,
    log_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取策略运行日志"""
    from app.models import StrategyLog

    # 检查策略是否存在且属于当前用户
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    # 查询日志
    query = db.query(StrategyLog).filter(StrategyLog.strategy_id == strategy_id)

    if level:
        query = query.filter(StrategyLog.level == level)

    if log_type:
        query = query.filter(StrategyLog.log_type == log_type)

    total = query.count()
    logs = query.order_by(StrategyLog.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": [
                {
                    "id": log.id,
                    "level": log.level,
                    "log_type": log.log_type,
                    "message": log.message,
                    "symbol": log.symbol,
                    "price": log.price,
                    "quantity": log.quantity,
                    "pnl": log.pnl,
                    "order_id": log.order_id,
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

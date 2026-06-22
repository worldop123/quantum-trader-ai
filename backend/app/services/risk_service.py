"""
风控服务
三层风控体系 + 三级熔断机制
"""
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, date
import json

from app.models import (
    User,
    RiskSettings,
    RiskStatus,
    RiskLog,
    StrategyRiskStatus,
    Strategy,
    TradeOrder,
)
from app.websocket import manager
from app.services.notification_service import notification_service


class RiskService:
    """风控服务类"""

    def __init__(self):
        pass

    # ========== 初始化 ==========

    def init_user_risk(self, db: Session, user_id: int) -> Tuple[RiskSettings, RiskStatus]:
        """初始化用户风控设置和状态"""
        # 检查是否已存在
        settings = db.query(RiskSettings).filter(RiskSettings.user_id == user_id).first()
        if not settings:
            settings = RiskSettings(user_id=user_id)
            db.add(settings)

        status = db.query(RiskStatus).filter(RiskStatus.user_id == user_id).first()
        if not status:
            status = RiskStatus(user_id=user_id)
            db.add(status)

        db.commit()
        db.refresh(settings)
        db.refresh(status)

        return settings, status

    def init_strategy_risk(self, db: Session, strategy_id: int) -> StrategyRiskStatus:
        """初始化策略风控状态"""
        status = db.query(StrategyRiskStatus).filter(
            StrategyRiskStatus.strategy_id == strategy_id
        ).first()

        if not status:
            status = StrategyRiskStatus(strategy_id=strategy_id)
            db.add(status)
            db.commit()
            db.refresh(status)

        return status

    # ========== 风控检查 ==========

    def check_before_order(
        self,
        db: Session,
        user_id: int,
        symbol: str,
        side: str,
        quantity: float,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        strategy_id: Optional[int] = None,
    ) -> Tuple[bool, str]:
        """
        下单前风控检查
        返回: (是否通过, 原因)
        """
        # 获取风控设置和状态
        settings = db.query(RiskSettings).filter(RiskSettings.user_id == user_id).first()
        if not settings:
            settings, _ = self.init_user_risk(db, user_id)

        status = db.query(RiskStatus).filter(RiskStatus.user_id == user_id).first()
        if not status:
            _, status = self.init_user_risk(db, user_id)

        # 如果风控未启用，直接通过
        if not settings.enabled:
            return True, ""

        # 检查是否暂停交易
        if status.trading_paused:
            return False, f"交易已暂停: {status.pause_reason}"

        # 检查熔断等级
        if status.circuit_breaker_level >= 3:
            return False, "三级熔断已触发，禁止交易"

        if status.circuit_breaker_level >= 2 and side == "buy":
            return False, "二级熔断已触发，只允许平仓"

        # ========== 单交易级风控 ==========

        # 强制止损检查
        if settings.force_stop_loss and not stop_loss and side == "buy":
            return False, "风控规则：每笔交易必须设置止损"

        # 盈亏比检查
        if stop_loss and take_profit and price:
            if side == "buy":
                risk = price - stop_loss
                reward = take_profit - price
            else:
                risk = stop_loss - price
                reward = price - take_profit

            if risk > 0 and reward > 0:
                ratio = reward / risk
                if ratio < settings.min_risk_reward_ratio:
                    return False, f"风控规则：盈亏比不足（当前{ratio:.2f}，最低要求{settings.min_risk_reward_ratio}）"

        # 单笔最大下单量检查
        if quantity > settings.max_order_quantity:
            return False, f"风控规则：单笔下单量超限（当前{quantity}，最大{settings.max_order_quantity}）"

        # 单笔最大亏损检查
        if stop_loss and price:
            if side == "buy":
                single_loss = (price - stop_loss) * quantity
            else:
                single_loss = (stop_loss - price) * quantity

            if single_loss > settings.max_single_loss:
                return False, f"风控规则：单笔亏损超限（预估{single_loss:.2f} USDT，最大{settings.max_single_loss} USDT）"

        # ========== 系统级风控 ==========

        # 连续亏损次数检查
        if status.consecutive_losses >= settings.max_consecutive_losses:
            return False, f"风控规则：连续亏损次数超限（当前{status.consecutive_losses}次，最大{settings.max_consecutive_losses}次）"

        # 单日最大亏损检查
        if abs(status.today_pnl) >= settings.max_daily_loss:
            return False, f"风控规则：单日亏损超限（当前{status.today_pnl:.2f} USDT，最大{settings.max_daily_loss} USDT）"

        # ========== 策略级风控 ==========
        if strategy_id:
            strategy_status = db.query(StrategyRiskStatus).filter(
                StrategyRiskStatus.strategy_id == strategy_id
            ).first()

            if strategy_status and strategy_status.paused:
                return False, f"策略已暂停: {strategy_status.pause_reason}"

            if strategy_status and strategy_status.consecutive_losses >= settings.strategy_consecutive_losses:
                return False, f"策略连续亏损次数超限（当前{strategy_status.consecutive_losses}次）"

        return True, ""

    # ========== 熔断机制 ==========

    def check_circuit_breaker(self, db: Session, user_id: int) -> int:
        """
        检查并更新熔断状态
        返回当前熔断等级
        """
        settings = db.query(RiskSettings).filter(RiskSettings.user_id == user_id).first()
        status = db.query(RiskStatus).filter(RiskStatus.user_id == user_id).first()

        if not settings or not status or status.today_start_balance == 0:
            return 0

        # 计算今日亏损比例
        loss_ratio = abs(status.today_pnl) / status.today_start_balance if status.today_start_balance > 0 else 0

        old_level = status.circuit_breaker_level
        new_level = 0

        if loss_ratio >= settings.circuit_breaker_level3:
            new_level = 3
        elif loss_ratio >= settings.circuit_breaker_level2:
            new_level = 2
        elif loss_ratio >= settings.circuit_breaker_level1:
            new_level = 1

        if new_level != old_level:
            status.circuit_breaker_level = new_level

            # 三级熔断：全部平仓，暂停交易
            if new_level == 3:
                status.trading_paused = True
                status.pause_reason = "三级熔断：单日亏损超过15%"
                self._add_risk_log(
                    db, user_id,
                    risk_type="circuit_breaker",
                    level="danger",
                    reason=f"三级熔断触发：今日亏损{loss_ratio*100:.2f}%",
                    action="全部平仓，暂停交易",
                    symbol="*",
                )

            # 二级熔断：暂停开新仓
            elif new_level == 2:
                self._add_risk_log(
                    db, user_id,
                    risk_type="circuit_breaker",
                    level="warning",
                    reason=f"二级熔断触发：今日亏损{loss_ratio*100:.2f}%",
                    action="暂停开新仓，只允许平仓",
                    symbol="*",
                )

            # 一级熔断：仓位减半
            elif new_level == 1:
                self._add_risk_log(
                    db, user_id,
                    risk_type="circuit_breaker",
                    level="warning",
                    reason=f"一级熔断触发：今日亏损{loss_ratio*100:.2f}%",
                    action="仓位自动降低50%",
                    symbol="*",
                )

            # 熔断解除
            elif old_level > 0 and new_level == 0:
                status.trading_paused = False
                status.pause_reason = None
                self._add_risk_log(
                    db, user_id,
                    risk_type="circuit_breaker",
                    level="info",
                    reason="熔断解除",
                    action="恢复正常交易",
                    symbol="*",
                )

            db.commit()

            # 发送WebSocket通知
            asyncio.create_task(manager.send_risk_alert(user_id, {
                "circuit_breaker_level": new_level,
                "loss_ratio": loss_ratio,
                "message": status.pause_reason or "熔断状态更新"
            }))

            # 发送PushPlus通知
            if settings.notification_enabled:
                notification_service.send_risk_alert(
                    user_id,
                    f"熔断警报 - 等级{new_level}",
                    f"今日亏损: {loss_ratio*100:.2f}%\n状态: {status.pause_reason or '正常'}"
                )

        return new_level

    # ========== 交易后更新 ==========

    def update_after_trade(
        self,
        db: Session,
        user_id: int,
        pnl: float,
        symbol: str,
        strategy_id: Optional[int] = None,
    ):
        """交易完成后更新风控状态"""
        settings = db.query(RiskSettings).filter(RiskSettings.user_id == user_id).first()
        status = db.query(RiskStatus).filter(RiskStatus.user_id == user_id).first()

        if not settings or not status:
            return

        # 更新今日盈亏
        status.today_pnl += pnl
        status.today_trades += 1

        # 更新连续亏损次数
        if pnl < 0:
            status.consecutive_losses += 1
            status.today_losses += 1
        else:
            status.consecutive_losses = 0
            status.today_wins += 1

        db.commit()

        # 检查熔断
        self.check_circuit_breaker(db, user_id)

        # 更新策略风控状态
        if strategy_id:
            self._update_strategy_risk(db, strategy_id, pnl)

        # 发送WebSocket更新
        asyncio.create_task(manager.send_risk_alert(user_id, {
            "today_pnl": status.today_pnl,
            "consecutive_losses": status.consecutive_losses,
            "circuit_breaker_level": status.circuit_breaker_level,
            "trading_paused": status.trading_paused,
        }))

    def _update_strategy_risk(self, db: Session, strategy_id: int, pnl: float):
        """更新策略风控状态"""
        status = db.query(StrategyRiskStatus).filter(
            StrategyRiskStatus.strategy_id == strategy_id
        ).first()

        if not status:
            status = self.init_strategy_risk(db, strategy_id)

        # 更新盈亏
        status.total_pnl += pnl
        status.today_pnl += pnl

        # 更新连续亏损
        if pnl < 0:
            status.consecutive_losses += 1
        else:
            status.consecutive_losses = 0

        # 检查策略风控
        settings = db.query(RiskSettings).filter(
            RiskSettings.user_id == status.strategy.user_id
        ).first()

        if settings:
            # 策略连续亏损检查
            if status.consecutive_losses >= settings.strategy_consecutive_losses:
                status.paused = True
                status.pause_reason = f"连续亏损{status.consecutive_losses}次"
                self._add_risk_log(
                    db, status.strategy.user_id,
                    risk_type="strategy",
                    level="warning",
                    reason=f"策略连续亏损{status.consecutive_losses}次",
                    action="自动暂停策略",
                    strategy_id=strategy_id,
                )

        db.commit()

    # ========== 每日重置 ==========

    def reset_daily_status(self, db: Session, user_id: int):
        """每日重置风控状态"""
        status = db.query(RiskStatus).filter(RiskStatus.user_id == user_id).first()
        if not status:
            return

        status.today_pnl = 0.0
        status.today_trades = 0
        status.today_wins = 0
        status.today_losses = 0
        status.consecutive_losses = 0
        status.circuit_breaker_level = 0
        status.trading_paused = False
        status.pause_reason = None

        # TODO: 更新今日起始资金

        db.commit()

    # ========== 风控日志 ==========

    def _add_risk_log(
        self,
        db: Session,
        user_id: int,
        risk_type: str,
        level: str,
        reason: str,
        action: str,
        details: Optional[Dict] = None,
        order_id: Optional[str] = None,
        strategy_id: Optional[int] = None,
        symbol: Optional[str] = None,
    ):
        """添加风控日志"""
        log = RiskLog(
            user_id=user_id,
            risk_type=risk_type,
            level=level,
            reason=reason,
            action=action,
            details=json.dumps(details) if details else None,
            order_id=order_id,
            strategy_id=strategy_id,
            symbol=symbol,
        )
        db.add(log)
        db.commit()

    def get_risk_logs(
        self,
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        risk_type: Optional[str] = None,
        level: Optional[str] = None,
    ) -> Tuple[list, int]:
        """获取风控日志列表"""
        query = db.query(RiskLog).filter(RiskLog.user_id == user_id)

        if risk_type:
            query = query.filter(RiskLog.risk_type == risk_type)

        if level:
            query = query.filter(RiskLog.level == level)

        total = query.count()
        logs = query.order_by(RiskLog.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        return logs, total

    # ========== 设置管理 ==========

    def get_settings(self, db: Session, user_id: int) -> RiskSettings:
        """获取风控设置"""
        settings = db.query(RiskSettings).filter(RiskSettings.user_id == user_id).first()
        if not settings:
            settings, _ = self.init_user_risk(db, user_id)
        return settings

    def update_settings(
        self,
        db: Session,
        user_id: int,
        settings_data: Dict[str, Any],
    ) -> RiskSettings:
        """更新风控设置"""
        settings = self.get_settings(db, user_id)

        for key, value in settings_data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        db.commit()
        db.refresh(settings)

        return settings

    def get_status(self, db: Session, user_id: int) -> RiskStatus:
        """获取风控状态"""
        status = db.query(RiskStatus).filter(RiskStatus.user_id == user_id).first()
        if not status:
            _, status = self.init_user_risk(db, user_id)
        return status


# 创建全局实例
risk_service = RiskService()

# 延迟导入避免循环引用
import asyncio

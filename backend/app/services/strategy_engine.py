"""
策略实盘运行引擎
支持策略实时运行、自动下单、止盈止损
"""
import asyncio
import time
from typing import Dict, Optional, List, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import Strategy, User, TradeOrder
from app.services import (
    okx_service,
    OKXService,
    risk_service,
    notification_service,
)
from app.websocket import manager
from app.database import get_db


class StrategyRunner:
    """策略运行器"""

    def __init__(self, strategy_id: int, user_id: int):
        self.strategy_id = strategy_id
        self.user_id = user_id
        self.running = False
        self.paused = False
        self.task: Optional[asyncio.Task] = None

        # 策略配置
        self.strategy_type = ""
        self.symbol = ""
        self.params: Dict = {}

        # 运行状态
        self.last_check_time = 0
        self.check_interval = 60  # 默认60秒检查一次
        self.total_trades = 0
        self.win_trades = 0
        self.loss_trades = 0
        self.total_pnl = 0.0

        # 持仓状态
        self.position = None
        self.entry_price = 0.0
        self.stop_loss = 0.0
        self.take_profit = 0.0

    async def start(self, db: Session):
        """启动策略"""
        if self.running:
            return False

        # 加载策略配置
        strategy = db.query(Strategy).filter(Strategy.id == self.strategy_id).first()
        if not strategy:
            return False

        self.strategy_type = strategy.strategy_type
        self.symbol = strategy.symbol
        self.params = strategy.params or {}
        self.check_interval = self.params.get("check_interval", 60)

        self.running = True
        self.paused = False

        # 启动运行循环
        self.task = asyncio.create_task(self._run_loop())

        # 更新策略状态
        strategy.status = "running"
        db.commit()

        # 记录日志
        self._add_log(db, "info", f"策略启动 - {strategy.name}")

        # 发送通知
        notification_service.send_strategy_notification(
            self.user_id,
            "策略启动",
            f"策略 {strategy.name} 已启动\n交易对: {self.symbol}"
        )

        return True

    async def stop(self, db: Session):
        """停止策略"""
        if not self.running:
            return False

        self.running = False

        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None

        # 更新策略状态
        strategy = db.query(Strategy).filter(Strategy.id == self.strategy_id).first()
        if strategy:
            strategy.status = "stopped"
            db.commit()

        # 记录日志
        self._add_log(db, "info", "策略停止")

        return True

    async def pause(self, db: Session):
        """暂停策略"""
        if not self.running or self.paused:
            return False

        self.paused = True

        # 更新策略状态
        strategy = db.query(Strategy).filter(Strategy.id == self.strategy_id).first()
        if strategy:
            strategy.status = "paused"
            db.commit()

        self._add_log(db, "info", "策略暂停")
        return True

    async def resume(self, db: Session):
        """继续策略"""
        if not self.running or not self.paused:
            return False

        self.paused = False

        # 更新策略状态
        strategy = db.query(Strategy).filter(Strategy.id == self.strategy_id).first()
        if strategy:
            strategy.status = "running"
            db.commit()

        self._add_log(db, "info", "策略继续运行")
        return True

    async def _run_loop(self):
        """策略运行主循环"""
        while self.running:
            try:
                if not self.paused:
                    await self._check_and_execute()

                await asyncio.sleep(self.check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️  策略 {self.strategy_id} 运行出错: {e}")
                await asyncio.sleep(self.check_interval)

    async def _check_and_execute(self):
        """检查并执行策略逻辑"""
        # 获取新的数据库会话
        db = next(get_db())
        try:
            # 根据策略类型执行不同逻辑
            if self.strategy_type == "ma_cross":
                await self._execute_ma_cross_strategy(db)
            elif self.strategy_type == "grid":
                await self._execute_grid_strategy(db)
            elif self.strategy_type == "rsi":
                await self._execute_rsi_strategy(db)
            elif self.strategy_type == "macd":
                await self._execute_macd_strategy(db)
            elif self.strategy_type == "boll":
                await self._execute_boll_strategy(db)
            elif self.strategy_type == "dca":
                await self._execute_dca_strategy(db)

            self.last_check_time = time.time()

        except Exception as e:
            print(f"⚠️  策略执行出错: {e}")
        finally:
            db.close()

    async def _execute_ma_cross_strategy(self, db: Session):
        """执行均线交叉策略"""
        # 获取K线数据
        result = await okx_service.get_candles(
            self.symbol,
            bar=self.params.get("timeframe", "1h"),
            limit=50
        )

        if not result or result.get("code") != "0" or not result.get("data"):
            return

        klines = result["data"]
        if len(klines) < 20:
            return

        # 计算均线
        closes = [float(k[4]) for k in klines]
        closes.reverse()  # 按时间正序排列

        fast_period = self.params.get("fast_period", 5)
        slow_period = self.params.get("slow_period", 20)

        fast_ma = self._calculate_ma(closes, fast_period)
        slow_ma = self._calculate_ma(closes, slow_period)

        if len(fast_ma) < 2 or len(slow_ma) < 2:
            return

        # 判断金叉死叉
        prev_fast = fast_ma[-2]
        prev_slow = slow_ma[-2]
        curr_fast = fast_ma[-1]
        curr_slow = slow_ma[-1]

        current_price = closes[-1]

        # 金叉：买入信号
        if prev_fast <= prev_slow and curr_fast > curr_slow:
            if not self.position:
                await self._open_position(db, current_price, "buy")

        # 死叉：卖出信号
        elif prev_fast >= prev_slow and curr_fast < curr_slow:
            if self.position:
                await self._close_position(db, current_price)

        # 检查止盈止损
        if self.position:
            await self._check_stop_loss_take_profit(db, current_price)

    async def _execute_grid_strategy(self, db: Session):
        """执行网格交易策略"""
        # 获取当前价格
        result = await okx_service.get_ticker(self.symbol)
        if not result or result.get("code") != "0" or not result.get("data"):
            return

        current_price = float(result["data"][0]["last"])

        # 网格参数
        upper_price = self.params.get("upper_price", current_price * 1.1)
        lower_price = self.params.get("lower_price", current_price * 0.9)
        grid_count = self.params.get("grid_count", 10)
        grid_amount = self.params.get("grid_amount", 100)  # 每格金额USDT

        # 计算网格间距
        grid_step = (upper_price - lower_price) / grid_count

        # 初始化网格状态（首次运行）
        if not hasattr(self, 'grid_orders'):
            self.grid_orders = {}  # 网格层级 -> 订单信息
            self.grid_profit = 0.0  # 网格总利润
            self.grid_trades = 0  # 网格成交次数
            self._init_grid_orders(db, current_price, lower_price, upper_price, grid_count, grid_step, grid_amount)

        # 检查网格订单成交情况
        await self._check_grid_orders(db, current_price, grid_step, grid_amount)

        # 检查止盈止损（整体策略）
        if self.position:
            await self._check_stop_loss_take_profit(db, current_price)

    def _init_grid_orders(
        self,
        db: Session,
        current_price: float,
        lower_price: float,
        upper_price: float,
        grid_count: int,
        grid_step: float,
        grid_amount: float,
    ):
        """初始化网格订单"""
        self._add_log(
            db, "info",
            f"初始化网格 - 价格区间: {lower_price:.2f} ~ {upper_price:.2f}, 网格数: {grid_count}",
            log_type="grid_init",
            details={
                "lower_price": lower_price,
                "upper_price": upper_price,
                "grid_count": grid_count,
                "grid_step": grid_step,
                "grid_amount": grid_amount,
            }
        )

        # 在当前价格下方放置买单，上方放置卖单
        # 计算当前价格所在的网格层级
        current_level = int((current_price - lower_price) / grid_step)
        current_level = max(0, min(grid_count, current_level))

        # 记录初始基准价
        self.last_grid_price = current_price
        self.grid_base_level = current_level

    async def _check_grid_orders(
        self,
        db: Session,
        current_price: float,
        grid_step: float,
        grid_amount: float,
    ):
        """检查网格订单成交情况"""
        if not hasattr(self, 'last_grid_price'):
            self.last_grid_price = current_price
            return

        # 计算价格变动的网格数
        price_diff = current_price - self.last_grid_price
        levels_moved = int(price_diff / grid_step)

        if abs(levels_moved) < 1:
            return

        # 价格上涨，触发卖单
        if levels_moved > 0:
            for i in range(levels_moved):
                sell_price = self.last_grid_price + (i + 1) * grid_step
                quantity = grid_amount / sell_price

                # 如果有持仓，卖出获利
                if self.position == "buy":
                    # 计算网格利润
                    grid_profit = grid_step * quantity
                    self.grid_profit += grid_profit
                    self.grid_trades += 1

                    self._add_log(
                        db, "success",
                        f"网格卖出 @ {sell_price:.2f}, 利润: {grid_profit:.2f} USDT",
                        log_type="grid_sell",
                        price=sell_price,
                        quantity=quantity,
                        pnl=grid_profit,
                    )

                    # 更新持仓状态（简化处理，实际需要管理多个网格仓位）
                    self.position = None
                    self.entry_price = 0.0

                # 在更高位置挂卖单
                # 简化处理：只维护一个持仓

        # 价格下跌，触发买单
        elif levels_moved < 0:
            for i in range(abs(levels_moved)):
                buy_price = self.last_grid_price - (i + 1) * grid_step
                quantity = grid_amount / buy_price

                # 如果没有持仓，买入
                if not self.position:
                    # 风控检查
                    passed, reason = risk_service.check_before_order(
                        db, self.user_id,
                        symbol=self.symbol,
                        side="buy",
                        quantity=quantity,
                        price=buy_price,
                        strategy_id=self.strategy_id,
                    )

                    if passed:
                        self.position = "buy"
                        self.entry_price = buy_price

                        self._add_log(
                            db, "info",
                            f"网格买入 @ {buy_price:.2f}",
                            log_type="grid_buy",
                            price=buy_price,
                            quantity=quantity,
                        )
                    else:
                        self._add_log(db, "warning", f"网格买入被风控拦截: {reason}")
                        break

        # 更新最后价格
        self.last_grid_price = current_price

    async def _execute_rsi_strategy(self, db: Session):
        """执行RSI超买超卖策略"""
        # 获取K线数据
        result = await okx_service.get_candles(
            self.symbol,
            bar=self.params.get("timeframe", "1h"),
            limit=50
        )

        if not result or result.get("code") != "0" or not result.get("data"):
            return

        klines = result["data"]
        if len(klines) < 20:
            return

        # 计算RSI
        closes = [float(k[4]) for k in klines]
        closes.reverse()  # 按时间正序排列

        rsi_period = self.params.get("rsi_period", 14)
        overbought = self.params.get("overbought", 70)
        oversold = self.params.get("oversold", 30)

        rsi = self._calculate_rsi(closes, rsi_period)

        if len(rsi) < 2:
            return

        current_rsi = rsi[-1]
        prev_rsi = rsi[-2]
        current_price = closes[-1]

        # RSI从超卖区回升，买入信号
        if prev_rsi <= oversold and current_rsi > oversold:
            if not self.position:
                await self._open_position(db, current_price, "buy")

        # RSI从超买区回落，卖出信号
        elif prev_rsi >= overbought and current_rsi < overbought:
            if self.position:
                await self._close_position(db, current_price)

        # 检查止盈止损
        if self.position:
            await self._check_stop_loss_take_profit(db, current_price)

    async def _execute_macd_strategy(self, db: Session):
        """执行MACD策略"""
        # 获取K线数据
        result = await okx_service.get_candles(
            self.symbol,
            bar=self.params.get("timeframe", "1h"),
            limit=60
        )

        if not result or result.get("code") != "0" or not result.get("data"):
            return

        klines = result["data"]
        if len(klines) < 40:
            return

        # 计算MACD
        closes = [float(k[4]) for k in klines]
        closes.reverse()  # 按时间正序排列

        fast_period = self.params.get("fast_period", 12)
        slow_period = self.params.get("slow_period", 26)
        signal_period = self.params.get("signal_period", 9)

        macd_line, signal_line, histogram = self._calculate_macd(
            closes, fast_period, slow_period, signal_period
        )

        if len(macd_line) < 2 or len(signal_line) < 2:
            return

        current_price = closes[-1]

        # 金叉：MACD线上穿信号线，买入信号
        if macd_line[-2] <= signal_line[-2] and macd_line[-1] > signal_line[-1]:
            if not self.position:
                await self._open_position(db, current_price, "buy")

        # 死叉：MACD线下穿信号线，卖出信号
        elif macd_line[-2] >= signal_line[-2] and macd_line[-1] < signal_line[-1]:
            if self.position:
                await self._close_position(db, current_price)

        # 检查止盈止损
        if self.position:
            await self._check_stop_loss_take_profit(db, current_price)

    async def _execute_boll_strategy(self, db: Session):
        """执行布林带策略"""
        # 获取K线数据
        result = await okx_service.get_candles(
            self.symbol,
            bar=self.params.get("timeframe", "1h"),
            limit=50
        )

        if not result or result.get("code") != "0" or not result.get("data"):
            return

        klines = result["data"]
        if len(klines) < 25:
            return

        # 计算布林带
        closes = [float(k[4]) for k in klines]
        closes.reverse()  # 按时间正序排列

        period = self.params.get("period", 20)
        std_dev = self.params.get("std_dev", 2)

        upper, middle, lower = self._calculate_boll(closes, period, std_dev)

        if len(upper) < 2 or len(middle) < 2 or len(lower) < 2:
            return

        current_price = closes[-1]
        prev_price = closes[-2]

        # 价格触及下轨，买入信号
        if prev_price > lower[-2] and current_price <= lower[-1]:
            if not self.position:
                await self._open_position(db, current_price, "buy")

        # 价格触及上轨，卖出信号
        elif prev_price < upper[-2] and current_price >= upper[-1]:
            if self.position:
                await self._close_position(db, current_price)

        # 检查止盈止损
        if self.position:
            await self._check_stop_loss_take_profit(db, current_price)

    async def _execute_dca_strategy(self, db: Session):
        """执行定投策略（DCA）"""
        # 获取当前价格
        result = await okx_service.get_ticker(self.symbol)
        if not result or result.get("code") != "0" or not result.get("data"):
            return

        current_price = float(result["data"][0]["last"])

        # 定投参数
        period = self.params.get("period", "day")  # hour/day/week
        amount = self.params.get("amount", 100)  # 每次定投金额USDT
        max_orders = self.params.get("max_orders", 0)  # 最大定投次数，0表示不限制

        # 计算下次定投时间
        if not hasattr(self, 'dca_last_buy_time'):
            self.dca_last_buy_time = 0
            self.dca_buy_count = 0

        # 计算间隔时间（秒）
        interval_map = {
            "hour": 3600,
            "day": 86400,
            "week": 604800,
        }
        interval = interval_map.get(period, 86400)

        current_time = time.time()

        # 检查是否到达定投时间
        if current_time - self.dca_last_buy_time >= interval:
            # 检查是否达到最大定投次数
            if max_orders > 0 and self.dca_buy_count >= max_orders:
                self._add_log(db, "info", "已达到最大定投次数，策略自动停止")
                await self.stop(db)
                return

            # 执行定投买入
            quantity = amount / current_price

            # 风控检查
            passed, reason = risk_service.check_before_order(
                db, self.user_id,
                symbol=self.symbol,
                side="buy",
                quantity=quantity,
                price=current_price,
                strategy_id=self.strategy_id,
            )

            if passed:
                try:
                    order_result = await okx_service.place_order(
                        inst_id=self.symbol,
                        side="buy",
                        ord_type="market",
                        sz=str(quantity),
                    )

                    if order_result and order_result.get("code") == "0":
                        self.dca_last_buy_time = current_time
                        self.dca_buy_count += 1

                        # 更新持仓状态（简化处理，累加持仓）
                        if not self.position:
                            self.position = "buy"
                            self.entry_price = current_price
                        else:
                            # 简单平均成本
                            total_cost = self.entry_price * (self.dca_buy_count - 1) + current_price
                            self.entry_price = total_cost / self.dca_buy_count

                        self._add_log(
                            db, "success",
                            f"定投买入 #{self.dca_buy_count} @ {current_price:.2f}, 金额: {amount:.2f} USDT",
                            log_type="dca_buy",
                            price=current_price,
                            quantity=quantity,
                            details={
                                "buy_count": self.dca_buy_count,
                                "amount": amount,
                                "period": period,
                            },
                        )

                        # 发送订单更新
                        await manager.send_order_update(self.user_id, {
                            "strategy_id": self.strategy_id,
                            "action": "dca_buy",
                            "side": "buy",
                            "price": current_price,
                            "quantity": quantity,
                            "buy_count": self.dca_buy_count,
                        })
                    else:
                        self._add_log(db, "error", f"定投下单失败: {order_result.get('msg', '未知错误')}")
                except Exception as e:
                    self._add_log(db, "error", f"定投下单异常: {str(e)}")
            else:
                self._add_log(db, "warning", f"定投被风控拦截: {reason}")

        # 检查止盈止损（如果有持仓）
        if self.position:
            await self._check_stop_loss_take_profit(db, current_price)

    def _calculate_ma(self, prices: List[float], period: int) -> List[float]:
        """计算移动平均线"""
        if len(prices) < period:
            return []

        ma = []
        for i in range(period - 1, len(prices)):
            ma.append(sum(prices[i - period + 1:i + 1]) / period)
        return ma

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """计算RSI指标"""
        if len(prices) < period + 1:
            return []

        rsi = []
        gains = []
        losses = []

        # 计算价格变化
        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        # 计算初始平均涨跌
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        # 计算第一个RSI
        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - (100 / (1 + rs)))

        # 平滑计算后续RSI
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period

            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - (100 / (1 + rs)))

        return rsi

    def _calculate_macd(self, prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        """计算MACD指标"""
        if len(prices) < slow_period + signal_period:
            return [], [], []

        # 计算EMA
        def calculate_ema(data: List[float], period: int) -> List[float]:
            if len(data) < period:
                return []

            ema = []
            # 初始值用SMA
            sma = sum(data[:period]) / period
            ema.append(sma)

            multiplier = 2 / (period + 1)
            for i in range(period, len(data)):
                ema.append((data[i] - ema[-1]) * multiplier + ema[-1])

            return ema

        fast_ema = calculate_ema(prices, fast_period)
        slow_ema = calculate_ema(prices, slow_period)

        # 对齐长度
        min_len = min(len(fast_ema), len(slow_ema))
        fast_ema = fast_ema[-min_len:]
        slow_ema = slow_ema[-min_len:]

        # 计算MACD线
        macd_line = [fast_ema[i] - slow_ema[i] for i in range(min_len)]

        # 计算信号线
        signal_line = calculate_ema(macd_line, signal_period)

        # 计算柱状图
        histogram = []
        signal_start = len(macd_line) - len(signal_line)
        for i in range(len(signal_line)):
            histogram.append(macd_line[signal_start + i] - signal_line[i])

        return macd_line, signal_line, histogram

    def _calculate_boll(self, prices: List[float], period: int = 20, std_dev: float = 2):
        """计算布林带"""
        if len(prices) < period:
            return [], [], []

        upper = []
        middle = []
        lower = []

        for i in range(period - 1, len(prices)):
            # 计算中轨（SMA）
            window = prices[i - period + 1:i + 1]
            sma = sum(window) / period
            middle.append(sma)

            # 计算标准差
            variance = sum((x - sma) ** 2 for x in window) / period
            std = variance ** 0.5

            # 计算上下轨
            upper.append(sma + std_dev * std)
            lower.append(sma - std_dev * std)

        return upper, middle, lower

    async def _open_position(self, db: Session, price: float, side: str):
        """开仓"""
        # 风控检查
        passed, reason = risk_service.check_before_order(
            db, self.user_id,
            symbol=self.symbol,
            side=side,
            quantity=self.params.get("quantity", 0.01),
            price=price,
            stop_loss=self.params.get("stop_loss", 0),
            take_profit=self.params.get("take_profit", 0),
            strategy_id=self.strategy_id,
        )

        if not passed:
            self._add_log(db, "warning", f"开仓被风控拦截: {reason}")
            return

        # 计算下单数量
        amount = self.params.get("amount", 100)  # USDT
        quantity = amount / price

        # 下单
        try:
            result = await okx_service.place_order(
                inst_id=self.symbol,
                side=side,
                ord_type="market",
                sz=str(quantity),
            )

            if result and result.get("code") == "0":
                self.position = side
                self.entry_price = price
                self.stop_loss = price * (1 - self.params.get("stop_loss_pct", 0.02)) if side == "buy" else price * (1 + self.params.get("stop_loss_pct", 0.02))
                self.take_profit = price * (1 + self.params.get("take_profit_pct", 0.04)) if side == "buy" else price * (1 - self.params.get("take_profit_pct", 0.04))

                self._add_log(db, "info", f"开仓成功 - {side.upper()} @ {price:.2f}")

                # 发送订单更新
                await manager.send_order_update(self.user_id, {
                    "strategy_id": self.strategy_id,
                    "action": "open",
                    "side": side,
                    "price": price,
                    "quantity": quantity,
                })
            else:
                self._add_log(db, "error", f"开仓失败: {result.get('msg', '未知错误')}")

        except Exception as e:
            self._add_log(db, "error", f"开仓异常: {str(e)}")

    async def _close_position(self, db: Session, price: float):
        """平仓"""
        if not self.position:
            return

        side = "sell" if self.position == "buy" else "buy"

        try:
            result = await okx_service.place_order(
                inst_id=self.symbol,
                side=side,
                ord_type="market",
                sz=str(self.params.get("quantity", 0.01)),
            )

            if result and result.get("code") == "0":
                # 计算盈亏
                if self.position == "buy":
                    pnl = (price - self.entry_price) * self.params.get("quantity", 0.01)
                else:
                    pnl = (self.entry_price - price) * self.params.get("quantity", 0.01)

                self.total_pnl += pnl
                self.total_trades += 1

                if pnl > 0:
                    self.win_trades += 1
                else:
                    self.loss_trades += 1

                # 更新风控状态
                risk_service.update_after_trade(
                    db, self.user_id,
                    pnl=pnl,
                    symbol=self.symbol,
                    strategy_id=self.strategy_id,
                )

                self._add_log(db, "info", f"平仓成功 - {side.upper()} @ {price:.2f}, 盈亏: {pnl:.2f} USDT")

                # 重置持仓
                self.position = None
                self.entry_price = 0.0
                self.stop_loss = 0.0
                self.take_profit = 0.0

                # 发送订单更新
                await manager.send_order_update(self.user_id, {
                    "strategy_id": self.strategy_id,
                    "action": "close",
                    "side": side,
                    "price": price,
                    "pnl": pnl,
                })
            else:
                self._add_log(db, "error", f"平仓失败: {result.get('msg', '未知错误')}")

        except Exception as e:
            self._add_log(db, "error", f"平仓异常: {str(e)}")

    async def _check_stop_loss_take_profit(self, db: Session, current_price: float):
        """检查止盈止损"""
        if not self.position:
            return

        if self.position == "buy":
            # 止损
            if current_price <= self.stop_loss:
                self._add_log(db, "warning", f"触发止损 @ {current_price:.2f}")
                await self._close_position(db, current_price)
                return

            # 止盈
            if current_price >= self.take_profit:
                self._add_log(db, "info", f"触发止盈 @ {current_price:.2f}")
                await self._close_position(db, current_price)
                return
        else:
            # 做空止损
            if current_price >= self.stop_loss:
                self._add_log(db, "warning", f"触发止损 @ {current_price:.2f}")
                await self._close_position(db, current_price)
                return

            # 做止盈
            if current_price <= self.take_profit:
                self._add_log(db, "info", f"触发止盈 @ {current_price:.2f}")
                await self._close_position(db, current_price)
                return

    def _add_log(
        self,
        db: Session,
        level: str,
        message: str,
        log_type: str = "info",
        details: Optional[Dict] = None,
        order_id: Optional[str] = None,
        price: Optional[float] = None,
        quantity: Optional[float] = None,
        pnl: Optional[float] = None,
    ):
        """添加策略运行日志"""
        from app.models import StrategyLog

        try:
            log = StrategyLog(
                strategy_id=self.strategy_id,
                level=level,
                log_type=log_type,
                message=message,
                details=details,
                order_id=order_id,
                symbol=self.symbol,
                price=price,
                quantity=quantity,
                pnl=pnl,
            )
            db.add(log)
            db.commit()
        except Exception as e:
            print(f"⚠️  保存策略日志失败: {e}")

        print(f"📝 策略 {self.strategy_id} [{level}]: {message}")

    def get_status(self) -> Dict[str, Any]:
        """获取策略运行状态"""
        status = {
            "strategy_id": self.strategy_id,
            "running": self.running,
            "paused": self.paused,
            "position": self.position,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "total_trades": self.total_trades,
            "win_trades": self.win_trades,
            "loss_trades": self.loss_trades,
            "total_pnl": self.total_pnl,
            "last_check_time": self.last_check_time,
            "check_interval": self.check_interval,
        }

        # 网格策略额外信息
        if self.strategy_type == "grid":
            status["grid_profit"] = getattr(self, 'grid_profit', 0.0)
            status["grid_trades"] = getattr(self, 'grid_trades', 0)
            status["last_grid_price"] = getattr(self, 'last_grid_price', 0.0)

        return status


class StrategyEngine:
    """策略引擎 - 管理所有运行中的策略"""

    def __init__(self):
        self.runners: Dict[int, StrategyRunner] = {}  # strategy_id -> runner

    async def start_strategy(self, db: Session, strategy_id: int, user_id: int) -> bool:
        """启动策略"""
        if strategy_id in self.runners:
            return False

        runner = StrategyRunner(strategy_id, user_id)
        success = await runner.start(db)

        if success:
            self.runners[strategy_id] = runner

        return success

    async def stop_strategy(self, db: Session, strategy_id: int) -> bool:
        """停止策略"""
        runner = self.runners.get(strategy_id)
        if not runner:
            return False

        success = await runner.stop(db)
        if success:
            del self.runners[strategy_id]

        return success

    async def pause_strategy(self, db: Session, strategy_id: int) -> bool:
        """暂停策略"""
        runner = self.runners.get(strategy_id)
        if not runner:
            return False

        return await runner.pause(db)

    async def resume_strategy(self, db: Session, strategy_id: int) -> bool:
        """继续策略"""
        runner = self.runners.get(strategy_id)
        if not runner:
            return False

        return await runner.resume(db)

    def get_strategy_status(self, strategy_id: int) -> Optional[Dict]:
        """获取策略运行状态"""
        runner = self.runners.get(strategy_id)
        if not runner:
            return None
        return runner.get_status()

    def get_running_strategies(self) -> List[int]:
        """获取所有运行中的策略ID"""
        return list(self.runners.keys())

    def is_running(self, strategy_id: int) -> bool:
        """检查策略是否在运行"""
        return strategy_id in self.runners

    async def restore_running_strategies(self, db: Session):
        """服务启动时恢复所有运行中的策略"""
        try:
            from app.models import Strategy
            # 查询所有状态为running或paused的策略
            strategies = db.query(Strategy).filter(
                Strategy.status.in_(["running", "paused"])
            ).all()

            if not strategies:
                print("✅ 没有需要恢复的运行中策略")
                return

            print(f"🔄 正在恢复 {len(strategies)} 个运行中的策略...")

            for strategy in strategies:
                try:
                    # 创建策略运行器
                    runner = StrategyRunner(strategy.id, strategy.user_id)
                    # 加载策略配置
                    runner.strategy_type = strategy.strategy_type
                    runner.symbol = strategy.symbol
                    runner.params = strategy.params or {}
                    runner.check_interval = runner.params.get("check_interval", 60)
                    runner.running = True
                    runner.paused = (strategy.status == "paused")

                    # 启动运行循环
                    runner.task = asyncio.create_task(runner._run_loop())
                    self.runners[strategy.id] = runner

                    print(f"  ✅ 策略 {strategy.id} ({strategy.name}) 已恢复 - 状态: {strategy.status}")
                except Exception as e:
                    print(f"  ❌ 恢复策略 {strategy.id} 失败: {e}")
                    # 恢复失败，更新状态为stopped
                    strategy.status = "stopped"
                    db.commit()

            print(f"✅ 策略恢复完成，共恢复 {len(self.runners)} 个策略")
        except Exception as e:
            print(f"❌ 恢复运行中策略时出错: {e}")


# 创建全局实例
strategy_engine = StrategyEngine()

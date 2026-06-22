import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from datetime import datetime


class BacktestService:
    """策略回测服务"""

    def __init__(self):
        pass

    def run_backtest(
        self,
        strategy_type: str,
        kline_data: List[Dict[str, Any]],
        params: Dict[str, Any],
        initial_capital: float = 10000.0
    ) -> Dict[str, Any]:
        """运行回测

        Args:
            strategy_type: 策略类型
            kline_data: K线数据
            params: 策略参数
            initial_capital: 初始资金
        """
        if not kline_data:
            return {
                "success": False,
                "message": "K线数据为空"
            }

        # 转换为DataFrame
        df = pd.DataFrame(kline_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.sort_values("timestamp").reset_index(drop=True)

        # 根据策略类型运行回测
        if strategy_type == "ma_cross":
            result = self._ma_cross_backtest(df, params, initial_capital)
        elif strategy_type == "grid":
            result = self._grid_backtest(df, params, initial_capital)
        elif strategy_type == "martingale":
            result = self._martingale_backtest(df, params, initial_capital)
        else:
            return {
                "success": False,
                "message": f"不支持的策略类型: {strategy_type}"
            }

        return result

    def _ma_cross_backtest(
        self,
        df: pd.DataFrame,
        params: Dict[str, Any],
        initial_capital: float
    ) -> Dict[str, Any]:
        """均线交叉策略回测"""
        fast_period = params.get("fast_period", 5)
        slow_period = params.get("slow_period", 20)

        # 计算均线
        df["ma_fast"] = df["close"].rolling(window=fast_period).mean()
        df["ma_slow"] = df["close"].rolling(window=slow_period).mean()

        # 生成信号
        df["signal"] = 0
        df.loc[df["ma_fast"] > df["ma_slow"], "signal"] = 1  # 金叉，买入
        df.loc[df["ma_fast"] < df["ma_slow"], "signal"] = -1  # 死叉，卖出

        # 回测
        capital = initial_capital
        position = 0.0
        trades = []
        equity_curve = []
        entry_price = 0.0

        for i, row in df.iterrows():
            if pd.isna(row["ma_fast"]) or pd.isna(row["ma_slow"]):
                equity_curve.append({
                    "timestamp": int(row["timestamp"].timestamp() * 1000),
                    "equity": capital,
                    "price": row["close"]
                })
                continue

            # 买入信号
            if row["signal"] == 1 and position == 0:
                position = capital / row["close"]
                entry_price = row["close"]
                capital = 0
                trades.append({
                    "timestamp": int(row["timestamp"].timestamp() * 1000),
                    "side": "buy",
                    "price": row["close"],
                    "quantity": position,
                    "amount": position * row["close"]
                })

            # 卖出信号
            elif row["signal"] == -1 and position > 0:
                capital = position * row["close"]
                pnl = (row["close"] - entry_price) * position
                trades.append({
                    "timestamp": int(row["timestamp"].timestamp() * 1000),
                    "side": "sell",
                    "price": row["close"],
                    "quantity": position,
                    "amount": capital,
                    "pnl": pnl,
                    "pnl_percent": (row["close"] - entry_price) / entry_price * 100
                })
                position = 0

            # 计算权益
            equity = capital + position * row["close"]
            equity_curve.append({
                "timestamp": int(row["timestamp"].timestamp() * 1000),
                "equity": equity,
                "price": row["close"]
            })

        # 最后平仓
        if position > 0:
            last_price = df.iloc[-1]["close"]
            capital = position * last_price
            pnl = (last_price - entry_price) * position
            trades.append({
                "timestamp": int(df.iloc[-1]["timestamp"].timestamp() * 1000),
                "side": "sell",
                "price": last_price,
                "quantity": position,
                "amount": capital,
                "pnl": pnl,
                "pnl_percent": (last_price - entry_price) / entry_price * 100
            })
            position = 0

        # 计算统计指标
        final_equity = capital if position == 0 else position * df.iloc[-1]["close"]
        total_return = final_equity - initial_capital
        total_return_percent = (final_equity - initial_capital) / initial_capital * 100

        # 计算最大回撤
        equity_values = [e["equity"] for e in equity_curve]
        peak = np.maximum.accumulate(equity_values)
        drawdown = (peak - equity_values) / peak * 100
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0

        # 计算胜率
        sell_trades = [t for t in trades if t["side"] == "sell"]
        winning_trades = [t for t in sell_trades if t.get("pnl", 0) > 0]
        losing_trades = [t for t in sell_trades if t.get("pnl", 0) <= 0]
        win_rate = len(winning_trades) / len(sell_trades) * 100 if len(sell_trades) > 0 else 0

        # 计算盈亏比
        total_profit = sum(t["pnl"] for t in winning_trades)
        total_loss = abs(sum(t["pnl"] for t in losing_trades))
        profit_factor = total_profit / total_loss if total_loss > 0 else float("inf")

        # 计算夏普比率（简化版）
        returns = np.diff(equity_values) / equity_values[:-1]
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 1 and np.std(returns) > 0 else 0

        return {
            "success": True,
            "total_return": total_return,
            "total_return_percent": total_return_percent,
            "max_drawdown": max_drawdown,
            "max_drawdown_percent": max_drawdown,
            "win_rate": win_rate,
            "total_trades": len(sell_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe_ratio,
            "equity_curve": equity_curve,
            "trades": trades
        }

    def _grid_backtest(
        self,
        df: pd.DataFrame,
        params: Dict[str, Any],
        initial_capital: float
    ) -> Dict[str, Any]:
        """网格交易策略回测"""
        grid_count = params.get("grid_count", 10)
        grid_spacing = params.get("grid_spacing", 0.01)  # 1%
        base_price = params.get("base_price", df.iloc[0]["close"])

        # 计算网格价格
        grid_prices = []
        for i in range(grid_count + 1):
            price = base_price * (1 - grid_spacing * grid_count / 2 + grid_spacing * i)
            grid_prices.append(price)

        # 简化版网格回测
        capital = initial_capital
        position = 0.0
        trades = []
        equity_curve = []
        grid_positions = {}  # 记录每个网格的持仓

        # 初始建仓（中间价位）
        mid_price = base_price
        initial_position_size = (capital * 0.5) / mid_price
        position = initial_position_size
        capital -= position * mid_price

        for i, row in df.iterrows():
            price = row["close"]

            # 检查网格触发（简化逻辑）
            for grid_price in grid_prices:
                grid_key = round(grid_price, 2)

                # 价格下跌到网格线，买入
                if price <= grid_price and grid_key not in grid_positions:
                    buy_amount = capital / (grid_count - len(grid_positions)) if grid_count > len(grid_positions) else capital * 0.1
                    if buy_amount > 10:  # 最小买入金额
                        buy_quantity = buy_amount / price
                        position += buy_quantity
                        capital -= buy_amount
                        grid_positions[grid_key] = buy_quantity
                        trades.append({
                            "timestamp": int(row["timestamp"].timestamp() * 1000),
                            "side": "buy",
                            "price": price,
                            "quantity": buy_quantity,
                            "amount": buy_amount,
                            "grid_level": grid_key
                        })

                # 价格上涨到网格线，卖出
                elif price >= grid_price * (1 + grid_spacing) and grid_key in grid_positions:
                    sell_quantity = grid_positions[grid_key]
                    sell_amount = sell_quantity * price
                    position -= sell_quantity
                    capital += sell_amount
                    pnl = (price - grid_price) * sell_quantity
                    trades.append({
                        "timestamp": int(row["timestamp"].timestamp() * 1000),
                        "side": "sell",
                        "price": price,
                        "quantity": sell_quantity,
                        "amount": sell_amount,
                        "pnl": pnl,
                        "pnl_percent": grid_spacing * 100,
                        "grid_level": grid_key
                    })
                    del grid_positions[grid_key]

            # 计算权益
            equity = capital + position * price
            equity_curve.append({
                "timestamp": int(row["timestamp"].timestamp() * 1000),
                "equity": equity,
                "price": price
            })

        # 计算统计指标
        final_equity = capital + position * df.iloc[-1]["close"]
        total_return = final_equity - initial_capital
        total_return_percent = (final_equity - initial_capital) / initial_capital * 100

        # 计算最大回撤
        equity_values = [e["equity"] for e in equity_curve]
        peak = np.maximum.accumulate(equity_values)
        drawdown = (peak - equity_values) / peak * 100
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0

        # 计算胜率
        sell_trades = [t for t in trades if t["side"] == "sell"]
        winning_trades = [t for t in sell_trades if t.get("pnl", 0) > 0]
        losing_trades = [t for t in sell_trades if t.get("pnl", 0) <= 0]
        win_rate = len(winning_trades) / len(sell_trades) * 100 if len(sell_trades) > 0 else 0

        # 计算盈亏比
        total_profit = sum(t.get("pnl", 0) for t in winning_trades)
        total_loss = abs(sum(t.get("pnl", 0) for t in losing_trades))
        profit_factor = total_profit / total_loss if total_loss > 0 else float("inf")

        # 计算夏普比率
        returns = np.diff(equity_values) / equity_values[:-1]
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 1 and np.std(returns) > 0 else 0

        return {
            "success": True,
            "total_return": total_return,
            "total_return_percent": total_return_percent,
            "max_drawdown": max_drawdown,
            "max_drawdown_percent": max_drawdown,
            "win_rate": win_rate,
            "total_trades": len(sell_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe_ratio,
            "equity_curve": equity_curve,
            "trades": trades
        }

    def _martingale_backtest(
        self,
        df: pd.DataFrame,
        params: Dict[str, Any],
        initial_capital: float
    ) -> Dict[str, Any]:
        """马丁格尔策略回测（高风险，仅供学习）"""
        base_order_size = params.get("base_order_size", 100)  # 基础订单金额
        multiplier = params.get("multiplier", 2.0)  # 加仓倍数
        max_levels = params.get("max_levels", 5)  # 最大加仓层数
        take_profit_percent = params.get("take_profit_percent", 0.01)  # 止盈百分比

        capital = initial_capital
        position = 0.0
        avg_price = 0.0
        current_level = 0
        trades = []
        equity_curve = []

        for i, row in df.iterrows():
            price = row["close"]

            # 初始建仓
            if position == 0 and current_level == 0:
                order_size = base_order_size
                if order_size <= capital:
                    quantity = order_size / price
                    position = quantity
                    avg_price = price
                    capital -= order_size
                    current_level = 1
                    trades.append({
                        "timestamp": int(row["timestamp"].timestamp() * 1000),
                        "side": "buy",
                        "price": price,
                        "quantity": quantity,
                        "amount": order_size,
                        "level": current_level
                    })

            # 加仓（价格下跌）
            elif position > 0 and current_level < max_levels:
                drawdown_percent = (avg_price - price) / avg_price
                # 每下跌一定比例加仓
                if drawdown_percent >= take_profit_percent * current_level:
                    order_size = base_order_size * (multiplier ** current_level)
                    if order_size <= capital:
                        quantity = order_size / price
                        total_cost = position * avg_price + order_size
                        position += quantity
                        avg_price = total_cost / position
                        capital -= order_size
                        current_level += 1
                        trades.append({
                            "timestamp": int(row["timestamp"].timestamp() * 1000),
                            "side": "buy",
                            "price": price,
                            "quantity": quantity,
                            "amount": order_size,
                            "level": current_level
                        })

            # 止盈
            elif position > 0:
                profit_percent = (price - avg_price) / avg_price
                if profit_percent >= take_profit_percent:
                    sell_amount = position * price
                    pnl = (price - avg_price) * position
                    capital += sell_amount
                    trades.append({
                        "timestamp": int(row["timestamp"].timestamp() * 1000),
                        "side": "sell",
                        "price": price,
                        "quantity": position,
                        "amount": sell_amount,
                        "pnl": pnl,
                        "pnl_percent": profit_percent * 100,
                        "level": current_level
                    })
                    position = 0
                    avg_price = 0
                    current_level = 0

            # 计算权益
            equity = capital + position * price
            equity_curve.append({
                "timestamp": int(row["timestamp"].timestamp() * 1000),
                "equity": equity,
                "price": price
            })

        # 计算统计指标
        final_equity = capital + position * df.iloc[-1]["close"]
        total_return = final_equity - initial_capital
        total_return_percent = (final_equity - initial_capital) / initial_capital * 100

        # 计算最大回撤
        equity_values = [e["equity"] for e in equity_curve]
        peak = np.maximum.accumulate(equity_values)
        drawdown = (peak - equity_values) / peak * 100
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0

        # 计算胜率
        sell_trades = [t for t in trades if t["side"] == "sell"]
        winning_trades = [t for t in sell_trades if t.get("pnl", 0) > 0]
        losing_trades = [t for t in sell_trades if t.get("pnl", 0) <= 0]
        win_rate = len(winning_trades) / len(sell_trades) * 100 if len(sell_trades) > 0 else 0

        # 计算盈亏比
        total_profit = sum(t.get("pnl", 0) for t in winning_trades)
        total_loss = abs(sum(t.get("pnl", 0) for t in losing_trades))
        profit_factor = total_profit / total_loss if total_loss > 0 else float("inf")

        # 计算夏普比率
        returns = np.diff(equity_values) / equity_values[:-1]
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 1 and np.std(returns) > 0 else 0

        return {
            "success": True,
            "total_return": total_return,
            "total_return_percent": total_return_percent,
            "max_drawdown": max_drawdown,
            "max_drawdown_percent": max_drawdown,
            "win_rate": win_rate,
            "total_trades": len(sell_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe_ratio,
            "equity_curve": equity_curve,
            "trades": trades,
            "warning": "马丁格尔策略风险极高，实际使用可能导致爆仓，仅供学习研究"
        }


# 创建默认实例
backtest_service = BacktestService()

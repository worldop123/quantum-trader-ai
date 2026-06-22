"""
实时数据推送服务
定期从OKX获取行情数据，通过WebSocket推送给订阅的客户端
"""
import asyncio
import time
from typing import Dict, Set
from app.websocket import manager
from app.services.okx_service import okx_service


class MarketDataService:
    """行情数据推送服务"""

    def __init__(self):
        # 订阅的交易对
        self.subscribed_symbols: Set[str] = set()
        # 最新行情数据缓存
        self.ticker_cache: Dict[str, dict] = {}
        # 最新深度数据缓存
        self.depth_cache: Dict[str, dict] = {}
        # K线数据缓存 {symbol: {timeframe: [klines]}}
        self.kline_cache: Dict[str, Dict[str, list]] = {}
        # 运行状态
        self.running = False
        # 推送间隔（秒）
        self.ticker_interval = 2  # 行情推送间隔
        self.depth_interval = 1   # 深度推送间隔
        self.kline_interval = 5   # K线推送间隔

    async def start(self):
        """启动行情推送服务"""
        if self.running:
            return

        self.running = True
        print("📡 行情数据推送服务已启动")

        # 启动各个推送任务
        asyncio.create_task(self._ticker_push_loop())
        asyncio.create_task(self._depth_push_loop())
        asyncio.create_task(self._kline_push_loop())

    async def stop(self):
        """停止行情推送服务"""
        self.running = False
        print("🛑 行情数据推送服务已停止")

    def _get_subscribed_symbols(self) -> Set[str]:
        """获取所有订阅的交易对"""
        symbols = set()
        for channel in manager.subscriptions.keys():
            if channel.startswith("ticker:"):
                symbol = channel.split(":", 1)[1]
                symbols.add(symbol)
            elif channel.startswith("depth:"):
                symbol = channel.split(":", 1)[1]
                symbols.add(symbol)
            elif channel.startswith("kline:"):
                parts = channel.split(":")
                if len(parts) >= 2:
                    symbols.add(parts[1])
        return symbols

    async def _ticker_push_loop(self):
        """行情推送循环"""
        while self.running:
            try:
                symbols = self._get_subscribed_symbols()

                for symbol in symbols:
                    try:
                        # 获取最新行情
                        result = await okx_service.get_ticker(symbol)

                        if result and result.get("code") == "0" and result.get("data"):
                            ticker_data = result["data"][0]

                            # 格式化数据
                            formatted = {
                                "symbol": symbol,
                                "last_price": float(ticker_data.get("last", 0)),
                                "open_24h": float(ticker_data.get("open24h", 0)),
                                "high_24h": float(ticker_data.get("high24h", 0)),
                                "low_24h": float(ticker_data.get("low24h", 0)),
                                "volume_24h": float(ticker_data.get("vol24h", 0)),
                                "turnover_24h": float(ticker_data.get("volCcy24h", 0)),
                                "price_change_percent": float(ticker_data.get("sodUtc8", 0)) * 100,
                                "timestamp": int(time.time() * 1000)
                            }

                            # 缓存数据
                            self.ticker_cache[symbol] = formatted

                            # 推送给订阅者
                            await manager.send_ticker_update(symbol, formatted)

                    except Exception as e:
                        print(f"⚠️  获取 {symbol} 行情失败: {e}")

                await asyncio.sleep(self.ticker_interval)

            except Exception as e:
                print(f"⚠️  行情推送循环出错: {e}")
                await asyncio.sleep(1)

    async def _depth_push_loop(self):
        """深度推送循环"""
        while self.running:
            try:
                symbols = set()
                for channel in manager.subscriptions.keys():
                    if channel.startswith("depth:"):
                        symbol = channel.split(":", 1)[1]
                        symbols.add(symbol)

                for symbol in symbols:
                    try:
                        # 获取最新深度
                        result = await okx_service.get_orderbook(symbol, sz=20)

                        if result and result.get("code") == "0" and result.get("data"):
                            depth_data = result["data"][0]

                            # 格式化数据
                            asks = [[float(price), float(size)] for price, size, _, _ in depth_data.get("asks", [])]
                            bids = [[float(price), float(size)] for price, size, _, _ in depth_data.get("bids", [])]

                            formatted = {
                                "symbol": symbol,
                                "asks": asks,
                                "bids": bids,
                                "timestamp": int(depth_data.get("ts", time.time() * 1000))
                            }

                            # 缓存数据
                            self.depth_cache[symbol] = formatted

                            # 推送给订阅者
                            await manager.send_depth_update(symbol, formatted)

                    except Exception as e:
                        print(f"⚠️  获取 {symbol} 深度失败: {e}")

                await asyncio.sleep(self.depth_interval)

            except Exception as e:
                print(f"⚠️  深度推送循环出错: {e}")
                await asyncio.sleep(1)

    async def _kline_push_loop(self):
        """K线推送循环"""
        while self.running:
            try:
                # 获取所有K线订阅
                kline_channels = [c for c in manager.subscriptions.keys() if c.startswith("kline:")]

                for channel in kline_channels:
                    try:
                        parts = channel.split(":")
                        if len(parts) < 3:
                            continue

                        symbol = parts[1]
                        timeframe = parts[2]

                        # 获取最新K线（只取最后一根）
                        result = await okx_service.get_candles(symbol, bar=timeframe, limit=2)

                        if result and result.get("code") == "0" and result.get("data"):
                            kline_raw = result["data"][0]  # 最新的一根

                            # 格式化数据
                            kline_data = {
                                "timestamp": int(kline_raw[0]),
                                "open": float(kline_raw[1]),
                                "high": float(kline_raw[2]),
                                "low": float(kline_raw[3]),
                                "close": float(kline_raw[4]),
                                "volume": float(kline_raw[5]),
                                "volume_ccy": float(kline_raw[6]) if len(kline_raw) > 6 else 0,
                            }

                            # 推送给订阅者
                            await manager.send_kline_update(symbol, timeframe, kline_data)

                    except Exception as e:
                        print(f"⚠️  获取 {channel} K线失败: {e}")

                await asyncio.sleep(self.kline_interval)

            except Exception as e:
                print(f"⚠️  K线推送循环出错: {e}")
                await asyncio.sleep(1)

    def get_cached_ticker(self, symbol: str) -> dict:
        """获取缓存的行情数据"""
        return self.ticker_cache.get(symbol, {})

    def get_cached_depth(self, symbol: str) -> dict:
        """获取缓存的深度数据"""
        return self.depth_cache.get(symbol, {})


# 创建全局实例
market_data_service = MarketDataService()

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set, Any
import json
import asyncio
import time


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 用户ID -> WebSocket连接列表
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # 订阅关系: channel -> set of (user_id, websocket)
        self.subscriptions: Dict[str, Set[tuple]] = {}
        # 心跳超时时间（秒）
        self.heartbeat_timeout = 60

    async def connect(self, websocket: WebSocket, user_id: int):
        """建立连接"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

        # 发送连接成功消息
        await self.send_to_connection(websocket, {
            "type": "connected",
            "data": {
                "message": "WebSocket连接成功",
                "user_id": user_id,
                "timestamp": int(time.time() * 1000)
            }
        })

    def disconnect(self, websocket: WebSocket, user_id: int):
        """断开连接"""
        # 从连接列表移除
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # 从所有订阅中移除
        for channel in list(self.subscriptions.keys()):
            self.subscriptions[channel].discard((user_id, websocket))
            if not self.subscriptions[channel]:
                del self.subscriptions[channel]

    async def send_to_connection(self, websocket: WebSocket, message: dict):
        """向单个连接发送消息"""
        try:
            await websocket.send_json(message)
            return True
        except:
            return False

    async def send_personal_message(self, message: dict, user_id: int):
        """发送个人消息"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await self.send_to_connection(connection, message)

    async def broadcast(self, message: dict):
        """广播消息"""
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                await self.send_to_connection(connection, message)

    def subscribe(self, channel: str, user_id: int, websocket: WebSocket):
        """订阅频道"""
        if channel not in self.subscriptions:
            self.subscriptions[channel] = set()
        self.subscriptions[channel].add((user_id, websocket))

    def unsubscribe(self, channel: str, user_id: int, websocket: WebSocket):
        """取消订阅"""
        if channel in self.subscriptions:
            self.subscriptions[channel].discard((user_id, websocket))
            if not self.subscriptions[channel]:
                del self.subscriptions[channel]

    def unsubscribe_all(self, user_id: int, websocket: WebSocket):
        """取消所有订阅"""
        for channel in list(self.subscriptions.keys()):
            self.subscriptions[channel].discard((user_id, websocket))
            if not self.subscriptions[channel]:
                del self.subscriptions[channel]

    async def publish(self, channel: str, data: Any, message_type: str = None):
        """向频道发布消息"""
        if channel not in self.subscriptions:
            return

        message = {
            "type": message_type or channel,
            "channel": channel,
            "data": data,
            "timestamp": int(time.time() * 1000)
        }

        for (user_id, websocket) in self.subscriptions.get(channel, set()):
            await self.send_to_connection(websocket, message)

    # ========== 特定类型消息 ==========

    async def send_ticker_update(self, symbol: str, ticker_data: dict):
        """发送行情更新"""
        await self.publish(f"ticker:{symbol}", ticker_data, "ticker")

    async def send_kline_update(self, symbol: str, timeframe: str, kline_data: dict):
        """发送K线更新"""
        await self.publish(f"kline:{symbol}:{timeframe}", kline_data, "kline")

    async def send_depth_update(self, symbol: str, depth_data: dict):
        """发送深度更新"""
        await self.publish(f"depth:{symbol}", depth_data, "depth")

    async def send_trade_update(self, symbol: str, trade_data: dict):
        """发送逐笔成交更新"""
        await self.publish(f"trade:{symbol}", trade_data, "trade")

    async def send_order_update(self, user_id: int, order_data: dict):
        """发送订单更新"""
        await self.send_personal_message({
            "type": "order_update",
            "data": order_data,
            "timestamp": int(time.time() * 1000)
        }, user_id)

    async def send_position_update(self, user_id: int, position_data: dict):
        """发送持仓更新"""
        await self.send_personal_message({
            "type": "position_update",
            "data": position_data,
            "timestamp": int(time.time() * 1000)
        }, user_id)

    async def send_balance_update(self, user_id: int, balance_data: dict):
        """发送余额更新"""
        await self.send_personal_message({
            "type": "balance_update",
            "data": balance_data,
            "timestamp": int(time.time() * 1000)
        }, user_id)

    async def send_notification(self, user_id: int, notification: dict):
        """发送通知"""
        await self.send_personal_message({
            "type": "notification",
            "data": notification,
            "timestamp": int(time.time() * 1000)
        }, user_id)

    async def send_risk_alert(self, user_id: int, alert_data: dict):
        """发送风控预警"""
        await self.send_personal_message({
            "type": "risk_alert",
            "data": alert_data,
            "timestamp": int(time.time() * 1000)
        }, user_id)

    def get_connection_count(self) -> int:
        """获取总连接数"""
        count = 0
        for connections in self.active_connections.values():
            count += len(connections)
        return count

    def get_user_count(self) -> int:
        """获取在线用户数"""
        return len(self.active_connections)

    def get_subscription_count(self) -> int:
        """获取总订阅数"""
        count = 0
        for subs in self.subscriptions.values():
            count += len(subs)
        return count


# 创建全局管理器实例
manager = ConnectionManager()

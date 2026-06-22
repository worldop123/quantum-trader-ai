import hmac
import base64
import hashlib
import time
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.config import settings


class OKXService:
    """OKX交易所服务类"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        passphrase: Optional[str] = None,
        is_demo: bool = True
    ):
        self.api_key = api_key or settings.OKX_API_KEY
        self.api_secret = api_secret or settings.OKX_API_SECRET
        self.passphrase = passphrase or settings.OKX_PASSPHRASE
        self.is_demo = is_demo

        if self.is_demo:
            self.base_url = "https://www.okx.com"
        else:
            self.base_url = "https://www.okx.com"

    def _get_timestamp(self) -> str:
        """获取ISO格式时间戳"""
        return datetime.utcnow().isoformat(timespec="seconds") + "Z"

    def _sign(self, timestamp: str, method: str, request_path: str, body: str = "") -> str:
        """生成签名"""
        if not self.api_secret:
            return ""

        message = timestamp + method.upper() + request_path + body
        mac = hmac.new(
            bytes(self.api_secret, encoding="utf8"),
            bytes(message, encoding="utf-8"),
            digestmod=hashlib.sha256
        )
        d = mac.digest()
        return base64.b64encode(d).decode()

    def _get_headers(self, method: str, request_path: str, body: str = "") -> Dict[str, str]:
        """获取请求头"""
        timestamp = self._get_timestamp()
        sign = self._sign(timestamp, method, request_path, body)

        headers = {
            "OK-ACCESS-KEY": self.api_key or "",
            "OK-ACCESS-SIGN": sign,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase or "",
            "Content-Type": "application/json",
        }

        if self.is_demo:
            headers["x-simulated-trading"] = "1"

        return headers

    async def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, body: Optional[Dict] = None) -> Dict[str, Any]:
        """发送请求"""
        url = self.base_url + endpoint

        # 构建请求路径（用于签名）
        request_path = endpoint
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            request_path = f"{endpoint}?{query_string}"

        body_str = ""
        if body:
            import json
            body_str = json.dumps(body)

        headers = self._get_headers(method, request_path, body_str)

        async with httpx.AsyncClient(timeout=30.0) as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=body)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")

            return response.json()

    # ========== 账户相关 ==========

    async def get_balance(self) -> Dict[str, Any]:
        """获取账户余额"""
        endpoint = "/api/v5/account/balance"
        result = await self._request("GET", endpoint)
        return result

    async def get_positions(self, inst_type: str = "SPOT") -> Dict[str, Any]:
        """获取持仓"""
        endpoint = "/api/v5/account/positions"
        params = {"instType": inst_type}
        result = await self._request("GET", endpoint, params=params)
        return result

    # ========== 交易相关 ==========

    async def place_order(
        self,
        inst_id: str,
        side: str,
        ord_type: str,
        sz: float,
        px: Optional[float] = None
    ) -> Dict[str, Any]:
        """下单

        Args:
            inst_id: 交易对，如 BTC-USDT
            side: buy/sell
            ord_type: limit/market
            sz: 数量
            px: 价格（限价单需要）
        """
        endpoint = "/api/v5/trade/order"

        body = {
            "instId": inst_id,
            "tdMode": "cash",
            "side": side,
            "ordType": ord_type,
            "sz": str(sz),
        }

        if px and ord_type == "limit":
            body["px"] = str(px)

        result = await self._request("POST", endpoint, body=body)
        return result

    async def cancel_order(self, inst_id: str, ord_id: str) -> Dict[str, Any]:
        """撤单"""
        endpoint = "/api/v5/trade/cancel-order"
        body = {
            "instId": inst_id,
            "ordId": ord_id,
        }
        result = await self._request("POST", endpoint, body=body)
        return result

    async def get_order(self, inst_id: str, ord_id: str) -> Dict[str, Any]:
        """查询订单"""
        endpoint = "/api/v5/trade/order"
        params = {
            "instId": inst_id,
            "ordId": ord_id,
        }
        result = await self._request("GET", endpoint, params=params)
        return result

    async def get_order_history(
        self,
        inst_type: str = "SPOT",
        state: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """获取历史订单"""
        endpoint = "/api/v5/trade/orders-history"
        params = {
            "instType": inst_type,
            "limit": str(limit),
        }
        if state:
            params["state"] = state
        result = await self._request("GET", endpoint, params=params)
        return result

    async def get_trade_history(
        self,
        inst_type: str = "SPOT",
        limit: int = 100
    ) -> Dict[str, Any]:
        """获取成交记录"""
        endpoint = "/api/v5/trade/fills"
        params = {
            "instType": inst_type,
            "limit": str(limit),
        }
        result = await self._request("GET", endpoint, params=params)
        return result

    # ========== 行情相关 ==========

    async def get_ticker(self, inst_id: str) -> Dict[str, Any]:
        """获取行情"""
        endpoint = "/api/v5/market/ticker"
        params = {"instId": inst_id}
        result = await self._request("GET", endpoint, params=params)
        return result

    async def get_tickers(self, inst_type: str = "SPOT") -> Dict[str, Any]:
        """获取所有行情"""
        endpoint = "/api/v5/market/tickers"
        params = {"instType": inst_type}
        result = await self._request("GET", endpoint, params=params)
        return result

    async def get_candles(
        self,
        inst_id: str,
        bar: str = "1H",
        limit: int = 100,
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取K线数据

        Args:
            inst_id: 交易对
            bar: 时间周期 1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/1W/1M
            limit: 数量
        """
        endpoint = "/api/v5/market/candles"
        params = {
            "instId": inst_id,
            "bar": bar,
            "limit": str(limit),
        }
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        result = await self._request("GET", endpoint, params=params)
        return result

    async def get_orderbook(self, inst_id: str, sz: int = 20) -> Dict[str, Any]:
        """获取深度数据"""
        endpoint = "/api/v5/market/books"
        params = {
            "instId": inst_id,
            "sz": str(sz),
        }
        result = await self._request("GET", endpoint, params=params)
        return result

    # ========== 公共数据 ==========

    async def get_instruments(self, inst_type: str = "SPOT") -> Dict[str, Any]:
        """获取交易对列表"""
        endpoint = "/api/v5/public/instruments"
        params = {"instType": inst_type}
        result = await self._request("GET", endpoint, params=params)
        return result

    async def verify_api_key(self) -> Dict[str, Any]:
        """验证API密钥是否有效"""
        try:
            result = await self.get_balance()
            if result.get("code") == "0":
                return {"success": True, "message": "API密钥验证成功", "data": result}
            else:
                return {"success": False, "message": result.get("msg", "验证失败"), "data": result}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}


# 创建默认实例
okx_service = OKXService()

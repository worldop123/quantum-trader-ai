import httpx
from typing import Optional, Dict, Any

from app.config import settings


class NotificationService:
    """通知服务类 - PushPlus"""

    def __init__(self):
        self.token = settings.PUSHPLUS_TOKEN
        self.base_url = settings.PUSHPLUS_URL

    async def send_pushplus(
        self,
        title: str,
        content: str,
        template: str = "html",
        custom_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送PushPlus通知

        Args:
            title: 消息标题
            content: 消息内容
            template: 模板类型 html/txt/json/markdown
            custom_token: 用户自定义token（优先使用）
        """
        token = custom_token or self.token

        if not token:
            return {
                "success": False,
                "message": "PushPlus Token未配置"
            }

        body = {
            "token": token,
            "title": title,
            "content": content,
            "template": template,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.base_url, json=body)
                result = response.json()

                if result.get("code") == 200:
                    return {
                        "success": True,
                        "message": "发送成功",
                        "data": result
                    }
                else:
                    return {
                        "success": False,
                        "message": result.get("msg", "发送失败"),
                        "data": result
                    }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

    async def send_order_notification(
        self,
        symbol: str,
        side: str,
        order_type: str,
        price: float,
        quantity: float,
        status: str,
        custom_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送订单通知"""
        side_text = "买入" if side == "buy" else "卖出"
        type_text = "限价单" if order_type == "limit" else "市价单"
        status_text = {
            "filled": "已成交",
            "partially_filled": "部分成交",
            "canceled": "已撤销",
            "rejected": "已拒绝",
            "pending": "挂单中",
        }.get(status, status)

        title = f"【QuantumTrader】订单{status_text}通知"

        content = f"""
<div style="padding: 20px; font-family: Arial, sans-serif;">
    <h2 style="color: #00ff88; margin-bottom: 20px;">📊 订单状态更新</h2>

    <div style="background: #1a1a2e; padding: 20px; border-radius: 10px; color: #fff;">
        <p><strong>交易对：</strong>{symbol}</p>
        <p><strong>方向：</strong><span style="color: {'#00ff88' if side == 'buy' else '#ff4757'};">{side_text}</span></p>
        <p><strong>类型：</strong>{type_text}</p>
        <p><strong>价格：</strong>{price}</p>
        <p><strong>数量：</strong>{quantity}</p>
        <p><strong>状态：</strong>{status_text}</p>
    </div>

    <p style="margin-top: 20px; color: #888; font-size: 12px;">
        此消息由 QuantumTrader AI量化交易系统自动发送
    </p>
</div>
"""

        return await self.send_pushplus(title, content, "html", custom_token)

    async def send_risk_alert(
        self,
        alert_type: str,
        message: str,
        level: str = "warning",
        custom_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送风险预警"""
        level_emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "danger": "🚨",
            "success": "✅",
        }.get(level, "⚠️")

        level_color = {
            "info": "#3498db",
            "warning": "#f39c12",
            "danger": "#ff4757",
            "success": "#00ff88",
        }.get(level, "#f39c12")

        title = f"【QuantumTrader】{level_emoji} 风险预警"

        content = f"""
<div style="padding: 20px; font-family: Arial, sans-serif;">
    <h2 style="color: {level_color}; margin-bottom: 20px;">{level_emoji} 风险预警</h2>

    <div style="background: #1a1a2e; padding: 20px; border-radius: 10px; color: #fff;">
        <p><strong>预警类型：</strong>{alert_type}</p>
        <p><strong>预警内容：</strong>{message}</p>
        <p><strong>风险等级：</strong><span style="color: {level_color};">{level.upper()}</span></p>
    </div>

    <p style="margin-top: 20px; color: #888; font-size: 12px;">
        请及时关注并采取相应措施。此消息由 QuantumTrader 自动发送。
    </p>
</div>
"""

        return await self.send_pushplus(title, content, "html", custom_token)

    async def send_strategy_notification(
        self,
        strategy_name: str,
        action: str,
        message: str,
        custom_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送策略通知"""
        title = f"【QuantumTrader】策略{action}通知"

        content = f"""
<div style="padding: 20px; font-family: Arial, sans-serif;">
    <h2 style="color: #00d4ff; margin-bottom: 20px;">🤖 策略状态更新</h2>

    <div style="background: #1a1a2e; padding: 20px; border-radius: 10px; color: #fff;">
        <p><strong>策略名称：</strong>{strategy_name}</p>
        <p><strong>操作：</strong>{action}</p>
        <p><strong>详情：</strong>{message}</p>
    </div>

    <p style="margin-top: 20px; color: #888; font-size: 12px;">
        此消息由 QuantumTrader AI量化交易系统自动发送
    </p>
</div>
"""

        return await self.send_pushplus(title, content, "html", custom_token)


# 创建默认实例
notification_service = NotificationService()

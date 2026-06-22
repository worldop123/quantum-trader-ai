import httpx
from typing import Optional, List, Dict, Any

from app.config import settings


class AIService:
    """AI服务类 - DeepSeek API"""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_API_URL
        self.model = "deepseek-chat"

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """聊天补全"""
        if not self.api_key:
            return {
                "success": False,
                "message": "DeepSeek API Key未配置",
                "content": None
            }

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=body)
                result = response.json()

                if "choices" in result and len(result["choices"]) > 0:
                    return {
                        "success": True,
                        "message": "success",
                        "content": result["choices"][0]["message"]["content"]
                    }
                else:
                    return {
                        "success": False,
                        "message": result.get("error", {}).get("message", "API调用失败"),
                        "content": None
                    }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "content": None
            }

    async def analyze_market(
        self,
        symbol: str,
        kline_data: List[Dict[str, Any]],
        timeframe: str = "1h"
    ) -> Dict[str, Any]:
        """行情分析"""
        # 准备分析数据
        recent_closes = [k["close"] for k in kline_data[-20:]] if kline_data else []
        current_price = recent_closes[-1] if recent_closes else 0
        price_change = (recent_closes[-1] - recent_closes[0]) / recent_closes[0] * 100 if len(recent_closes) > 1 else 0

        system_prompt = """你是一位专业的加密货币交易分析师，擅长技术分析和市场研判。
请基于提供的K线数据进行客观分析，给出专业的分析报告。

分析要求：
1. 趋势判断（短期/中期）
2. 关键支撑位和阻力位
3. 技术指标分析（MA、MACD、RSI等）
4. 交易建议（谨慎参考，不构成投资建议）
5. 风险提示

请用中文回复，结构清晰，专业但易懂。"""

        user_prompt = f"""请分析 {symbol} 的行情：

时间周期：{timeframe}
当前价格：{current_price}
近20周期涨跌幅：{price_change:.2f}%

最近收盘价：
{recent_closes}

请给出详细的技术分析报告。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        result = await self.chat_completion(messages, temperature=0.5, max_tokens=3000)
        return result

    async def explain_strategy(
        self,
        strategy_type: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """策略解释"""
        strategy_names = {
            "ma_cross": "均线交叉策略",
            "grid": "网格交易策略",
            "martingale": "马丁格尔策略",
            "mean_reversion": "均值回归策略",
            "breakout": "突破策略",
        }

        strategy_name = strategy_names.get(strategy_type, strategy_type)

        system_prompt = """你是一位专业的量化交易策略专家，擅长解释各种交易策略的原理和风险。

请用通俗易懂的语言解释策略原理，包括：
1. 策略基本原理
2. 适用市场环境
3. 风险点和注意事项
4. 参数说明
5. 优化建议

请用中文回复，结构清晰。"""

        user_prompt = f"""请解释 {strategy_name}：

策略参数：
{params}

请详细解释这个策略的工作原理、优缺点和风险。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        result = await self.chat_completion(messages, temperature=0.7, max_tokens=2500)
        return result

    async def generate_trade_signal(
        self,
        symbol: str,
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成交易信号（仅供参考）"""
        system_prompt = """你是一位谨慎的交易信号生成助手。
请基于市场数据给出参考性的交易信号分析，必须强调风险提示，不构成任何投资建议。"""

        user_prompt = f"""请基于以下数据分析 {symbol} 的交易信号：

{market_data}

请给出：
1. 当前市场状态判断
2. 可能的交易方向（仅供参考）
3. 入场点位建议（仅供参考）
4. 止损止盈建议（仅供参考）
5. 风险等级评估

重要提示：以上分析仅供学习参考，不构成投资建议。加密货币交易风险极高，请谨慎决策。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        result = await self.chat_completion(messages, temperature=0.5, max_tokens=2000)
        return result


# 创建默认实例
ai_service = AIService()

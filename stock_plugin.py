import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

class StockPlugin:
    """AstrBot 股票行情查询插件"""
    
    def __init__(self):
        self.name = "股票行情"
        self.description = "提供实时股票行情和市场信息"
        self.version = "1.0.0"
        self.author = "小羽"
        self.api_key = "your_alpha_vantage_api_key"  # 需要配置API密钥
        self.base_url = "https://www.alphavantage.co/query"
        
    async def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """获取股票实时行情"""
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol.upper(),
                "apikey": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self.format_stock_data(data, symbol)
                    else:
                        return {"error": f"无法获取{symbol}的股票信息"}
        except Exception as e:
            return {"error": f"获取股票信息时出错: {str(e)}"}
    
    async def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票详细信息"""
        try:
            params = {
                "function": "OVERVIEW",
                "symbol": symbol.upper(),
                "apikey": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        return {}
        except Exception as e:
            return {}
    
    def format_stock_data(self, data: Dict, symbol: str) -> Dict[str, Any]:
        """格式化股票数据"""
        quote = data.get("Global Quote", {})
        
        if not quote:
            return {"error": f"未找到股票 {symbol} 的信息"}
        
        try:
            current_price = float(quote.get("05. price", 0))
            previous_close = float(quote.get("08. previous close", 0))
            change = float(quote.get("09. change", 0))
            change_percent = quote.get("10. change percent", "0%").rstrip("%")
            
            stock_info = {
                "symbol": quote.get("01. symbol", symbol),
                "price": current_price,
                "change": change,
                "change_percent": float(change_percent),
                "previous_close": previous_close,
                "open": float(quote.get("02. open", 0)),
                "high": float(quote.get("03. high", 0)),
                "low": float(quote.get("04. low", 0)),
                "volume": int(quote.get("06. volume", 0)),
                "latest_trading_day": quote.get("07. latest trading day", ""),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return stock_info
        except (ValueError, KeyError) as e:
            return {"error": f"解析股票数据时出错: {str(e)}"}
    
    def get_stock_message(self, stock_data: Dict[str, Any]) -> str:
        """生成股票信息消息"""
        if "error" in stock_data:
            return f"❌ {stock_data['error']}"
        
        # 确定涨跌颜色和表情
        change_emoji = "📈" if stock_data["change"] > 0 else "📉" if stock_data["change"] < 0 else "➡️"
        change_color = "🔴" if stock_data["change"] > 0 else "🟢" if stock_data["change"] < 0 else "⚪"
        
        message = f"""{change_emoji} {stock_data['symbol']} 股票行情
        
💰 当前价格: ${stock_data['price']:.2f}
{change_color} 涨跌: {stock_data['change']:+.2f} ({stock_data['change_percent']:+.2f}%)
📊 今开: ${stock_data['open']:.2f}
🔺 最高: ${stock_data['high']:.2f}
🔻 最低: ${stock_data['low']:.2f}
📉 昨收: ${stock_data['previous_close']:.2f}
👥 成交量: {stock_data['volume']:,}
📅 交易日: {stock_data['latest_trading_day']}
🕒 更新时间: {stock_data['timestamp']}"""
        
        return message
    
    async def get_market_summary(self) -> str:
        """获取市场摘要"""
        major_indices = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
        summary = "📊 主要股票行情摘要：\n\n"
        
        for symbol in major_indices:
            stock_data = await self.get_stock_quote(symbol)
            if "error" not in stock_data:
                change_emoji = "📈" if stock_data["change"] > 0 else "📉" if stock_data["change"] < 0 else "➡️"
                summary += f"{change_emoji} {symbol}: ${stock_data['price']:.2f} ({stock_data['change_percent']:+.2f}%)\n"
            else:
                summary += f"❌ {symbol}: 获取失败\n"
        
        return summary
    
    async def execute(self, command: str, params: list) -> str:
        """执行插件命令"""
        if command == "股票" or command == "stock":
            if not params:
                return await self.get_market_summary()
            
            symbol = params[0]
            stock_data = await self.get_stock_quote(symbol)
            return self.get_stock_message(stock_data)
        
        elif command == "市场" or command == "market":
            return await self.get_market_summary()
        
        return "未知命令，使用：股票 [代码] 或 市场"

# AstrBot 插件注册
class AstrBotStockPlugin:
    def __init__(self):
        self.plugin = StockPlugin()
        
    async def handle_message(self, message: str, platform: str, user_id: str) -> Optional[str]:
        """处理消息"""
        if message.startswith("股票 ") or message.startswith("/股票 "):
            symbol = message.split(" ", 1)[1].strip()
            if symbol:
                stock_data = await self.plugin.get_stock_quote(symbol)
                return self.plugin.get_stock_message(stock_data)
        
        elif message == "市场" or message == "/市场":
            return await self.plugin.get_market_summary()
        
        return None
    
    def get_help(self) -> str:
        """获取帮助信息"""
        return """📈 股票行情插件帮助：
        
使用方法：
• 股票 [股票代码] - 查询指定股票行情
• 市场 - 查看主要股票行情摘要
• /股票 [股票代码] - 同上
• /市场 - 同上
        
示例：
• 股票 AAPL
• 股票 TSLA
• 市场"""

# 导出插件实例
stock_plugin_instance = AstrBotStockPlugin()
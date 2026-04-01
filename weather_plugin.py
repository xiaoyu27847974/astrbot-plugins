import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime
import json

class WeatherPlugin:
    """AstrBot 天气预报插件"""
    
    def __init__(self):
        self.name = "天气预报"
        self.description = "提供实时天气信息和预报"
        self.version = "1.0.0"
        self.author = "小羽"
        self.api_key = "your_weather_api_key"  # 需要配置天气API密钥
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    async def get_weather(self, city: str) -> Dict[str, Any]:
        """获取指定城市的天气信息"""
        try:
            # 获取城市坐标
            geo_url = f"{self.base_url}/weather?q={city}&appid={self.api_key}&lang=zh_cn&units=metric"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(geo_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self.format_weather_data(data)
                    else:
                        return {"error": f"无法获取{city}的天气信息"}
        except Exception as e:
            return {"error": f"获取天气信息时出错: {str(e)}"}
    
    def format_weather_data(self, data: Dict) -> Dict[str, Any]:
        """格式化天气数据"""
        weather_info = {
            "city": data.get("name", ""),
            "country": data.get("sys", {}).get("country", ""),
            "temperature": data.get("main", {}).get("temp", 0),
            "feels_like": data.get("main", {}).get("feels_like", 0),
            "humidity": data.get("main", {}).get("humidity", 0),
            "pressure": data.get("main", {}).get("pressure", 0),
            "description": data.get("weather", [{}])[0].get("description", ""),
            "wind_speed": data.get("wind", {}).get("speed", 0),
            "visibility": data.get("visibility", 0),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return weather_info
    
    def get_weather_message(self, weather_data: Dict[str, Any]) -> str:
        """生成天气信息消息"""
        if "error" in weather_data:
            return f"❌ {weather_data['error']}"
        
        message = f"""🌤️ {weather_data['city']}, {weather_data['country']} 天气信息
        
🌡️ 温度: {weather_data['temperature']}°C (体感: {weather_data['feels_like']}°C)
💧 湿度: {weather_data['humidity']}%
📊 气压: {weather_data['pressure']} hPa
🌪️ 风速: {weather_data['wind_speed']} m/s
👁️ 能见度: {weather_data['visibility']} m
📝 天气: {weather_data['description']}
🕒 更新时间: {weather_data['timestamp']}"""
        
        return message
    
    async def execute(self, command: str, params: list) -> str:
        """执行插件命令"""
        if command == "天气" or command == "weather":
            if not params:
                return "请提供城市名称，例如：天气 北京"
            
            city = params[0]
            weather_data = await self.get_weather(city)
            return self.get_weather_message(weather_data)
        
        return "未知命令，使用：天气 [城市名]"

# AstrBot 插件注册
class AstrBotPlugin:
    def __init__(self):
        self.plugin = WeatherPlugin()
        
    async def handle_message(self, message: str, platform: str, user_id: str) -> Optional[str]:
        """处理消息"""
        if message.startswith("天气 ") or message.startswith("/天气 "):
            city = message.split(" ", 1)[1].strip()
            if city:
                weather_data = await self.plugin.get_weather(city)
                return self.plugin.get_weather_message(weather_data)
        
        return None
    
    def get_help(self) -> str:
        """获取帮助信息"""
        return """🌤️ 天气预报插件帮助：
        
使用方法：
• 天气 [城市名] - 查询指定城市天气
• /天气 [城市名] - 同上
        
示例：
• 天气 北京
• 天气 上海
• 天气 广州"""

# 导出插件实例
plugin_instance = AstrBotPlugin()
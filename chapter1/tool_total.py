from tool_search import get_attraction
from tool_weather import get_weather

# 将所有工具放入一个字典，方便后续调用
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
}

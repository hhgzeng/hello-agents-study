import os

from dotenv import load_dotenv
from tavily import TavilyClient


def get_attraction(city: str, weather: str) -> str:
    """
    根据城市和天气，使用 Tavily Search API 搜索并返回优化后的景点推荐。
    """
    # 1. 从 .env 中获取 API Key
    load_dotenv()
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "错误：未配置 TAVILY_API_KEY 环境变量"

    # 2. 初始化 Tavily 客户端
    tavily = TavilyClient(api_key=api_key)

    # 3. 构造一个精确的查询
    query = f"'{city}'在'{weather}'天气下最值得去的旅游景点推荐及理由"

    try:
        # 4. 调用 API，include_answer=True 会返回一个综合性的回答
        response = tavily.search(query=query, search_depth="basic", include_answer=True)

        # 5. Tavily 返回的结果已经非常干净，可以直接使用
        # response["answer"] 是一个基于所有搜索结果的总结性回答
        if response.get("answer"):
            return response["answer"]

        # 如果没有综合性回答，则格式化原始结果
        formatted_results = []
        for result in response.get("results", []):
            formatted_results.append(f"- {result['title']}: {result['content']}")

        if not formatted_results:
            return "抱歉，没有找到相关的旅游景点推荐。"

        return "根据搜索结果，为您找到以下信息:\n" + "\n".join(formatted_results)

    except Exception as e:
        return f"错误：执行 Tavily 搜索时出现问题 - {e}"

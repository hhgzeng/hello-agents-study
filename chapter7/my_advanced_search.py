import os

from hello_agents import ToolRegistry


class MyAdvanacedSearchTool:
    """
    自定义高级搜索工具类
    展示多源整合和智能选择的设计模式
    """

    def __init__(self):
        self.name = "my_advanced_search"
        self.description = "智能搜索工具，支持多个搜索源，自动选择最佳结果"
        self.search_sources = []
        self._setup_search_sources()

    def _setup_search_sources(self):
        """set avaiable search source"""
        # check Tavily available
        if os.getenv("TAVILY_API_KEY"):
            try:
                from tavily import TavilyClient

                self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
                self.search_sources.append("tavily")
                print("✅ Tavily 搜索源已启用")
            except ImportError:
                print("⚠️ Tavily 库未安装")

        # check SerpApi available
        if os.getenv("SERPAPI_API_KEY"):
            try:
                import serpapi

                self.search_sources.append("serpapi")
                print("✅ SerpApi 搜索源已启用")
            except ImportError:
                print("⚠️ SerpApi 库未安装")

        if self.search_sources:
            print(f"🔧 可用搜索源: {', '.join(self.search_sources)}")
        else:
            print("⚠️ 没有可用的搜索源，请配置 API 密钥")

    def search(self, query: str) -> str:
        """execute intelligent search"""
        if not query.strip():
            return "❌ 错误：搜索查询不能为空"

        # check there is available search source
        if not self.search_sources:
            return """❌ 没有可用的搜索源，请配置以下API密钥之一：

1. Tavily API: 设置环境变量 TAVILY_API_KEY
   获取地址: https://tavily.com/

2. SerpAPI: 设置环境变量 SERPAPI_API_KEY
   获取地址: https://serpapi.com/

配置后重新运行程序。"""

        print(f"🔍 开始智能搜索: {query}")

        # try multi search sources, return the best result
        for source in self.search_sources:
            try:
                if source == "tavily":
                    result = self._search_with_tavily(query)
                    if result and "未找到" not in result:
                        return f"📊 Tavily AI 搜索结果：\n\n{result}"

                elif source == "serpapi":
                    result = self._search_with_serpapi(query)
                    if result and "未找到" not in result:
                        return f"🌐 SerpApi Google搜索结果：\n\n{result}"

            except Exception as e:
                print(f"⚠️ {source} 搜索失败: {e}")
                continue

    def _search_with_tavily(self, query: str) -> str:
        """use Tavily search"""
        response = self.tavily_client.search(query=query, max_results=3)
        # print("search with taivly:")

        if response.get("answer"):
            result = f"💡 AI直接答案：{response['answer']}\n\n"
        else:
            result = ""

        # print("no direct answer")
        result += "🔗 相关结果：\n"
        for i, item in enumerate(response.get("results", [])[:3], 1):
            # print(i, item)
            result += f"[{i}] {item.get('title', '')}\n"
            result += f"    {item.get('content', '')[:150]}...\n\n"

        return result

    def _search_with_serpapi(self, query: str) -> str:
        """use SerpApi search"""
        import serpapi

        search = serpapi.GoogleSearch(
            {"q": query, "api_key": os.getenv("SERPAPI_API_KEY"), "num": 3}
        )

        results = search.get_dict()

        result = "🔗 Google 搜索结果：\n"
        if "organic_results" in results:
            for i, res in enumerate(result["organic_results"][:3], 1):
                result += f"[{i}] {res.get('title', '')}\n"
                result += f"    {res.get('snippet', '')}\n\n"

        return result


def create_advanced_search_registry():
    """创建包含高级搜索工具的注册表"""
    registry = ToolRegistry()

    # create search tool instance
    search_tool = MyAdvanacedSearchTool()

    # register search tool
    registry.register_function(
        name="advanced_search",
        description="高级搜索工具，整合Tavily和SerpAPI多个搜索源，提供更全面的搜索结果",
        func=search_tool.search,
    )

    return registry

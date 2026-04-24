"""
NoteTool 与 ContextBuilder 集成示例

展示如何将 NoteTool 与 ContextBuilder 集成，实现：
1. 长期项目追踪
2. 笔记检索与上下文注入
3. 基于历史笔记的连贯建议
"""

from dotenv import load_dotenv
load_dotenv()

from hello_agents import SimpleAgent, HelloAgentsLLM

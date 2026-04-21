from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM, SimpleAgent, ToolRegistry
from hello_agents.tools import MemoryTool, RAGTool

load_dotenv()

# create LLM instance
llm = HelloAgentsLLM()

# create agent
agent = SimpleAgent(
    name="智能助手", llm=llm, system_prompt="你是一个有记忆和知识检索能力的 AI 助手"
)

# create tool registry
tool_registry = ToolRegistry()

# add memory tool
memory_tool = MemoryTool(user_id="user123")
tool_registry.register_tool(memory_tool)

# add RAG tool
rag_tool = RAGTool(knowledge_base_path="./knowledge_base")
tool_registry.register_tool(rag_tool)

# cofigurate tool for agent
agent.tool_registry = tool_registry

# begin conversation
response = agent.run("你好！请记住我叫张三，我是一名 Python 开发者")
print(response)

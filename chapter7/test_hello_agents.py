from hello_agents import SimpleAgent, HelloAgentsLLM
from dotenv import load_dotenv

# load environment
load_dotenv()

# create LLM instance - framework automatic detect provider
llm = HelloAgentsLLM()

# or manually specify provider (ptional)
# llm = HelloAgentsLLM(provider="modelscope")

# create SimpleAgebt
agent = SimpleAgent(
    name="AI 助手",
    llm=llm,
    system_prompt="你是一个乐于助人的 AI 助手"
)

# basic conversation
response = agent.run("你好！请介绍一下自己")
print(response)

# add tool function (optional)
from hello_agents.tools import CalculatorTool
calculator = CalculatorTool
# 需要实现7.4.1的MySimpleAgent进行调用，后续章节会支持此类调用方式
# agent.add_tool(calculator)

# now we can use tool
response = agent.run("请帮我计算 2 + 3 * 4")
print(response)

# view conversation history
print(f"历史消息数: {len(agent.get_history())}")

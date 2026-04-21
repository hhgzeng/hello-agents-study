from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM
from my_reflection_agent import MyReflectionAgent

load_dotenv()
llm = HelloAgentsLLM()

general_agent = MyReflectionAgent(name="我的反思助手", llm=llm)

# code agent (simliar to chapter 4)
code_prompts = {
    "initial": "You are a Python expert, please write funciton: {task}",
    "reflect": "Please review algorithm efficiency of the code: \ntask: {task}\ncode: {content}",
    "refine": "Please optimize the code based on the feedback:\ntask: {task}\nfeedback: {feedback}"
}
code_agent = MyReflectionAgent(
    name="My code assistant",
    llm=llm,
    custom_prompt=code_prompts
)

# test usage
result = general_agent.run("写一篇关于人工智能发展历程的简短文章")
print(f"最终结果: {result}")

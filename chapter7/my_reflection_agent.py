DEFAULT_PROMPTS = {
    "initial": """ 请根据以下要求完成任务:

任务:
{task}

请提供一个完整、准确的回答。 """,
    "reflect": """ 请仔细审查以下回答，并找出可能的问题或改进空间:

# 原始任务:
{task}

# 当前回答:
{content}

请分析这个回答的质量，指出不足之处，并提出具体的改进建议。
如果回答已经很好，请回答"无需改进"。""",
    "refine": """请根据反馈意见改进你的回答:

# 原始任务:
{task}

# 上一轮回答:
{last_content} 

# 反馈意见:
{feedback}

请提供一个改进后的回答。 """,
}

from typing import Any, Dict, List, Optional

from hello_agents import HelloAgentsLLM, ReflectionAgent, Config


class Memory:
    """
    一个简单的短期记忆模块，用于存储智能体的行动与反思轨迹。
    """

    def __init__(self):
        self.records: List[Dict[str, Any]] = []

    def add_record(self, record_type: str, content: str):
        self.records.append({"type": record_type, "content": content})
        print(f"📝 记忆已更新，新增一条 '{record_type}' 记录。")

    def get_trajectory(self) -> str:
        trajectory = ""
        for record in self.records:
            if record["type"] == "execution":
                trajectory += f"--- 上一轮尝试 ---\n{record["content"]}\n\n"
            elif record["type"] == "reflection":
                trajectory += f"--- 评审员反馈 ---\n{record["content"]}\n\n"

        return trajectory.strip()

    def get_last_execution(self) -> str:
        for record in reversed(self.records):
            if record["type"] == "execution":
                return record["content"]
        return None


class MyReflectionAgent(ReflectionAgent):
    """
    重写的 Reflection Agent - 自我反思和结果优化的智能体
    """

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        max_iterations: int = 3,
        custom_prompt: Optional[str] = None,
    ):
        super().__init__(name, llm, system_prompt, config)
        self.max_iterations = max_iterations
        self.memory = Memory()
        self.prompt_template = custom_prompt if custom_prompt else DEFAULT_PROMPTS
        print(f"✅ {name} 初始化完成，最大迭代次数: {max_iterations}")

    def run(self, task: str):
        print(f"\n--- 开始处理任务 ---\n")
        print(f"任务: {task}")

        self.memory = Memory()

        print(f"\n--- 正在进行初始尝试 ---")
        initial_prompt = self.prompt_template["initial"].format(task=task)
        initial_content = self._get_llm_response(initial_prompt)
        self.memory.add_record("execution", initial_content)

        for i in range(self.max_iterations):
            print(f"--- 第 {i + 1} / {self.max_iterations} 轮迭代 ---")

            print("\n-> 正在进行反思...")
            last_content = self.memory.get_last_execution()
            reflect_prompt = self.prompt_template["reflect"].format(
                task=task, content=last_content
            )
            feedback = self._get_llm_response(reflect_prompt)
            self.memory.add_record("reflection", feedback)

            if "无需改进" in feedback or "no need for improvement" in feedback.lower():
                print("\n✅ 反思认为内容已无需改进，任务完成。")
                break

            print("\n-> 正在优化...")
            refine_prompt = self.prompt_template["refine"].format(
                task=task, last_content=last_content, feedback=feedback
            )
            refined_content = self._get_llm_response(refine_prompt)
            self.memory.add_record("execution", refined_content)

        final_content = self.memory.get_last_execution()
        print("\n --- 任务完成 ---\n")
        print(f"最终生成的内容: \n{final_content}")
        return final_content

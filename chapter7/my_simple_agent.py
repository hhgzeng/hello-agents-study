# my_simple_agent.py
import re
from typing import Iterator, Optional

from hello_agents import Config, HelloAgentsLLM, Message, SimpleAgent, ToolRegistry


class MySimpleAgent(SimpleAgent):
    """
    重写的简单对话Agent 展示如何基于框架基类构建自定义Agent
    """

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        tool_registry: Optional[ToolRegistry] = None,
        enable_tool_calling: bool = True,
    ):
        super().__init__(name, llm, system_prompt, config)
        self.tool_registry = tool_registry
        self.enable_tool_calling = enable_tool_calling and tool_registry is not None
        print(
            f"✅ {name} 初始化完成，工具调用: {'启用' if self.enable_tool_calling else '禁用'}"
        )

    def run(self, input_text: str, max_tool_iterations: int = 3, **kwargs) -> str:
        """
        重写的运行方法 - 实现简单对话逻辑，支持可选工具调用
        """
        print(f"🤖 {self.name} 正在处理: {input_text}")

        # construct message list
        messages = []

        # add system message (which may include tool info)
        enhanced_system_prompt = self._get_enhanced_system_prompt()
        messages.append({"role": "system", "content": enhanced_system_prompt})

        # add historic message
        for msg in self._history:
            messages.append({"role": msg.role, "content": msg.content})

        # add current user message
        messages.append({"role": "user", "content": input_text})

        # if not enable tool call, use simple conversation logic
        if not self.enable_tool_calling:
            response = self.llm.invoke(messages, **kwargs)
            self.add_message(Message(input_text, "user"))
            self.add_message(Message(response, "assistant"))
            print(f"✅ {self.name} 响应完成")
            return response

        # support multi-tools call
        return self._run_with_tools(messages, input_text, max_tool_iterations, **kwargs)

    def _get_enhanced_system_prompt(self) -> str:
        """construct enhanced system prompt, including tool info"""
        base_prompt = self.system_prompt or "你是一个有用的 AI 助手"

        if not self.enable_tool_calling or not self.tool_registry:
            return base_prompt

        # get tool description
        tools_description = self.tool_registry.get_tools_description()
        if not tools_description or tools_description == "暂无可用工具":
            return base_prompt

        tools_section = "\n\n## 可用工具\n"
        tools_section += "你可以使用以下工具来帮助回答问题: \n"
        tools_section += tools_description + "\n"

        tools_section += "\n## 工具调用格式\n"
        tools_section += "当需要使用工具时，请使用以下格式:\n"
        tools_section += "`[TOOL_CALL:{tool_name}:{parameters}]`\n"
        tools_section += "例如: `[TOOL_CALL:search:Python编程]` 或 `[TOOL_CALL:memory:recall=用户信息]`\n\n"
        tools_section += "工具调用结果会自动插入到对话中，然后你可以基于结果继续回答。\n"

        return base_prompt + tools_section

    def _run_with_tools(self, messages: list, input_text: str, max_tool_interations: int, **kwargs) -> str:
        """support tool call run logic"""
        current_iteration = 0
        final_response = ""

        while current_iteration < max_tool_interations:
            # call LLM
            response = self.llm.invoke(messages, **kwargs)

            # check whether is tool call
            tool_calls = self._parse_tool_calls(response)

            if tool_calls:
                print(f"🔧 监测到 {len(tool_calls)} 个工具调用")
                # execute all tool call and collect results
                tool_results = []
                clean_response = response

                for call in tool_calls:
                    result = self._execute_tool_call(call["tool_name"], call["parameters"])
                    tool_results.append(result)
                    # remove the tool call mark from the response
                    clean_response = clean_response.replace(call["original", ""])

                # construct messages including tool results
                messages.append({"role": "assistant", "content": clean_response})

                # add tool results
                tool_results_text = "\n\n".join(tool_results)
                messages.append({"role": "user", "content": f"工具执行结果:\n{tool_results_text}\n\n请基于这些结果给出完整的回答。"})

                current_iteration += 1
                continue

            # if not tool call, this is the final answer
            final_response = response
            break

        # if exceed max iteration, get the final answer
        if current_iteration >= max_tool_interations and not final_response:
            final_response = self.llm.invoke(messages, **kwargs)

        # save to history
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final_response, "assistant"))
        print(f"✅ {self.name} 响应完成")

        return final_response

    def _parse_tool_calls(self, text: str) -> list:
        """parse tool call in text"""
        pattern = r'\[TOOL_CALL:([^:]+):(^\]]+)\]'
        matches = re.findall(pattern, text)

        tool_calls = []
        for tool_name, parameters in matches:
            tool_calls.append({
                "tool_name": tool_name.strip(),
                "parameters": parameters.strip(),
                "original": f"[TOOL_CALL:{tool_name}:{parameters}]"
            })

        return tool_calls

    def _execute_tool_call(self, tool_name: str, parameters: str) -> str:
        """execute tool call"""
        if not self.tool_registry:
            return f"❌ 错误：未配置工具注册表"

        try:
            if tool_name == "calculator":
                result = self.tool_registry.execute_tool(tool_name, parameters)
            else:
                param_dict = self._parse_tool_parameters(tool_name, parameters)
                tool = self.tool_registry.get_tool(tool_name)
                if not tool:
                    return f"❌ 错误：未找到工具 '{tool_name}'"

                result = tool.run(param_dict)

            return f"🔧 工具 {tool_name} 执行结果:\n{result}"

        except Exception as e:
            return f"❌ 工具调用失败: {str(e)}"

    def _parse_tool_parameters(self, tool_name: str, parameters: str) -> dict:
        """intelligent parse tool parameters"""
        param_dict = {}

        if '=' in parameters:
            # format: key=value or action=search, query=Python
            if ',' in parameters:
                # multiple parameters
                pairs = parameters.split(',')
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        param_dict[key.strip()] = value.strip()
            else:
                # single parameter: key=value
                key, value = parameters.split('=', 1)
                param_dict[key.strip()] = value.strip()
        else:
            # 直接传入参数，根据工具类型智能推断
            if tool_name == "search":
                param_dict = {"query": parameters}
            elif tool_name == "memory":
                param_dict = {"action": "search", "query": parameters}
            else:
                param_dict = {"input": parameters}

        return param_dict

    def stream_run(self, input_text: str, **kwargs) -> Iterator[str]:
        """自定义的流式运行方法"""
        print(f"🌊 {self.name} 开始流式处理: {input_text}")

        messages = []

        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        for msg in self._history:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": input_text})

        # stream call LLM
        full_response = ""
        print("📝 实时响应: ", end="")
        for chunk in self.llm.stream_invoke(messages, **kwargs):
            full_response += chunk
            print(chunk, end="", flush=True)
            yield chunk
        
        print()

        # save completed messages to history
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(full_response, "assistant"))
        print(f"✅ {self.name} 流式响应完成")

    def add_tool(self, tool) -> None:
        """add tool to Agent (simple method)"""
        if not self.tool_registry:
            self.tool_registry = ToolRegistry()
            self.enable_tool_calling = True
        
        self.tool_registry.register_tool(tool)
        print(f"🔧 工具 '{tool.name}' 已添加")
    
    def has_tools(self) -> bool:
        """check if there is any avaiable tools"""
        return self.enable_tool_calling and self.tool_registry is not None
    
    def remove_tool(self, tool_name: str) -> bool:
        """remove tool"""
        if self.tool_registry:
            self.tool_registry.unregister(tool_name)
            return True
        return False
    
    def list_tools(self) -> list:
        """list all avaiable tools"""
        if self.tool_registry:
            return self.tool_registry.list_tools()
        return []

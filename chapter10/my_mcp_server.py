"""
简单的 MCP (Model Context Protocol) 服务器示例
通过 stdio 传输实现，提供基本的计算工具
遵循 JSON-RPC 2.0 规范
"""

import json
import sys
from typing import Any, Optional


class SimpleMCPServer:
    """简单的 MCP 服务器实现"""

    def __init__(self):
        self.tools = {
            "add": {
                "description": "Add two numbers",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"},
                    },
                    "required": ["a", "b"],
                },
            },
            "subtract": {
                "description": "Subtract two numbers",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"},
                    },
                    "required": ["a", "b"],
                },
            },
            "multiply": {
                "description": "Multiply two numbers",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"},
                    },
                    "required": ["a", "b"],
                },
            },
        }

    def make_response(
        self, request_id: Optional[int], result: Any = None, error: Optional[str] = None
    ) -> dict:
        """创建符合 JSON-RPC 2.0 规范的响应"""
        response = {
            "jsonrpc": "2.0",
        }
        if request_id is not None:
            response["id"] = request_id

        if error:
            response["error"] = {"code": -32603, "message": error}
        else:
            response["result"] = result

        return response

    def handle_initialize(self, params: dict) -> dict:
        """处理初始化请求"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
            },
            "serverInfo": {
                "name": "Simple MCP Server",
                "version": "1.0.0",
            },
        }

    def handle_list_tools(self, params: dict) -> dict:
        """处理列表工具请求"""
        tools = []
        for name, schema in self.tools.items():
            tools.append(
                {
                    "name": name,
                    "description": schema["description"],
                    "inputSchema": schema["inputSchema"],
                }
            )
        return {"tools": tools}

    def handle_call_tool(self, params: dict) -> tuple:
        """处理工具调用请求
        返回 (result, error) 元组
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "add":
                result = arguments["a"] + arguments["b"]
            elif tool_name == "subtract":
                result = arguments["a"] - arguments["b"]
            elif tool_name == "multiply":
                result = arguments["a"] * arguments["b"]
            else:
                return None, f"Unknown tool: {tool_name}"

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Result: {result}",
                    }
                ]
            }, None
        except Exception as e:
            return None, str(e)

    def process_message(self, message: dict) -> Optional[dict]:
        """处理 MCP 协议消息
        返回 JSON-RPC 2.0 格式的响应
        """
        method = message.get("method")
        msg_id = message.get("id")

        # 通知消息没有 id，不需要响应
        is_notification = msg_id is None

        try:
            if method == "initialize":
                result = self.handle_initialize(message.get("params", {}))
                return self.make_response(msg_id, result=result)

            elif method == "tools/list":
                result = self.handle_list_tools(message.get("params", {}))
                return self.make_response(msg_id, result=result)

            elif method == "tools/call":
                result, error = self.handle_call_tool(message.get("params", {}))
                if error:
                    return self.make_response(msg_id, error=error)
                return self.make_response(msg_id, result=result)

            # 处理通知消息（如 notifications/initialized）
            elif method and method.startswith("notifications/"):
                # 通知消息不需要响应
                return None

            else:
                if is_notification:
                    # 未知通知，不需要响应
                    return None
                return self.make_response(msg_id, error=f"Unknown method: {method}")

        except Exception as e:
            if is_notification:
                # 通知消息处理出错，但不需要响应
                return None
            return self.make_response(msg_id, error=str(e))


def main():
    """主入口点"""
    server = SimpleMCPServer()

    while True:
        try:
            # 读取一行输入
            line = sys.stdin.readline()
            if not line:
                break

            # 解析 JSON 消息
            message = json.loads(line)

            # 处理消息
            response = server.process_message(message)

            # 发送响应
            if response:
                print(json.dumps(response), flush=True)

        except json.JSONDecodeError as e:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": f"Parse error: {e}"},
                    }
                ),
                flush=True,
            )
        except Exception as e:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": f"Internal error: {e}"},
                    }
                ),
                flush=True,
            )


if __name__ == "__main__":
    main()

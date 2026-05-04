# 01_TestConnect.py — Test script for MCP, ANP, and A2A protocol tools
from hello_agents.tools import MCPTool, A2ATool, ANPTool


# ============================================================
# 1. MCP (Model Context Protocol) — 调用远程工具
# ============================================================
mcp_tool = MCPTool()
result = mcp_tool.run(
    {
        "action": "call_tool",
        "tool_name": "add",
        "arguments": {"a": 10, "b": 20},
    }
)
print(f"[MCP] 计算结果: {result}")  # 预期输出: 30.0

# ============================================================
# 2. ANP (Agent Network Protocol) — 注册 & 发现服务
# ============================================================
anp_tool = ANPTool()

anp_tool.run(
    {
        "action": "register_service",
        "service_id": "calculator",
        "service_type": "math",
        "endpoint": "http://localhost:8080",
    }
)

services = anp_tool.run({"action": "discover_services"})
print(f"[ANP] 发现的服务: {services}")

# ============================================================
# 3. A2A (Agent-to-Agent) — 建立点对点连接
# ============================================================
a2a_tool = A2ATool("http://localhost:5000")
print("[A2A] 工具创建成功")
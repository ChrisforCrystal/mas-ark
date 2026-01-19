
import time
import json
from dataclasses import dataclass
from typing import List, Dict, Any

# ==========================================
# 1. 模拟 CRD 配置 (Configuration)
# ==========================================

@dataclass
class ToolConfig:
    name: str
    type: str # "mcp" or "http"
    
@dataclass
class AgentConfig:
    name: str
    prompt: str
    tools: List[ToolConfig]

@dataclass
class TeamConfig:
    name: str
    members: List[AgentConfig]

# ==========================================
# 2. 模拟基础设施 (MCP Server & LLM)
# ==========================================

class MockMCPServer:
    """模拟一个提供文件操作的 MCP 工具服务"""
    def call_tool(self, tool_name: str, args: Dict) -> str:
        if tool_name == "mcp-filesystem-write-file":
            return f"[MCP] Success: Content written to {args.get('path')}"
        elif tool_name == "web-search":
            return f"[Tool] Search Result: '2024 AI Trends: Generative AI is booming...'"
        return "[MCP] Error: Tool not found"

class MockLLM:
    """模拟大模型"""
    def chat(self, system_prompt: str, user_input: str) -> str:
        print(f"  [LLM Thinking] (Prompt includes: '{user_input[:20]}...')")
        time.sleep(1) # Simulate network latency
        
        # 简单的规则模拟 LLM 决策
        if "Research" in user_input and "search" not in system_prompt:
             # 第一次请求，LLM 决定调用工具
             return json.dumps({"action": "call_tool", "tool": "web-search", "args": {"query": "AI Trends 2024"}})
        elif "Summarize" in user_input:
             return "Based on the search results, AI is growing fast in 2024."
        elif "Write" in user_input:
             # 需要写文件
             return json.dumps({"action": "call_tool", "tool": "mcp-filesystem-write-file", "args": {"path": "report.md", "content": "Report..."}})
        else:
             return "I have completed the task."

# ==========================================
# 3. 模拟 Ark Controller (The Engine)
# ==========================================

class ArkController:
    def __init__(self):
        self.mcp_client = MockMCPServer()
        self.llm_client = MockLLM()
        self.memory = []

    def run_team(self, team: TeamConfig, user_query: str):
        print(f"🚀 [Controller] Starting Team: {team.name}")
        print(f"📝 [Controller] Query: {user_query}")
        
        context = user_query
        
        # A2A (Agent to Agent) 核心逻辑：上一个 Agent 的输出 = 下一个 Agent 的输入
        for i, agent in enumerate(team.members):
            print(f"\n--- [Controller] Activating Agent {i+1}: {agent.name} ---")
            
            # 1. 思考 (Think)
            response = self.llm_client.chat(agent.prompt, context)
            
            # 2. 行动 (Act - Tool Call)
            if "call_tool" in response:
                tool_call = json.loads(response)
                print(f"  ⚡ [Controller] Intercepted Tool Call: {tool_call['tool']}")
                
                # Controller 负责去调用 MCP
                tool_result = self.mcp_client.call_tool(tool_call['tool'], tool_call['args'])
                print(f"  ✅ [Controller] Tool Output: {tool_result}")
                
                # 3. 观察 (Observe - Re-prompt LLM)
                # 将工具结果喂回给 LLM 让他总结
                context = f"Observation: {tool_result}. Please summarize this."
                final_answer = self.llm_client.chat(agent.prompt, context)
                print(f"  🤖 [Agent {agent.name}] Says: {final_answer}")
                
                # A2A: 更新上下文传递给下一个人
                context = f"Previous Agent ({agent.name}) said: {final_answer}. Now your turn."
            else:
                print(f"  🤖 [Agent {agent.name}] Says: {response}")
                context = response

        print(f"\n🏁 [Controller] Team Execution Finished. Final Result: {context}")

# ==========================================
# 4. 运行 Demo
# ==========================================

if __name__ == "__main__":
    # 定义资源 (YAML in code)
    researcher = AgentConfig("Researcher", "You are a researcher.", [ToolConfig("web-search", "http")])
    writer = AgentConfig("Writer", "You are a writer.", [ToolConfig("mcp-filesystem-write-file", "mcp")])
    team = TeamConfig("MyTeam", [researcher, writer])
    
    # 启动控制器
    controller = ArkController()
    controller.run_team(team, "Do research on AI and write a report.")

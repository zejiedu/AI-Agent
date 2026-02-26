import dashscope
import re
import json
import os
from dashscope import Generation
from typing import List, Dict, Optional

# ====================== 全局配置 ======================
dashscope.api_key = "YOUR_API_KEY"
LONG_TERM_MEMORY_PATH = "llm_agent_long_memory.json"
LLM_MODEL = "qwen-turbo"
LLM_TEMPERATURE = 0.3

# ====================== 长期记忆工具函数 ======================
def load_long_term_memory() -> List[Dict[str, str]]:
    if os.path.exists(LONG_TERM_MEMORY_PATH):
        try:
            with open(LONG_TERM_MEMORY_PATH, "r", encoding="utf-8") as f:
                memory = json.load(f)
                if isinstance(memory, list):
                    print(f"✅ 长期记忆加载成功，共{len(memory)}条对话记录")
                    return memory
                else:
                    print("⚠️ 记忆文件格式错误，初始化空记忆")
                    return []
        except Exception as e:
            print(f"⚠️ 加载记忆异常：{str(e)}，初始化空记忆")
            return []
    else:
        with open(LONG_TERM_MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print("✅ 已创建新的长期记忆文件")
        return []

def save_long_term_memory(memory: List[Dict[str, str]], max_length: int = 20) -> None:
    try:
        trimmed_memory = memory[-max_length:]
        with open(LONG_TERM_MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(trimmed_memory, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ 保存长期记忆失败：{str(e)}")

# ====================== 工具函数 ======================
def calculate_tool(expression: str) -> str:
    allowed_chars = set("0123456789+-*/(). ")
    if not all(char in allowed_chars for char in expression):
        return "计算错误：仅支持数字和+-*/()运算"
    try:
        result = eval(expression)
        return f"计算结果：{expression} = {result}"
    except ZeroDivisionError:
        return "计算错误：除数不能为0"
    except SyntaxError:
        return "计算错误：表达式语法错误"
    except Exception:
        return "计算错误：无法识别的表达式格式"

def parse_tool_call(llm_output: str) -> Optional[Dict[str, str]]:
    pattern = r"TOOL:\s*calculate\((.*?)\)"
    match = re.search(pattern, llm_output.strip(), re.IGNORECASE)
    if match:
        return {"tool": "calculate", "params": match.group(1).strip()}
    return None

# ====================== 智能体主类 ======================
class LLMAgentWithLongMemory:
    def __init__(self):
        self.memory = load_long_term_memory()

    def perceive(self) -> str:
        user_input = input("你：").strip()
        if not user_input:
            print("智能体：请输入有效内容～")
            return self.perceive()
        return user_input

    def decide(self, user_input: str) -> str:
        if "清空记忆" in user_input:
            self.memory = []
            save_long_term_memory(self.memory)
            return "✅ 已清空所有长期记忆！"

        system_prompt = {
            "role": "system",
            "content": """
你是具备长期记忆和工具调用能力的智能体，遵循以下规则：
1. 记忆：你能记住所有历史对话，重启后也不会丢失；
2. 工具：仅拥有calculate(数学表达式)工具，计算需求必须输出：TOOL: calculate(表达式)；
3. 输出：工具调用仅返回格式指令，非计算需求直接友好回复，回答简洁（≤100字）。
            """
        }

        messages = [system_prompt] + self.memory
        messages.append({"role": "user", "content": user_input})

        try:
            response = Generation.call(
                model=LLM_MODEL,
                messages=messages,
                temperature=LLM_TEMPERATURE,
                top_p=0.6
            )
            return response.output.text
        except Exception as e:
            return f"LLM调用失败：{str(e)}"

    def act(self, llm_reply: str, user_input: str) -> str:
        tool_call = parse_tool_call(llm_reply)
        if tool_call and tool_call["tool"] == "calculate":
            final_reply = calculate_tool(tool_call["params"])
            print(f"智能体（计算器工具）：{final_reply}")
        else:
            final_reply = llm_reply
            print(f"智能体：{final_reply}")

        self.memory.append({"role": "user", "content": user_input})
        self.memory.append({"role": "assistant", "content": final_reply})
        save_long_term_memory(self.memory)

        return final_reply

    def run(self) -> None:
        print("📌 LLM智能体（带长期记忆）已启动，输入'exit'退出对话\n")
        while True:
            user_input = self.perceive()
            if user_input.lower() == "exit":
                print("智能体：再见！已保存所有对话记忆～")
                break
            llm_reply = self.decide(user_input)
            self.act(llm_reply, user_input)

# ====================== 运行入口 ======================
if __name__ == "__main__":
    agent = LLMAgentWithLongMemory()
    agent.run()
import dashscope


import dashscope
import re
from dashscope import Generation
from typing import List, Dict, Optional

# 你自己的 API Key
dashscope.api_key = "YOUR_API_KEY"

class ToolEnabledLLMAgent:
    """具备工具调用能力的LLM智能体（计算器工具）"""
    def __init__(self):
        self.context_memory: List[Dict[str, str]] = []

    # ========== 工具定义 ==========
    def calculate(self, expression: str) -> str:
        """
        计算器工具：执行数学表达式计算
        :param expression: 数学表达式（如"1+2*3"）
        :return: 计算结果或错误信息
        """
        # 安全校验：仅允许数字和基础运算符
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "计算错误：仅支持数字和+-*/()运算"
        
        try:
            # 生产环境建议使用ast.literal_eval替代eval，提升安全性
            result = eval(expression)
            return f"计算结果：{expression} = {result}"
        except ZeroDivisionError:
            return "计算错误：除数不能为0"
        except:
            return "计算错误：表达式格式不合法（如'2*(3+4)'）"

    def parse_tool_call(self, llm_output: str) -> Optional[Dict[str, str]]:
        """
        解析LLM输出的工具调用指令
        :param llm_output: LLM原始输出
        :return: 工具调用信息（如{"tool": "calculate", "params": "1+2"}），无调用则返回None
        """
        # 匹配格式：TOOL: calculate(表达式)
        pattern = r"TOOL:\s*calculate\((.*?)\)"
        match = re.search(pattern, llm_output.strip(), re.IGNORECASE)
        if match:
            return {
                "tool": "calculate",
                "params": match.group(1).strip()
            }
        return None

    # ========== 核心模块 ==========
    def perceive(self) -> str:
        """感知模块：获取用户输入"""
        user_input = input("你：").strip()
        if not user_input:
            return self.perceive()
        return user_input

    def decide(self, user_input: str) -> str:
        """决策模块：LLM推理（含工具调用判断）"""
        # 1. 定义System Prompt（包含工具使用说明）
        system_prompt = {
            "role": "system",
            "content": """
你是具备计算能力的智能体，遵循以下规则：
1. 当用户提出计算需求时，必须严格按格式输出工具调用指令：TOOL: calculate(数学表达式)；
2. 非计算需求直接回答，无需调用工具；
3. 回答简洁，不超过100字。
            """
        }

        # 2. 构造消息链
        messages = [system_prompt] + self.context_memory
        messages.append({"role": "user", "content": user_input})

        # 3. 调用LLM
        try:
            response = Generation.call(
                model="qwen-turbo",
                messages=messages,
                temperature=0.3,  # 极低随机性，保证工具调用格式准确
                top_p=0.6
            )
            return response.output.text
        except Exception as e:
            return f"LLM调用失败：{str(e)}"

    def act(self, llm_reply: str, user_input: str) -> str:
        """
        动作模块：执行回复或工具调用
        :param llm_reply: LLM原始回复
        :param user_input: 当前用户输入
        :return: 最终回复内容（用于保存到记忆）
        """
        # 1. 解析工具调用指令
        tool_call = self.parse_tool_call(llm_reply)
        if tool_call and tool_call["tool"] == "calculate":
            # 2. 执行计算器工具
            tool_result = self.calculate(tool_call["params"])
            print(f"智能体（计算器工具）：{tool_result}")
            final_reply = tool_result
        else:
            # 3. 无工具调用，直接输出LLM回复
            print(f"智能体：{llm_reply}")
            final_reply = llm_reply

        # 4. 保存到记忆
        self.context_memory.append({"role": "user", "content": user_input})
        self.context_memory.append({"role": "assistant", "content": final_reply})
        return final_reply

    def run(self) -> None:
        """智能体主循环"""
        print("工具增强型LLM智能体已启动（输入'exit'退出）\n")
        while True:
            user_input = self.perceive()
            if user_input.lower() == "exit":
                print("智能体：再见！")
                break
            llm_reply = self.decide(user_input)
            self.act(llm_reply, user_input)

if __name__ == "__main__":
    agent = ToolEnabledLLMAgent()
    agent.run()
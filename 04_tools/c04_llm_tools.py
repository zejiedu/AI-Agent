import dashscope
import re
import json
import os
import requests
from typing import List, Dict, Optional, Callable
from dashscope import Generation

# ====================== 全局配置 ======================
# 1. LLM配置（替换为你的API Key）
dashscope.api_key = "YOUR_API_KEY"
LLM_MODEL = "qwen-turbo"
LLM_TEMPERATURE = 0.2

# 2. 长期记忆配置
LONG_TERM_MEMORY_PATH = "llm_agent_long_memory.json"
MAX_MEMORY_LENGTH = 20  # 最大记忆条数

# ====================== 长期记忆工具函数 ======================
def load_long_term_memory() -> List[Dict[str, str]]:
    """加载长期记忆（保留第3章逻辑，补充格式校验）"""
    if os.path.exists(LONG_TERM_MEMORY_PATH):
        try:
            with open(LONG_TERM_MEMORY_PATH, "r", encoding="utf-8") as f:
                memory = json.load(f)
                if isinstance(memory, list):
                    print(f"✅ 加载长期记忆成功，共{len(memory)}条记录")
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

def save_long_term_memory(memory: List[Dict[str, str]]) -> None:
    """保存长期记忆（限制长度，保留第3章逻辑）"""
    try:
        trimmed_memory = memory[-MAX_MEMORY_LENGTH:]
        with open(LONG_TERM_MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(trimmed_memory, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ 保存长期记忆失败：{str(e)}")

# ====================== 工具函数库 ======================
def get_weather(city: str) -> str:
    """天气查询工具（完整异常处理版）"""
    if not city or city.strip() == "":
        return "❌ 请输入有效的城市名（如北京、上海）"
    
    try:
        # url = f"https://wttr.in/{city.strip()}?format=3" # 原始URL，延迟比较大，因此使用uapis.cn的API
        import urllib.parse
        encoded_city = urllib.parse.quote(city.strip())
        url = f'https://uapis.cn/api/v1/misc/weather?city={encoded_city}'
        headers = {"User-Agent": "Mozilla/5.0"}
        # 移除verify=False以避免SSL警告，或使用requests.packages.urllib3.disable_warnings()
        import requests.packages.urllib3
        requests.packages.urllib3.disable_warnings()
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        # 直接使用response.text，requests会自动处理编码
        weather_info = response.text
        return f"✅ {weather_info}"
    except requests.exceptions.Timeout:
        return "❌ 天气API请求超时，请稍后重试"
    except requests.exceptions.HTTPError:
        return "❌ 城市不存在或API返回错误"
    except requests.exceptions.RequestException as e:
        return f"❌ 网络请求失败：{str(e)}"
    except Exception as e:
        return f"❌ 天气查询异常：{str(e)}"

def calculate_tool(expression: str) -> str:
    """计算器工具（安全优化版）"""
    allowed_chars = set("0123456789+-*/(). ")
    if not all(char in allowed_chars for char in expression):
        return "❌ 计算表达式非法，仅支持数字和+-*/()运算"
    
    try:
        result = eval(expression)
        return f"✅ 计算结果：{expression} = {result}"
    except ZeroDivisionError:
        return "❌ 计算错误：除数不能为0"
    except SyntaxError:
        return "❌ 计算错误：表达式语法错误（如缺少括号）"
    except Exception as e:
        return f"❌ 计算失败：{str(e)}"

# ====================== 多工具智能体主类 ======================
class MultiToolLLMAgent:
    def __init__(self):
        self.memory = load_long_term_memory()  # 加载长期记忆

    def perceive(self) -> str:
        """感知模块：获取用户输入（过滤空值）"""
        user_input = input("你：").strip()
        if not user_input:
            print("智能体：请输入有效内容～")
            return self.perceive()
        return user_input

    def decide(self, user_input: str) -> str:
        """决策模块：LLM推理（多工具调用规则）"""
        # 清空记忆指令
        if "清空记忆" in user_input:
            self.memory = []
            save_long_term_memory(self.memory)
            return "✅ 已清空所有长期记忆！"

        # 系统提示词（多工具规则）
        system_prompt = {
            "role": "system",
            "content": """
你是具备长期记忆和多工具调用能力的智能体，严格遵循以下规则：
1. 可用工具列表：
   - calculate(数学表达式)：执行数学计算，参数为合法数学表达式；
   - get_weather(城市名)：查询城市天气，参数为中文城市名。
2. 工具调用格式（必须严格遵守，无额外内容）：
   正确：TOOL: calculate(100+200)、TOOL: get_weather(广州)
3. 回复规则：
   - 仅计算/查天气需求调用对应工具，其他需求直接自然语言回复；
   - 回复简洁，非工具调用内容不超过100字。
            """
        }

        # 构造LLM输入
        messages = [system_prompt] + self.memory
        messages.append({"role": "user", "content": user_input})

        # 调用LLM API
        try:
            response = Generation.call(
                model=LLM_MODEL,
                messages=messages,
                temperature=LLM_TEMPERATURE,
                top_p=0.5
            )
            return response.output.text
        except Exception as e:
            return f"LLM调用失败：{str(e)}"

    def parse_tool_call(self, llm_output: str) -> Optional[Dict[str, str]]:
        """通用工具指令解析（支持多工具）"""
        pattern = r"^TOOL:\s*(\w+)\((.*?)\)$"
        match = re.match(pattern, llm_output.strip(), re.IGNORECASE)
        if not match:
            return None
        return {
            "tool": match.group(1).strip().lower(),
            "params": match.group(2).strip()
        }

    def execute_tool(self, tool_info: Dict[str, str]) -> str:
        """工具执行（映射表调用）"""
        tool_mapping = {
            "calculate": calculate_tool,
            "get_weather": get_weather
        }
        tool_name = tool_info["tool"]
        tool_params = tool_info["params"]
        
        if tool_name in tool_mapping:
            try:
                return tool_mapping[tool_name](tool_params)
            except Exception as e:
                return f"❌ 工具执行失败：{str(e)}"
        else:
            return f"❌ 未知工具：{tool_name}，仅支持calculate/get_weather"

    def act(self, llm_reply: str, user_input: str) -> str:
        """动作模块：执行工具/输出回复"""
        tool_info = self.parse_tool_call(llm_reply)
        if tool_info:
            tool_result = self.execute_tool(tool_info)
            print(f"智能体（{tool_info['tool']}工具）：{tool_result}")
            final_reply = tool_result
        else:
            final_reply = llm_reply.strip()
            print(f"智能体：{final_reply}")

        # 更新并保存记忆
        self.memory.append({"role": "user", "content": user_input})
        self.memory.append({"role": "assistant", "content": final_reply})
        save_long_term_memory(self.memory)

        return final_reply

    def run(self) -> None:
        """智能体主循环"""
        print("📌 多工具LLM智能体（带长期记忆）已启动，输入'exit'退出\n")
        while True:
            user_input = self.perceive()
            if user_input.lower() == "exit":
                print("智能体：再见！已保存所有对话记忆～")
                break
            llm_reply = self.decide(user_input)
            self.act(llm_reply, user_input)

# ====================== 运行入口 ======================
if __name__ == "__main__":
    agent = MultiToolLLMAgent()
    agent.run()
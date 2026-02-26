import dashscope
import re
import json
import os
import requests

# ====================== 全局配置 ======================
dashscope.api_key = "YOUR_API_KEY"
MEMORY_FILE = "agent_memory.json"
MAX_MEMORY_LENGTH = 20
LLM_MODEL = "qwen-turbo"
LLM_TEMPERATURE = 0.2
# ====================== 工具1：计算器 ======================
def calculate(expression: str) -> str:
    try:
        # 安全字符校验
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            return "❌ 仅支持数字与基础运算符"
        result = eval(expression)
        return f"✅ 计算结果：{result}"
    except ZeroDivisionError:
        return "❌ 除数不能为0"
    except SyntaxError:
        return "❌ 表达式语法错误"
    except:
        return "❌ 计算失败"

# ====================== 工具2：天气查询 ======================
def get_weather(city: str) -> str:
    try:
        city = city.strip()
        url = f"https://wttr.in/{city}?format=3"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return f"✅ {resp.text}"
    except:
        return "❌ 天气查询失败"

# ====================== 工具3：联网搜索（新增） ======================
def web_search(query: str, max_results: int = 3) -> str:
    if not query:
        return "❌ 请输入搜索内容"
    url = "https://search.inetol.net/search"
    params = {"q": query, "format": "json", "language": "zh-CN"}
    try:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        res = []
        for item in data.get("results", [])[:max_results]:
            title = item.get("title", "无标题")
            content = item.get("content", "无摘要")
            res.append(f"【标题】{title}\n【摘要】{content}\n")
        return "\n".join(res) if res else "🔍 未找到结果"
    except:
        return "❌ 搜索服务异常"

# ====================== 长期记忆模块 ======================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_memory(memory):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory[-MAX_MEMORY_LENGTH:], f, ensure_ascii=False, indent=2)
    except:
        pass

# ====================== 多工具智能体 ======================
class SearchEnabledAgent:
    def __init__(self):
        self.memory = load_memory()

    def think(self, user_input):
        # 清空记忆指令
        if "清空记忆" in user_input:
            self.memory = []
            save_memory(self.memory)
            return "✅ 记忆已清空"

        system_prompt = {
            "role": "system",
            "content": """
你是具备长期记忆的智能体，可使用三种工具：
1 calculate(数学表达式) → 数学计算
2 get_weather(城市名) → 查询天气
3 search(关键词) → 联网搜索

需要工具时，严格输出：
TOOL: 函数名(参数)
不需要工具则直接自然语言回复。
            """
        }

        messages = [system_prompt] + self.memory
        messages.append({"role": "user", "content": user_input})

        try:
            response = dashscope.Generation.call(
                model=LLM_MODEL,
                messages=messages,
                temperature=LLM_TEMPERATURE,
                top_p=0.5
            )
            return response.output.text
        except:
            return "❌ LLM调用失败"

    def use_tool(self, text):
        pattern = r"TOOL:\s*(\w+)\((.*?)\)"
        match = re.search(pattern, text.strip())
        if not match:
            return None

        tool_name = match.group(1)
        param = match.group(2).strip()

        tool_map = {
            "calculate": calculate,
            "get_weather": get_weather,
            "search": web_search
        }

        if tool_name in tool_map:
            try:
                return tool_map[tool_name](param)
            except:
                return f"❌ 工具{tool_name}执行失败"
        return "❌ 未知工具"

    def run(self):
        print("🧠 智能体已启动（搜索+天气+计算+长期记忆）")
        while True:
            ipt = input("你：")
            if ipt.strip().lower() == "exit":
                print("👋 再见！")
                break

            llm_output = self.think(ipt)
            tool_result = self.use_tool(llm_output)

            if tool_result:
                print("智能体(工具)：", tool_result)
                final = tool_result
            else:
                print("智能体：", llm_output)
                final = llm_output

            self.memory.append({"role": "user", "content": ipt})
            self.memory.append({"role": "assistant", "content": final})
            save_memory(self.memory)

if __name__ == "__main__":
    agent = SearchEnabledAgent()
    agent.run()
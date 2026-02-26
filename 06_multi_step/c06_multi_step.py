import dashscope
import re
import json
import os
import requests

# ====================== 配置 ======================
dashscope.api_key = "YOUR_API_KEY"
MEMORY_FILE = "agent_memory.json"
MAX_MEMORY = 20

# ====================== 工具1：计算 ======================
def calculate(exp):
    try:
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in exp):
            return "❌ 表达式非法"
        return f"✅ 结果：{eval(exp)}"
    except:
        return "❌ 计算失败"

# ====================== 工具2：天气 ======================
def get_weather(city):
    try:
        url = f"https://wttr.in/{city.strip()}?format=3"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        return f"✅ {res.text}"
    except:
        return "❌ 天气查询失败"

# ====================== 工具3：搜索 ======================
def web_search(query):
    try:
        url = "https://search.inetol.net/search"
        params = {"q": query, "format": "json", "language": "zh-CN"}
        res = requests.get(url, params=params, timeout=15)
        data = res.json()
        out = []
        for item in data.get("results", [])[:3]:
            t = item.get("title", "")
            c = item.get("content", "")
            out.append(f"【标题】{t}\n【摘要】{c}")
        return "\n".join(out) if out else "🔍 无结果"
    except:
        return "❌ 搜索失败"

# ====================== 记忆 ======================
def load_mem():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_mem(mem):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(mem[-MAX_MEMORY:], f, ensure_ascii=False, indent=2)

# ====================== 任务规划解析 ======================
def parse_plan(text):
    lines = text.strip().split('\n')
    steps = []
    task_start = False
    for line in lines:
        line = line.strip()
        if line.startswith('TASK:'):
            task_start = True
        elif task_start and line.startswith('STEP'):
            steps.append(line)
        elif line.startswith('FINISH'):
            break
    return steps

# ====================== 工具调用解析 ======================
def parse_tool_call(text):
    pattern = r"TOOL:\s*(\w+)\((.*?)\)"
    match = re.search(pattern, text.strip())
    if not match:
        return None
    return {"name": match[1], "param": match[2].strip()}

# ====================== 高级智能体（带任务规划） ======================
class PlanAgent:
    def __init__(self):
        self.memory = load_mem()
        self.plan_steps = []
        self.current_step = 0

    def llm(self, messages):
        try:
            resp = dashscope.Generation.call(model="qwen-turbo", messages=messages)
            return resp.output.text
        except:
            return "❌ LLM出错"
    def run_step(self, step_content: str):
        messages = [
            {
                "role": "system",
                "content": "你只负责执行步骤，需要工具时严格输出：TOOL: 工具名(参数)，不需要则直接输出结果。"
            },
            {"role": "user", "content": step_content}
        ]
        return self.llm(messages)
    def run_tool(self, tool_call):
        tool_map = {
            "calculate": calculate,
            "get_weather": get_weather,
            "search": web_search
        }
        name = tool_call["name"]
        param = tool_call["param"]
        return tool_map[name](param) if name in tool_map else "❌ 未知工具"

    def chat(self, user_input):
        if "清空记忆" in user_input:
            self.memory = []
            save_mem(self.memory)
            return "✅ 记忆已清空"

        messages = [
            {
                "role": "system",
                "content": """
你是高级智能体，拥有长期记忆、3种工具、多轮任务规划能力。

工具：
1 calculate(表达式) → 计算
2 get_weather(城市) → 天气
3 search(关键词) → 搜索

规则：
1. 简单问题直接回答。
2. 复杂问题必须输出规划：
TASK: 任务
STEP 1: ...
STEP 2: ...
FINISH
3. 执行步骤时输出 TOOL: 函数(参数)
"""
            }
        ] + self.memory + [{"role": "user", "content": user_input}]

        reply = self.llm(messages)
        self.plan_steps = parse_plan(reply)
        self.current_step = 0

        if not self.plan_steps:
            tool = parse_tool_call(reply)
            if tool:
                res = self.run_tool(tool)
                output = f"🛠️ 工具结果：\n{res}"
                final = res
            else:
                output = reply
                final = reply
        else:
            output = "📋 生成任务规划：\n" + reply + "\n"
            self.step_results = []
            for i, step in enumerate(self.plan_steps):
                output += f"\n▶ 执行 {step}\n"
                step_reply = self.run_step(step)
                tool_step = parse_tool_call(step_reply)
                if tool_step:
                    res = self.run_tool(tool_step)
                    output += f"✅ 结果：{res}\n"
                    self.step_results.append(res)
                else:
                    output += f"✅ 结果：{step_reply}\n"
                    self.step_results.append(step_reply)
            final = "任务完成，结果已记录"

        self.memory.append({"role": "user", "content": user_input})
        self.memory.append({"role": "assistant", "content": final})
        save_mem(self.memory)
        return output

# ====================== 运行 ======================
if __name__ == "__main__":
    agent = PlanAgent()
    print("🧠 高级智能体（任务规划版）已启动，输入 exit 退出\n")
    while True:
        ipt = input("你：")
        if ipt.lower() == "exit":
            print("👋 再见")
            break
        print("智能体：", agent.chat(ipt))
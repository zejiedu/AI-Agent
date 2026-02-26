import json
import os  # 补充导入，处理文件路径
from c01_01_simpleAgent import SimpleAgent
class AdvancedAgent(SimpleAgent):
    def __init__(self, memory_path: str = "agent_memory.json"):
        super().__init__()
        self.name = "进阶智能体"
        self.memory_path = memory_path
        self.load_memory()  # 启动时加载长期记忆

    # 长期记忆：保存到文件（持久化）
    def save_memory(self):
        """将记忆写入JSON文件，实现长期存储"""
        try:
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"记忆保存失败：{e}")

    # 加载长期记忆
    def load_memory(self):
        """启动时从文件加载历史记忆"""
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    self.memory = json.load(f)
            except Exception as e:
                print(f"记忆加载失败，初始化空记忆：{e}")
                self.memory = []
        else:
            self.memory = []

    # 工具调用模块：计算器（模拟真实智能体的工具能力）
    def calculate(self, expression: str) -> str:
        """安全的计算器工具（避免eval的安全风险）"""
        try:
            # 仅允许数字和基础运算符，提升安全性
            allowed_chars = "0123456789+-*/(). "
            if not all(c in allowed_chars for c in expression):
                return "计算出错：仅支持数字和+-*/()运算"
            result = eval(expression)  # 演示用，生产环境建议用ast模块
            return f"计算结果：{expression} = {result}"
        except:
            return "计算出错：请输入合法算式（如 1+2*3）"

    # 强化策略逻辑：整合长期记忆+工具调用
    def think(self, user_input: str) -> str:
        self.memory.append(user_input)
        self.save_memory()  # 实时保存长期记忆

        # 工具调用决策
        if "计算" in user_input:
            expr = user_input.replace("计算", "").strip()
            return self.calculate(expr)
        elif "你好" in user_input:
            return f"你好！我是{self.name}，我的记忆重启不丢失～"
        elif "清空记忆" in user_input:
            self.memory = []
            self.save_memory()
            return "记忆已清空（文件已同步删除）"
        else:
            return super().think(user_input)

# 运行进阶智能体
if __name__ == "__main__":
    agent = AdvancedAgent()
    agent.run()
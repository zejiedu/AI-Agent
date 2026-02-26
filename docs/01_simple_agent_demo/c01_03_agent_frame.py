import json
import os
from typing import Dict, List, Optional

# ====================== 1. 环境模块（Environment） ======================
class AgentEnvironment:
    """智能体与外部环境的交互层：负责输入获取、数据持久化"""
    def __init__(self, memory_file: str = "agent_memory.json"):
        self.memory_file = memory_file
        # 初始化空记忆文件（避免文件不存在报错）
        self._init_memory_file()

    def _init_memory_file(self):
        """初始化记忆文件，确保文件存在且格式合法"""
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False)

    def get_user_input(self) -> str:
        """获取环境输入（用户输入）"""
        return input("你：").strip()

    def write_memory(self, memory_data: List[str]):
        """将记忆写入环境（文件）"""
        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise RuntimeError(f"记忆写入失败：{e}")

    def read_memory(self) -> List[str]:
        """从环境（文件）读取记忆"""
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"记忆读取失败：{e}")

# ====================== 2. 感知模块（Perception） ======================
class AgentPerception:
    """感知层：解析环境输入，提取意图和关键信息"""
    @staticmethod
    def parse_input(user_input: str) -> Dict[str, str]:
        """
        解析用户输入，输出结构化感知结果
        返回格式：{"raw_input": 原始输入, "intent": 意图, "key_info": 关键信息}
        """
        intent = "unknown"
        key_info = ""

        if not user_input:
            intent = "empty_input"
        elif "你好" in user_input:
            intent = "greeting"
        elif "计算" in user_input:
            intent = "calculate"
            key_info = user_input.replace("计算", "").strip()
        elif "记忆" in user_input:
            intent = "check_memory"
        elif "清空记忆" in user_input:
            intent = "clear_memory"
        elif "结束" in user_input:
            intent = "exit"

        return {
            "raw_input": user_input,
            "intent": intent,
            "key_info": key_info
        }

# ====================== 3. 记忆模块（State/Memory） ======================
class AgentMemory:
    """记忆层：管理短期/长期记忆，关联环境模块实现持久化"""
    def __init__(self, env: AgentEnvironment):
        self.env = env
        self.short_term_memory: List[str] = []  # 运行时短期记忆
        self.long_term_memory: List[str] = self.env.read_memory()  # 持久化长期记忆

    def add_memory(self, content: str):
        """添加记忆，同步更新短期/长期记忆"""
        if content:  # 过滤空内容
            self.short_term_memory.append(content)
            self.long_term_memory.append(content)
            self.env.write_memory(self.long_term_memory)

    def get_all_memory(self) -> List[str]:
        """获取所有长期记忆"""
        return self.long_term_memory

    def clear_memory(self):
        """清空所有记忆，同步到文件"""
        self.short_term_memory = []
        self.long_term_memory = []
        self.env.write_memory([])

# ====================== 4. 决策模块（Policy） ======================
class AgentPolicy:
    """决策层：基于感知结果和记忆，生成动作决策"""
    @staticmethod
    def make_decision(perception_result: Dict[str, str], memory: AgentMemory) -> str:
        """
        核心决策逻辑：根据感知结果和记忆生成回复
        :param perception_result: 感知模块的解析结果
        :param memory: 记忆模块实例
        :return: 决策结果（回复内容）
        """
        intent = perception_result["intent"]
        key_info = perception_result["key_info"]

        if intent == "empty_input":
            return "请输入有效内容，我才能回应你～"
        elif intent == "greeting":
            return "你好呀！我是按通用架构实现的模块化智能体～"
        elif intent == "calculate":
            if not key_info:
                return "请输入需要计算的算式，比如‘计算 1+2*3’"
            # 调用计算器工具（内聚到决策层）
            allowed_chars = "0123456789+-*/(). "
            if not all(c in allowed_chars for c in key_info):
                return "计算出错：仅支持数字和+-*/()运算"
            try:
                result = eval(key_info)
                return f"计算结果：{key_info} = {result}"
            except:
                return "计算出错：请检查算式合法性（如 2*(3+4)）"
        elif intent == "check_memory":
            all_memory = memory.get_all_memory()
            return f"我的记忆里有这些内容：{all_memory}" if all_memory else "我还没有任何记忆～"
        elif intent == "clear_memory":
            memory.clear_memory()
            return "记忆已经清空啦！"
        elif intent == "exit":
            return "再见啦！下次再聊～"
        else:
            return "我还没学会处理这个问题，你可以教我呀～"

# ====================== 5. 动作模块（Action） ======================
class AgentAction:
    """动作层：执行决策结果，作用于环境"""
    @staticmethod
    def execute(action_content: str) -> bool:
        """
        执行动作（输出回复），返回是否需要退出
        :param action_content: 决策模块生成的回复内容
        :return: True=退出，False=继续
        """
        print("智能体：", action_content)
        return "再见" in action_content

# ====================== 6. 智能体主类（整合所有模块） ======================
class ModularAgent:
    """智能体主类：整合所有模块，实现完整生命周期"""
    def __init__(self):
        # 按架构初始化模块，建立依赖关系
        self.env = AgentEnvironment()
        self.perception = AgentPerception()
        self.memory = AgentMemory(self.env)
        self.policy = AgentPolicy()
        self.action = AgentAction()

    def run(self):
        """智能体主循环：感知→记忆→决策→动作"""
        print("模块化智能体已启动（按通用架构开发），输入‘结束’退出～")
        while True:
            # 1. 感知环境：获取用户输入
            user_input = self.env.get_user_input()
            
            # 2. 解析输入：提取意图和关键信息
            perception_result = self.perception.parse_input(user_input)
            
            # 3. 更新记忆：将输入纳入状态
            self.memory.add_memory(user_input)
            
            # 4. 决策：生成回复内容
            decision_result = self.policy.make_decision(perception_result, self.memory)
            
            # 5. 执行动作：输出回复，判断是否退出
            is_exit = self.action.execute(decision_result)
            if is_exit:
                break

# 运行智能体
if __name__ == "__main__":
    try:
        agent = ModularAgent()
        agent.run()
    except Exception as e:
        print(f"智能体运行出错：{e}")
        
        

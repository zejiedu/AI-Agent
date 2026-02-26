class SimpleAgent:
    def __init__(self):
        # 智能体的状态（短期记忆）：存储用户输入的历史信息
        self.memory = []

    # 感知+决策（策略模块核心）：处理输入并生成决策
    def think(self, user_input: str) -> str:
        # 感知：将用户输入纳入自身状态（更新记忆）
        self.memory.append(user_input)

        # 决策：基于状态的规则型策略
        if "你好" in user_input:
            return "你好呀！我是你的第一个智能体～"
        elif "记忆" in user_input:
            return f"我记得你说过：{self.memory}"
        elif "结束" in user_input:
            return "再见！下次再聊～"
        else:
            return "我还在学习中，你可以教我更多！"

    # 动作执行：持续交互的主循环
    def run(self):
        print("极简智能体已启动，输入‘结束’退出")
        while True:
            user_input = input("你：").strip()
            if not user_input:  # 补充空输入校验，提升鲁棒性
                print("智能体：请输入有效内容～")
                continue
            response = self.think(user_input)
            print("智能体：", response)
            if "结束" in user_input:
                break

# 运行智能体（规范的入口函数）
if __name__ == "__main__":
    agent = SimpleAgent()
    agent.run()
    

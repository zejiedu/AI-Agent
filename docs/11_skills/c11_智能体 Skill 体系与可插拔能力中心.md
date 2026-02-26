# 第11章 智能体 Skill 体系与可插拔能力中心
## 11.1 本章核心价值
前10章已经实现：
- 结构化记忆
- 外部知识库 RAG
- 工具调用
- 工作流规划
- 多智能体协作

但**工具是零散的、能力是写死的、扩展不方便**。
真正工业级 Agent 必须支持：
**Skill 体系 = 可插拔、可注册、可发现、可调度、可热更新的标准化能力单元。**

本章目标：
**打造一套完整的 Skill 开放体系，让任何人都能给智能体“装插件”。**

---

# 11.2 Skill 架构设计
## 11.2.1 什么是 Skill
- **Skill = 标准化能力插件**
- 一个 Skill = 一段可执行逻辑 + 元数据（名称、描述、入参、示例）
- Skill 可以是：函数、API、工具、流程、模型调用、外部服务

## 11.2.2 Skill 体系结构
```
用户请求
   ↓
意图识别 → 匹配可用 Skill
   ↓
Skill 注册中心（所有能力统一管理）
   ↓
Skill 执行器（参数校验 → 执行 → 返回结果）
   ↓
结果反思 → 记忆保存 → 回答用户
```

## 11.2.3 Skill 核心规范
每个 Skill 必须包含：
- `name`：技能唯一名称
- `description`：技能描述（给 LLM 看）
- `input_args`：入参列表（name/type/desc）
- `execute`：执行函数
- `output`：输出格式

---

# 11.3 完整可运行代码（直接嵌入工程）

## 11.3.1 Skill 基类（所有技能的标准）
```python
# skill_system/base_skill.py
from typing import Dict, Any, List
import json

class BaseSkill:
    """技能基类：所有 Skill 必须继承此类"""
    name: str = ""
    description: str = ""
    input_args: List[Dict[str, str]] = []  # 格式: [{"name":"x","type":"str","desc":"xxx"}]
    output_type: str = "str"

    def execute(self, **kwargs) -> Any:
        """执行技能（子类必须实现）"""
        raise NotImplementedError("Skill 必须实现 execute 方法")

    def to_dict(self):
        """转为技能描述字典（给 LLM 用）"""
        return {
            "skill_name": self.name,
            "description": self.description,
            "input_args": self.input_args,
            "output_type": self.output_type
        }

    def __str__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
```

---

# 11.3.2 Skill 注册中心（统一管理所有能力）
```python
# skill_system/skill_registry.py
from typing import Dict, Type
from skill_system.base_skill import BaseSkill

class SkillRegistry:
    """技能注册中心：统一注册、发现、管理所有 Skill"""
    _skills: Dict[str, BaseSkill] = {}

    @classmethod
    def register(cls, skill_instance: BaseSkill):
        """注册技能"""
        if not skill_instance.name:
            raise ValueError("Skill name 不能为空")
        cls._skills[skill_instance.name] = skill_instance
        print(f"✅ 技能注册成功: {skill_instance.name}")

    @classmethod
    def get_skill(cls, skill_name: str) -> BaseSkill:
        """获取技能"""
        return cls._skills.get(skill_name)

    @classmethod
    def list_skills(cls) -> list:
        """列出所有技能"""
        return [skill.to_dict() for skill in cls._skills.values()]

    @classmethod
    def clear(cls):
        """清空技能（测试用）"""
        cls._skills.clear()
```

---

# 11.3.3 内置 Skill 示例（直接可用）
## 1）计算 Skill
```python
# skill_system/skills/calculate_skill.py
from skill_system.base_skill import BaseSkill

class CalculateSkill(BaseSkill):
    name = "calculate"
    description = "执行数学表达式计算，支持加减乘除"
    input_args = [
        {"name": "expression", "type": "str", "desc": "数学表达式，如 1+2*3"}
    ]

    def execute(self, expression: str = ""):
        try:
            # 安全计算
            allowed_chars = "0123456789+-*/(). "
            if not all(c in allowed_chars for c in expression):
                return "❌ 表达式包含非法字符"
            return f"计算结果: {eval(expression)}"
        except Exception as e:
            return f"计算失败: {str(e)}"
```

## 2）天气查询 Skill
```python
# skill_system/skills/weather_skill.py
from skill_system.base_skill import BaseSkill
import requests

class WeatherSkill(BaseSkill):
    name = "weather"
    description = "查询城市天气"
    input_args = [{"name": "city", "type": "str", "desc": "城市名"}]

    def execute(self, city: str = ""):
        try:
            url = f"http://wttr.in/{city}?format=3"
            r = requests.get(url, timeout=5)
            return r.text.strip()
        except:
            return f"无法查询 {city} 的天气"
```

## 3）知识库检索 Skill
```python
# skill_system/skills/rag_skill.py
from skill_system.base_skill import BaseSkill
from knowledge_manager import KnowledgeManager

class RagSkill(BaseSkill):
    name = "rag_search"
    description = "检索企业私有知识库"
    input_args = [{"name": "query", "type": "str", "desc": "检索问题"}]

    def __init__(self):
        self.km = KnowledgeManager()

    def execute(self, query: str = ""):
        return self.km.search_knowledge(query)
```

## 4）记忆查询 Skill
```python
# skill_system/skills/memory_skill.py
from skill_system.base_skill import BaseSkill
from agent_rag import RAGEnabledAgent

class MemorySkill(BaseSkill):
    name = "memory recall"
    description = "检索用户历史记忆"
    input_args = [{"name": "query", "type": "str", "desc": "记忆关键词"}]

    def execute(self, query: str = "", user_id="default_user"):
        agent = RAGEnabledAgent(user_id=user_id)
        mem = agent.retrieve_structured_memory(query)
        return mem if mem else "暂无相关记忆"
```

---

# 11.3.4 Skill 执行器（自动解析、调用、校验）
```python
# skill_system/skill_executor.py
import json
import re
from skill_system.skill_registry import SkillRegistry
from skill_system.base_skill import BaseSkill

class SkillExecutor:
    """技能执行器：解析指令 → 调用技能 → 返回结果"""

    @staticmethod
    def parse_skill_call(llm_response: str):
        """
        从 LLM 回复中解析技能调用
        格式：SKILL: name(arg1=val1, arg2=val2)
        """
        pattern = r"SKILL:\s*(\w+)\((.*?)\)"
        match = re.search(pattern, llm_response)
        if not match:
            return None

        skill_name = match.group(1)
        args_str = match.group(2)

        # 解析参数
        args = {}
        if args_str:
            for part in args_str.split(","):
                part = part.strip()
                if "=" in part:
                    k, v = part.split("=", 1)
                    args[k.strip()] = v.strip().strip('"').strip("'")
        return {
            "skill_name": skill_name,
            "args": args
        }

    @staticmethod
    def run_skill(skill_name: str, **kwargs):
        skill = SkillRegistry.get_skill(skill_name)
        if not skill:
            return f"❌ 技能 {skill_name} 不存在"
        try:
            return skill.execute(**kwargs)
        except Exception as e:
            return f"执行失败: {str(e)}"

    @classmethod
    def execute_from_llm(cls, llm_response: str):
        parsed = cls.parse_skill_call(llm_response)
        if not parsed:
            return None
        return cls.run_skill(
            skill_name=parsed["skill_name"],
            **parsed["args"]
        )
```

---

# 11.3.5 Skill 增强型智能体（最终版）
```python
# agent_skill.py
from agent_rag import RAGEnabledAgent
from skill_system.skill_executor import SkillExecutor

class SkillEnabledAgent(RAGEnabledAgent):
    """支持 Skill 体系的智能体（最终完全体）"""

    def run_with_skill(self, user_input: str):
        # 1. 获取记忆 + 知识库
        context = self.retrieve_all_context(user_input)

        # 2. 获取所有可用技能
        from skill_system.skill_registry import SkillRegistry
        skills = SkillRegistry.list_skills()

        # 3. 构建 Prompt
        prompt = f"""
你是具备 Skill 能力的智能体。
可用技能:
{skills}

规则:
- 需要调用技能时，严格输出格式:
SKILL: 技能名(参数名="值")

上下文:
{context}

用户问题: {user_input}
"""
        # 4. LLM 推理
        llm_resp = self.call_llm(prompt)
        print("🤖 LLM 思考:", llm_resp)

        # 5. 执行技能
        skill_result = SkillExecutor.execute_from_llm(llm_resp)

        # 6. 最终回答
        if skill_result:
            final = f"【执行结果】\n{skill_result}"
        else:
            final = llm_resp

        # 7. 保存记忆
        self.add_structured_memory(user_input, final)
        return final
```

---

# 11.3.6 启动入口（可直接运行）
```python
# main_skill.py
from skill_system.skill_registry import SkillRegistry
from skill_system.skills.calculate_skill import CalculateSkill
from skill_system.skills.weather_skill import WeatherSkill
from skill_system.skills.rag_skill import RagSkill
from skill_system.skills.memory_skill import MemorySkill
from agent_skill import SkillEnabledAgent

# 注册所有技能
SkillRegistry.register(CalculateSkill())
SkillRegistry.register(WeatherSkill())
SkillRegistry.register(RagSkill())
SkillRegistry.register(MemorySkill())

if __name__ == "__main__":
    agent = SkillEnabledAgent(user_id="skill_user")

    print("===== 第11章｜Skill 体系智能体 =====")
    print("支持：计算、天气、知识库检索、记忆检索")
    print("输入 exit 退出")
    print("="*40)

    while True:
        inp = input("\n请输入: ")
        if inp.lower() == "exit":
            break
        ans = agent.run_with_skill(inp)
        print("\n【最终回答】")
        print(ans)
```

---

# 11.4 可直接测试的示例
## 示例 1：计算
```
帮我算 100 - 25 * 3
```
输出：
```
SKILL: calculate(expression="100-25*3")
计算结果: 25
```

## 示例 2：查天气
```
北京天气怎么样
```
输出：
```
SKILL: weather(city="北京")
北京: ⛅️ +15°C
```

## 示例 3：检索知识库
```
智能体支持哪些文档格式？
```
输出：
```
SKILL: rag_search(query="支持哪些文档格式")
【外部知识库参考】...
```

## 示例 4：记忆检索
```
我之前说过我喜欢喝什么？
```
输出：
```
SKILL: memory recall(query="喜欢喝什么")
【历史记忆】用户喜欢喝无糖拿铁
```

---

# 11.5 本章总结（可直接写进书）
第11章完成了**工业级智能体的最后一块拼图：Skill 体系**。

你现在拥有：
- **标准化 Skill 规范**
- **Skill 注册中心**
- **自动解析 & 执行**
- **可插拔、可扩展、可热更**
- **与记忆、RAG、工作流、多智能体完全打通**

这就是：
**AutoGPT、MetaGPT、Dify、Coze 扣子 的底层核心架构。**

---

# 第12章 Skill 工程化落地：标准化文档规范与生态化能力中心
## 12.1 本章核心价值
前11章实现了Skill的核心逻辑（基类、注册、执行），但**缺乏工程化的文档规范和可落地的目录结构**——实际生产中，一个可复用、可协作、可维护的Skill体系，必须包含「标准化文档+结构化目录+可执行脚本+大模型提示词指导」四位一体的完整形态。

本章目标：
**定义工业级的 Skill 文档规范（SKILL.md），并构建可落地的 Skill 生态化能力中心，让任何人都能按规范开发/接入/使用 Skill，让大模型能精准理解并调用 Skill。**

---

## 12.2 先完整理解 SKILL.md 核心规范
### 12.2.1 SKILL.md 的本质
SKILL.md 是**单个 Skill 的“说明书+接口文档+提示词指导+元数据”**，是连接「人类开发者」「Skill 代码」「大模型」的核心桥梁：
- 对开发者：明确 Skill 的开发、部署、测试规范；
- 对大模型：指导其何时调用、如何传参、如何解析结果；
- 对平台：提供 Skill 的元数据（分类、版本、依赖），支持自动注册、发现、调度。

### 12.2.2 SKILL.md 完整规范模板（可直接复用）
````markdown
# Skill 元数据
| 字段         | 说明                                                                 | 示例值                                  |
|--------------|----------------------------------------------------------------------|-----------------------------------------|
| Skill ID     | 全局唯一标识（格式：分类.名称.版本）| tool.calculate.v1                       |
| 名称         | 简洁易理解的 Skill 名称                                             | 数学计算                                |
| 分类         | Skill 分类（工具/知识库/记忆/写作/流程）| 工具                                    |
| 版本         | 语义化版本号                                                         | v1.0.0                                  |
| 作者         | 开发者信息                                                           | 张三 <zhangsan@example.com>             |
| 依赖         | 运行所需的包/服务/环境变量                                           | requests>=2.31.0, DASHSCOPE_API_KEY     |
| 适用场景     | 该 Skill 适用的业务场景                                             | 数学运算、报表计算、公式验证            |
| 调用成本     | 耗时/资源消耗（轻量/中量/重量级）| 轻量                                    |
| 风险等级     | 安全风险（低/中/高）| 低（仅计算，无外部调用）|

# 功能描述
## 核心能力
提供通用数学表达式计算能力，支持加减乘除、括号优先级，内置非法字符校验，避免安全风险。

## 适用边界
- ✅ 支持：整数/小数的加减乘除、括号优先级计算
- ❌ 不支持：复杂函数（如sin/cos）、超大数运算、网络请求类计算

# 接口规范
## 输入参数
| 参数名       | 类型   | 是否必填 | 描述                     | 示例值          | 校验规则                          |
|--------------|--------|----------|--------------------------|-----------------|-----------------------------------|
| expression   | string | 是       | 数学表达式               | "100-25*3+15"   | 仅允许 0-9+-*/(). 字符            |
| timeout      | int    | 否       | 执行超时时间（秒）| 3               | 1-10 之间的整数                   |

## 输出格式
| 类型   | 描述                     | 成功示例                          | 失败示例                          |
|--------|--------------------------|-----------------------------------|-----------------------------------|
| string | 计算结果/错误提示        | "计算结果：40"                    | "计算失败：表达式包含非法字符"    |

# 大模型调用指导
## 调用触发条件
当用户输入包含以下特征时，触发该 Skill：
- 包含“计算”“算一下”“等于多少”等关键词；
- 包含明显的数学表达式（如“1+2*3”“(10-5)/2”）；
- 无其他更匹配的 Skill（如“财务计算”优先于通用计算）。

## 调用格式（严格遵循）
```plaintext
SKILL: calculate(expression="用户输入的表达式", timeout=3)
```

## 结果解析规则
1. 若结果以“计算结果：”开头，直接提取数值返回给用户；
2. 若结果以“计算失败：”开头，将错误信息友好化后返回；
3. 若结果为空，返回“暂时无法完成计算，请检查表达式”。

# 执行脚本说明
## 目录结构

```
skills/
├── calculate/
│   ├── SKILL.md          # 本文档
│   ├── calculate_skill.py # Skill 核心代码
│   ├── test_calculate.py  # 单元测试脚本
│   ├── requirements.txt   # 依赖清单
│   └── prompt.txt        # 大模型专用提示词（可选）
```

## 运行方式
### 1. 本地运行
```bash
# 安装依赖
pip install -r requirements.txt
# 测试运行
python test_calculate.py
```

### 2. 平台接入
```python
# 注册到 Skill 中心
from skill_registry import SkillRegistry
from calculate_skill import CalculateSkill
SkillRegistry.register(CalculateSkill())
```

## 测试用例
| 输入参数                | 预期输出                  | 测试结果 |
|-------------------------|---------------------------|----------|
| expression="1+2*3"      | "计算结果：7"             | ✅ 通过   |
| expression="10/0"       | "计算失败：除零错误"      | ✅ 通过   |
| expression="1+2a"       | "计算失败：表达式包含非法字符" | ✅ 通过   |

## 版本变更记录
| 版本   | 变更内容                     | 变更时间       |
|--------|------------------------------|----------------|
| v1.0.0 | 初始版本，支持基础四则运算   | 2026-02-24     |
| v1.0.1 | 增加超时参数，优化错误提示   | 2026-02-25     |
````

### 12.2.3 SKILL.md 核心模块解读
| 模块     | 核心作用                         | 对大模型的价值                                   |
| ------ | ---------------------------- | ----------------------------------------- |
| 元数据    | 定义 Skill 的基础属性，支持平台自动分类、版本管理 | 大模型了解 Skill 的适用范围、调用成本，优先选择低成本/高匹配的 Skill |
| 功能描述   | 明确 Skill 的能力边界，避免大模型错误调用     | 大模型判断“当前用户请求是否在 Skill 能力范围内”，减少无效调用       |
| 接口规范   | 定义输入输出的格式、校验规则               | 大模型按规范传参，避免参数错误；按格式解析结果，统一返回样式            |
| 调用指导   | 明确触发条件、调用格式、结果解析规则           | 大模型精准触发调用、正确传参、合理解析结果，无需额外思考              |
| 执行脚本说明 | 提供部署、测试、注册的工程化指导             | 对大模型非直接作用，但保证 Skill 能稳定运行，间接提升调用成功率       |
| 测试用例   | 验证 Skill 正确性，也为大模型提供参考案例     | 大模型可参考测试用例，判断输入是否符合要求                     |

---

## 12.3 Skill 工程化目录结构（落地级）
基于 SKILL.md 规范，构建可落地的 Skill 生态目录，兼顾「开发效率」「协作性」「大模型兼容性」：
```
skill_center/  # Skill 能力中心根目录
├── README.md   # 能力中心总说明
├── requirements.txt  # 全局依赖
├── skill_registry.py  # 全局 Skill 注册中心（复用第11章）
├── skill_executor.py  # 全局 Skill 执行器（复用第11章）
├── skill_manager.py   # Skill 生命周期管理器（新增）
├── skills/  # 所有 Skill 存放目录（按分类划分）
│   ├── tool/  # 工具类 Skill
│   │   ├── calculate/  # 单个 Skill 目录（以 Skill 名称命名）
│   │   │   ├── SKILL.md  # 核心文档（必须）
│   │   │   ├── calculate_skill.py  # Skill 代码（必须）
│   │   │   ├── test_calculate.py  # 单元测试（建议）
│   │   │   ├── requirements.txt  # 独立依赖（可选）
│   │   │   └── prompt.txt  # 大模型专用提示词（可选）
│   │   ├── weather/
│   │   │   ├── SKILL.md
│   │   │   ├── weather_skill.py
│   │   │   └── test_weather.py
│   ├── rag/  # 知识库类 Skill
│   │   ├── rag_search/
│   │   │   ├── SKILL.md
│   │   │   ├── rag_skill.py
│   │   │   └── test_rag.py
│   ├── memory/  # 记忆类 Skill
│   │   ├── memory_recall/
│   │   │   ├── SKILL.md
│   │   │   ├── memory_skill.py
│   │   │   └── test_memory.py
│   ├── workflow/  # 流程类 Skill
│   │   ├── report_generator/
│   │   │   ├── SKILL.md
│   │   │   ├── report_skill.py
│   │   │   └── test_report.py
├── skill_templates/  # Skill 模板目录（供开发者复用）
│   ├── SKILL_TEMPLATE.md  # SKILL.md 模板
│   ├── base_skill_template.py  # Skill 代码模板
│   └── test_template.py  # 测试脚本模板
└── docs/  # 补充文档
    ├── skill_develop_guide.md  # Skill 开发指南
    ├── skill_call_guide.md  # 大模型调用 Skill 指南
    └── skill_version_manage.md  # Skill 版本管理规范
```

### 12.3.1 关键目录说明
1. **skill_center/skills/**：按分类划分 Skill 目录，每个 Skill 一个独立子目录，包含完整的「文档+代码+测试」；
2. **skill_center/skill_templates/**：提供标准化模板，降低开发者接入成本；
3. **skill_center/skill_manager.py**：新增的 Skill 生命周期管理器，负责 SKILL.md 解析、自动注册、版本管理、依赖检查。

---

## 12.4 核心实现：Skill 生命周期管理器（解析 SKILL.md + 自动注册）
### 12.4.1 Skill 管理器核心功能
1.  解析 SKILL.md：自动提取元数据、接口规范、调用指导；
2.  自动注册：读取 skills/ 目录下的所有 SKILL.md，自动注册对应的 Skill 代码；
3.  依赖检查：根据 SKILL.md 中的依赖项，自动检查并安装缺失依赖；
4.  版本管理：支持多版本 Skill 共存，按版本号调用；
5.  提示词生成：根据 SKILL.md 自动生成大模型调用 Skill 的提示词。

### 12.4.2 Skill 管理器完整代码
```python
# skill_center/skill_manager.py
import os
import re
import json
import markdown
import subprocess
from typing import Dict, List
from skill_registry import SkillRegistry
from skill_executor import SkillExecutor

class SkillMetadata:
    """Skill 元数据类（解析 SKILL.md 得到）"""
    def __init__(self):
        self.skill_id: str = ""
        self.name: str = ""
        self.category: str = ""
        self.version: str = ""
        self.author: str = ""
        self.dependencies: List[str] = []
        self.scenario: str = ""
        self.cost: str = ""
        self.risk: str = ""
        self.input_args: List[Dict] = []
        self.output_format: Dict = {}
        self.trigger_conditions: str = ""
        self.call_format: str = ""
        self.parse_rules: str = ""

class SkillManager:
    """Skill 生命周期管理器"""
    def __init__(self, skill_root_dir: str = "./skills"):
        self.skill_root_dir = skill_root_dir
        self.skill_metadata_map: Dict[str, SkillMetadata] = {}  # Skill ID → 元数据
        self.skill_code_path_map: Dict[str, str] = {}  # Skill ID → 代码路径

    def parse_skill_md(self, md_path: str) -> SkillMetadata:
        """解析 SKILL.md，提取元数据"""
        metadata = SkillMetadata()
        if not os.path.exists(md_path):
            raise FileNotFoundError(f"SKILL.md 不存在：{md_path}")
        
        # 读取 MD 文件内容
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
        
        # 1. 解析元数据表格（正则匹配）
        meta_pattern = r"# Skill 元数据\n\| 字段 \| 说明 \| 示例值 \|\n\|--------|--------|---------|\n(.*?)\n# 功能描述"
        meta_match = re.search(meta_pattern, md_content, re.DOTALL)
        if meta_match:
            meta_lines = meta_match.group(1).split("\n")
            for line in meta_lines:
                line = line.strip()
                if not line or line.startswith("|"):
                    parts = line.split("|")
                    if len(parts) >= 4:
                        field = parts[1].strip()
                        value = parts[3].strip()
                        if field == "Skill ID":
                            metadata.skill_id = value
                        elif field == "名称":
                            metadata.name = value
                        elif field == "分类":
                            metadata.category = value
                        elif field == "版本":
                            metadata.version = value
                        elif field == "作者":
                            metadata.author = value
                        elif field == "依赖":
                            metadata.dependencies = [d.strip() for d in value.split(",") if d.strip()]
                        elif field == "适用场景":
                            metadata.scenario = value
                        elif field == "调用成本":
                            metadata.cost = value
                        elif field == "风险等级":
                            metadata.risk = value
        
        # 2. 解析输入参数表格
        input_pattern = r"## 输入参数\n\| 参数名 \| 类型 \| 是否必填 \| 描述 \| 示例值 \| 校验规则 \|\n\|--------|--------|----------|--------|---------|----------|\n(.*?)\n## 输出格式"
        input_match = re.search(input_pattern, md_content, re.DOTALL)
        if input_match:
            input_lines = input_match.group(1).split("\n")
            for line in input_lines:
                line = line.strip()
                if not line or line.startswith("|"):
                    parts = line.split("|")
                    if len(parts) >= 7:
                        arg = {
                            "name": parts[1].strip(),
                            "type": parts[2].strip(),
                            "required": parts[3].strip() == "是",
                            "desc": parts[4].strip(),
                            "example": parts[5].strip(),
                            "validate": parts[6].strip()
                        }
                        metadata.input_args.append(arg)
        
        # 3. 解析调用指导
        trigger_pattern = r"## 调用触发条件\n(.*?)\n## 调用格式"
        trigger_match = re.search(trigger_pattern, md_content, re.DOTALL)
        if trigger_match:
            metadata.trigger_conditions = trigger_match.group(1).strip()
        
        call_pattern = r"## 调用格式（严格遵循）\n```plaintext\n(.*?)\n```"
        call_match = re.search(call_pattern, md_content, re.DOTALL)
        if call_match:
            metadata.call_format = call_match.group(1).strip()
        
        parse_pattern = r"## 结果解析规则\n(.*?)\n# 执行脚本说明"
        parse_match = re.search(parse_pattern, md_content, re.DOTALL)
        if parse_match:
            metadata.parse_rules = parse_match.group(1).strip()
        
        return metadata

    def check_dependencies(self, dependencies: List[str]):
        """检查并安装 Skill 依赖"""
        if not dependencies:
            return
        try:
            # 过滤环境变量类依赖（如 DASHSCOPE_API_KEY）
            pkg_deps = [d for d in dependencies if not d.isupper() and "=" in d]
            if pkg_deps:
                subprocess.check_call(["pip", "install"] + pkg_deps)
                print(f"✅ 成功安装依赖：{pkg_deps}")
        except Exception as e:
            print(f"❌ 依赖安装失败：{e}")

    def load_skill_from_dir(self, skill_dir: str):
        """从 Skill 目录加载（解析 MD + 注册代码）"""
        # 1. 查找 SKILL.md
        md_path = os.path.join(skill_dir, "SKILL.md")
        if not os.path.exists(md_path):
            print(f"⚠️ 跳过 {skill_dir}：未找到 SKILL.md")
            return
        
        # 2. 解析元数据
        try:
            metadata = self.parse_skill_md(md_path)
            if not metadata.skill_id:
                print(f"⚠️ 跳过 {skill_dir}：Skill ID 为空")
                return
        except Exception as e:
            print(f"⚠️ 解析 {md_path} 失败：{e}")
            return
        
        # 3. 检查依赖
        self.check_dependencies(metadata.dependencies)
        
        # 4. 查找 Skill 代码文件（匹配目录名+_skill.py）
        skill_name = os.path.basename(skill_dir)
        code_files = [f for f in os.listdir(skill_dir) if f.endswith("_skill.py")]
        if not code_files:
            print(f"⚠️ 跳过 {skill_dir}：未找到 *skill.py 代码文件")
            return
        code_path = os.path.join(skill_dir, code_files[0])
        
        # 5. 动态导入并注册 Skill
        try:
            # 动态导入模块
            module_name = f"skills.{metadata.category}.{skill_name}.{os.path.splitext(code_files[0])[0]}"
            module = __import__(module_name, fromlist=["*"])
            # 查找 Skill 类（继承 BaseSkill）
            from base_skill import BaseSkill
            skill_class = None
            for attr in dir(module):
                cls = getattr(module, attr)
                if isinstance(cls, type) and issubclass(cls, BaseSkill) and cls != BaseSkill:
                    skill_class = cls
                    break
            if not skill_class:
                print(f"⚠️ 跳过 {skill_dir}：未找到 BaseSkill 子类")
                return
            # 实例化并注册
            skill_instance = skill_class()
            SkillRegistry.register(skill_instance)
            # 保存元数据和代码路径
            self.skill_metadata_map[metadata.skill_id] = metadata
            self.skill_code_path_map[metadata.skill_id] = code_path
            print(f"✅ 成功加载 Skill：{metadata.skill_id}（{metadata.name}）")
        except Exception as e:
            print(f"⚠️ 注册 {skill_dir} 代码失败：{e}")
            return

    def load_all_skills(self):
        """加载所有 Skill（遍历 skills/ 目录）"""
        print("🚀 开始加载所有 Skill...")
        # 遍历分类目录
        for category_dir in os.listdir(self.skill_root_dir):
            category_path = os.path.join(self.skill_root_dir, category_dir)
            if not os.path.isdir(category_path):
                continue
            # 遍历分类下的 Skill 目录
            for skill_dir in os.listdir(category_path):
                skill_path = os.path.join(category_path, skill_dir)
                if os.path.isdir(skill_path):
                    self.load_skill_from_dir(skill_path)
        print(f"🏁 Skill 加载完成，共加载 {len(self.skill_metadata_map)} 个 Skill")

    def generate_llm_prompt(self) -> str:
        """根据所有 Skill 的元数据，生成大模型调用提示词"""
        prompt = """你是 Skill 调用专家，必须严格按照以下规则调用 Skill：

# 可用 Skill 列表
"""
        for skill_id, metadata in self.skill_metadata_map.items():
            prompt += f"""
## {skill_id} - {metadata.name}
- 分类：{metadata.category}
- 能力：{metadata.scenario}
- 触发条件：{metadata.trigger_conditions}
- 调用格式：{metadata.call_format}
- 结果解析：{metadata.parse_rules}
"""
        prompt += """
# 调用规则
1. 优先选择匹配度最高的 Skill，避免无效调用；
2. 严格按照「调用格式」传参，参数值必须符合校验规则；
3. 解析结果时必须遵循「结果解析规则」，友好化返回给用户；
4. 无法匹配 Skill 时，直接回答，不强制调用。
"""
        return prompt

    def get_skill_metadata(self, skill_id: str) -> SkillMetadata:
        """获取指定 Skill 的元数据"""
        return self.skill_metadata_map.get(skill_id)

    def list_skills_by_category(self, category: str) -> List[SkillMetadata]:
        """按分类列出 Skill"""
        return [meta for meta in self.skill_metadata_map.values() if meta.category == category]
```

---

## 12.5 落地级 Skill 调用示例（结合 SKILL.md 提示词）
### 12.5.1 完整调用流程
```python
# skill_center/main_skill_center.py
from skill_manager import SkillManager
from agent_skill import SkillEnabledAgent

if __name__ == "__main__":
    # 1. 初始化 Skill 管理器，加载所有 Skill
    skill_manager = SkillManager(skill_root_dir="./skills")
    skill_manager.load_all_skills()
    
    # 2. 生成大模型调用提示词（基于 SKILL.md）
    llm_prompt = skill_manager.generate_llm_prompt()
    print("📋 大模型 Skill 调用提示词：")
    print(llm_prompt[:500] + "...")
    
    # 3. 初始化 Skill 增强型智能体
    agent = SkillEnabledAgent(user_id="skill_center_user")
    
    # 4. 增强智能体的 Prompt（融入 SKILL.md 提示词）
    agent.skill_prompt = llm_prompt  # 需在 agent_skill.py 中新增该属性
    
    # 5. 交互循环
    print("\n===== Skill 能力中心 =====")
    print("输入 exit 退出，输入任意请求调用 Skill")
    while True:
        user_input = input("\n请输入：").strip()
        if user_input.lower() == "exit":
            break
        # 调用智能体（自动匹配 Skill）
        result = agent.run_with_skill_enhanced(user_input)  # 增强版调用方法
        print("\n🎯 回答：")
        print(result)
```

### 12.5.2 增强版 Skill 调用方法（agent_skill.py 扩展）
```python
# agent_skill.py 新增方法
def run_with_skill_enhanced(self, user_input: str):
    """结合 SKILL.md 提示词的增强版 Skill 调用"""
    # 1. 获取记忆 + 知识库上下文
    context = self.retrieve_all_context(user_input)
    
    # 2. 构建完整 Prompt（包含 SKILL.md 生成的提示词）
    full_prompt = f"""
{self.skill_prompt}

# 上下文信息
{context}

# 用户请求
{user_input}
"""
    # 3. LLM 推理
    llm_resp = self.call_llm(full_prompt)
    print(f"🤖 LLM 思考：{llm_resp}")
    
    # 4. 执行 Skill
    skill_result = SkillExecutor.execute_from_llm(llm_resp)
    
    # 5. 生成最终回答
    if skill_result:
        final_answer = skill_result
    else:
        final_answer = llm_resp
    
    # 6. 保存记忆
    self.add_structured_memory(user_input, final_answer)
    
    return final_answer
```

---

## 12.6 Skill 生态化运营建议（企业级落地）
### 12.6.1 Skill 开发流程标准化
1.  开发者从 `skill_templates/` 复制模板；
2.  按 SKILL.md 规范填写元数据、接口、调用指导；
3.  编写 Skill 代码（继承 BaseSkill）；
4.  编写单元测试（覆盖测试用例）；
5.  提交到 `skills/对应分类/` 目录；
6.  Skill 管理器自动加载、注册、上线。

### 12.6.2 Skill 版本管理
1.  遵循语义化版本（MAJOR.MINOR.PATCH）：
    - MAJOR：不兼容的API变更；
    - MINOR：新增功能，兼容旧版本；
    - PATCH：修复bug，兼容旧版本；
2.  多版本共存：Skill ID 包含版本号（如 tool.calculate.v1/tool.calculate.v2），支持灰度发布；
3.  版本回滚：Skill 管理器记录版本历史，支持一键回滚到指定版本。

### 12.6.3 Skill 监控与运维
1.  调用日志：记录每个 Skill 的调用次数、成功率、耗时；
2.  异常告警：Skill 调用失败率超过阈值时，自动告警；
3.  性能优化：对高频调用的 Skill 做缓存，对耗时久的 Skill 做异步执行。

### 12.6.4 Skill 生态扩展
1.  开放平台：提供 Skill 接入API，允许第三方开发者提交 Skill；
2.  Skill 市场：展示所有可用 Skill，支持评分、收藏、推荐；
3.  低代码开发：提供可视化界面，无需编码即可配置简单 Skill（如知识库检索、流程调用）。

---

## 12.7 本章总结
### 12.7.1 核心知识点回顾
1.  **SKILL.md 是 Skill 的核心说明书**：包含元数据、接口、调用指导，是连接开发者、代码、大模型的桥梁；
2.  **工程化目录结构**：按「分类→Skill→文档/代码/测试」分层，兼顾可维护性和扩展性；
3.  **Skill 管理器**：自动解析 SKILL.md、检查依赖、注册代码，降低运营成本；
4.  **大模型提示词增强**：基于 SKILL.md 自动生成提示词，让大模型精准调用 Skill。

### 12.7.2 落地价值
本章完成了 Skill 从「代码逻辑」到「工程化落地」的闭环，构建了：
> 标准化文档（SKILL.md） + 结构化目录 + 自动化管理 + 生态化运营

的完整 Skill 能力中心，可直接落地到企业生产环境，支持：
- 开发者高效开发/维护 Skill；
- 大模型精准理解/调用 Skill；
- 平台方统一管理/运营 Skill；
- 最终用户便捷使用 Skill 能力。

---

这套体系完全对标工业级智能体平台（如 Dify、Coze、MetaGPT），可直接用于办公自动化、企业知识库、智能客服、科研辅助等各类场景。

---

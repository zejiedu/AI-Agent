# 智能体系统开发指南

版本：0.0.2

从极简智能体demo开始，逐步引入复杂功能，覆盖从基础到高级的智能体系统开发。

## 项目简介



这是一个从基础到高级的智能体（Agent）系统开发教程，涵盖了智能体的核心架构、LLM集成、工具扩展、记忆管理、知识库接入等完整技术栈。项目采用模块化设计，逐步构建从简单规则型智能体到具备外部知识库的高级RAG智能体的完整体系。

## 目录结构

项目按学习路径和功能模块组织，每个目录对应一个核心技术点：


  - [第一章 智能体的架构与工程实现](docs/01_simple_agent_demo/c01-从简单Demo理解智能体.md)

  - [第二章 工程化实现可用的LLM智能体](docs/02_llm_agent._demo/c02_工程化实现可用的LLM智能体.md)

  - [第三章 LLM智能体的长期记忆](docs/03_llm_agent_long_memory/c03_llm_memory.md)

  - [第四章 LLM智能体的工具集成](docs/04_tools/c04_llm_tools.md)

  - [第五章 LLM智能体的搜索能力](docs/05_llm_search/c05_llm_search.md)

  - [第六章 LLM智能体的多步骤规划](docs/06_multi_step/c06_multi_step.md)

  - [第七章 智能体的结构化长期记忆](docs/07_agent_structured_memory/c07_智能体的结构化长期记忆.md)

  - [第八章 智能体外部知识库接入](docs/08_agent_knowledge_system/08_外部知识库接入.md)

  - [第九章 智能体工作流引擎](docs/09_workflow/c09_智能体工作流引擎：条件判断、多步骤规划、子任务自动拆分.md)

  - [第十章 多智能体协作](docs/10_MultiAgent/c10_MultiAgent.md)

  - [第十一章 智能体 Skill 体系与可插拔能力中心](docs/11_skills/c11_智能体%20Skill%20体系与可插拔能力中心.md)

  - [第十二章 Skill 工程化落地](docs/12_SKILL.md/c12_Skill%20工程化落地.md)

  - [第十三章 Model Control Protocol](docs/13_MCP/13_Model%20Control%20Protocol.md)

  - [第十四章 MCP 网关与多技能统一调度](docs/14_mcp_net/c14_MCP%20网关与多技能统一调度.md)

  - [第十五章 MCP 安全、权限与审计体系](docs/15_mcp_safe/c15_MCP%20安全、权限与审计体系.md)

  - [第十六章 智能体UI](docs/16_UI/c16_智能体UI.md)

  - [第十七章 多智能体协作](docs/17_multiAgent2/c17_多智能体协作.md)

  - [第十八章 智能体的现在与未来](docs/18_next_tech/c18_end.md)

## 核心功能模块

### 1. 智能体基础架构
- **最小智能体实现**：基于规则的简单智能体，演示核心架构
- **模块化设计**：环境感知、决策、动作执行三层架构
- **工程化实践**：异常处理、鲁棒性设计

### 2. LLM智能体
- **大语言模型集成**：接入通义千问API
- **Prompt工程**：结构化提示词设计
- **上下文记忆**：多轮对话管理
- **工具调用**：计算器工具集成

### 3. 记忆系统
- **短期记忆**：内存存储对话上下文
- **长期记忆**：JSON文件持久化
- **结构化记忆**：向量数据库+关系型数据库混合存储
- **语义检索**：基于SentenceTransformer的相似度搜索

### 4. 工具扩展
- **计算器工具**：数学表达式计算
- **天气查询**：基于wttr.in API
- **联网搜索**：基于SearXNG开源搜索
- **多工具管理**：统一的工具调用框架

### 5. 任务规划
- **多步骤任务拆解**：复杂任务自动拆分
- **任务执行流程**：顺序执行子步骤
- **工具调用协调**：跨工具任务处理

### 6. 外部知识库
- **多格式文件支持**：PDF、MD、TXT
- **RAG技术**：检索增强生成
- **向量数据库**：ChromaDB持久化存储
- **知识管理**：文档上传、删除、查询

## 技术栈

- **核心语言**：Python 3.11+
- **LLM接口**：通义千问API
- **向量模型**：SentenceTransformer (all-MiniLM-L6-v2)
- **向量数据库**：ChromaDB
- **关系数据库**：SQLite
- **文件解析**：pdfplumber、python-markdown
- **网络请求**：requests
- **其他依赖**：regex、dotenv

## 快速开始

### 环境准备

1. 安装依赖：
```bash
pip install dashscope requests regex json5 sentence-transformers chromadb pdfplumber python-markdown pytesseract
```

2. 配置API密钥：
   - 在代码中替换 `dashscope.api_key = "YOUR_API_KEY"` 为你的通义千问API密钥

### 运行示例

#### 1. 基础智能体
```bash
cd 01_simple_agent_demo
python c01_01_simpleAgent.py
```

#### 2. LLM智能体
```bash
cd 02_llm_agent._demo
python c02_llm_agent.py
```

#### 3. 带长期记忆的智能体
```bash
cd 03_llm_agent_long_memory
python c03_llm_memory.py
```

#### 4. 多工具智能体
```bash
cd 04_tools
python c04_llm_tools.py
```

#### 5. 外部知识库智能体
```bash
cd 08_agent_knowledge_system/c08_agent_knowledge_system
# 先上传文档到知识库
python main.py
```

## 学习路径

1. **基础阶段**：
   - 01_simple_agent_demo - 理解智能体核心架构
   - 02_llm_agent._demo - 掌握LLM集成基础
   - 03_llm_agent_long_memory - 实现长期记忆

2. **进阶阶段**：
   - 04_tools - 学习工具扩展
   - 05_llm_search - 集成搜索能力
   - 06_multi_step - 实现任务规划

3. **高级阶段**：
   - 07_agent_structured_memory - 构建结构化记忆
   - 08_agent_knowledge_system - 接入外部知识库
   - 09_workflow 到 18_next_tech - 前沿技术探索

## 核心概念

### 智能体定义
智能体是**能够感知环境、自主决策、执行动作并持续迭代优化的计算实体**，核心特征为：
```
智能体 = 环境感知 + 自主决策 + 动作执行 + 迭代学习
```

### LLM智能体三要素
1. **Prompt工程**：定义智能体身份和行为规则
2. **上下文记忆**：维护对话历史，避免失忆
3. **工具调用**：扩展LLM能力边界

### RAG技术
检索增强生成（Retrieval-Augmented Generation），通过外部知识库提升LLM回答的准确性和可靠性：
- **知识检索**：从外部知识库获取相关信息
- **知识融合**：将检索结果与用户问题结合
- **生成优化**：基于融合信息生成回答

## 工程化最佳实践

1. **模块化设计**：按功能拆分代码，高内聚低耦合
2. **异常处理**：完善的错误捕获和处理机制
3. **参数校验**：输入验证，避免安全风险
4. **性能优化**：
   - 记忆长度限制，避免上下文过长
   - 批量处理，提升向量入库效率
   - 缓存策略，加速高频记忆访问
5. **安全性**：
   - API密钥管理（建议使用环境变量）
   - 工具调用安全校验
   - 记忆内容脱敏

## 应用场景

- **智能客服**：结合结构化记忆和外部知识库，提供个性化服务
- **任务助手**：多工具协作，完成复杂任务
- **知识管理**：企业内部文档智能问答
- **个人助理**：长期记忆用户偏好，提供个性化建议

## 扩展方向

1. **多模态能力**：支持图片、语音输入
2. **多语言支持**：国际化扩展
3. **分布式部署**：多智能体协同
4. **模型微调**：基于领域数据定制模型
5. **可视化界面**：Web或桌面应用

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，欢迎交流讨论。


<!-- python -m http.server 9000 -->
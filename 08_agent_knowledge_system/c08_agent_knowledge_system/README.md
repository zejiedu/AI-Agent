# 智能体工程：结构化记忆+外部知识库（第7+8章整合版）

## 一、工程介绍
整合《智能体入门》第7章（结构化长期记忆）和第8章（外部知识库接入）的完整可运行工程，实现：
1. 结构化记忆：基于向量库的语义化记忆存储与检索
2. 外部知识库：支持PDF/MD/TXT多格式文档接入
3. RAG增强：记忆+知识库+工具调用+任务规划一体化
4. 工程化：完整异常处理、降级方案、批量操作

## 二、快速开始
### 1. 环境准备
```bash
# 1. 克隆/下载工程
git clone <工程地址>
cd agent_knowledge_system

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置API Key
# 编辑.env文件，添加通义千问API Key（阿里云百炼平台获取）
echo "DASHSCOPE_API_KEY=你的API_KEY" > .env
```

### 2. 运行工程
```bash
python main.py
```

### 3. 基础指令
| 指令 | 说明 |
|------|------|
| exit | 退出程序 |
| list | 查看知识库文档列表 |
| add  | 批量添加demo_docs目录下的测试文档 |
| add ./demo_docs/readme.md | 添加单个文档 |
| del ./demo_docs/readme.md | 删除指定文档 |

### 4. 测试示例
```
# 1. 添加测试文档
请输入指令/问题：add

# 2. 检索知识库
请输入指令/问题：智能体支持哪些格式的文档？

# 3. 结构化记忆
请输入指令/问题：我喜欢喝无糖拿铁
请输入指令/问题：我上次说喜欢喝什么？

# 4. 工具调用
请输入指令/问题：计算1+2*3
请输入指令/问题：查询北京天气
```

## 三、 工程目录结构
```
agent_knowledge_system/
├── README.md                  # 工程说明文档
├── requirements.txt           # 依赖清单
├── .env                       # 环境配置（API Key）
├── config.py                  # 全局配置
├── structured_memory.py       # 第7章：结构化记忆核心
├── document_parser.py         # 第8章：文档解析（PDF/MD/TXT）
├── text_splitter.py           # 第8章：文本分割器
├── vector_db.py               # 向量库扩展（记忆+知识库）
├── knowledge_manager.py       # 第8章：知识库管理器
├── agent_rag.py               # 核心智能体（RAG+记忆+工具）
├── main.py                    # 运行入口
├── demo_docs/                 # 测试文档目录
│   ├── test.pdf
│   ├── readme.md
│   └── notes.txt
├── structured_memory/         # 自动生成：向量库+元数据
│   ├── chroma_db/
│   └── metadata.db
└── basic_memory.json          # 降级用：JSON记忆文件
```
## 二、完整文件内容
### 1. requirements.txt
```txt
# 基础依赖
python>=3.8
dashscope>=1.14.0
requests>=2.31.0
python-dotenv>=1.0.0
retrying>=1.3.4

# 向量库+嵌入模型
chromadb>=0.4.24
sentence-transformers>=2.7.0
numpy>=1.26.4

# 文档解析
pdfplumber>=0.10.3
python-markdown>=3.5.1
pytesseract>=0.3.10  # OCR（可选）
Pillow>=10.2.0       # 图片处理

# 数据库
sqlite3>=2.6.0
```

### 2. .env（需自行配置）
```env
# 通义千问API Key（阿里云百炼平台获取）
DASHSCOPE_API_KEY=your_api_key_here

# 可选：OCR路径（Windows示例）
# TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
```


## 四、核心功能
### 1. 结构化记忆
- 基于ChromaDB的向量存储
- 记忆类型：用户偏好/任务记录/工具结果/上下文
- 自动过期清理、权重动态调整
- 降级方案：向量库失败自动切回JSON存储

### 2. 外部知识库
- 支持格式：PDF/MD/TXT
- 文本分割：语义分割（300-500 token）
- 检索：向量语义检索+元数据筛选
- 批量操作：文件夹批量上传/删除

### 3. RAG增强
- 记忆+知识库双上下文融合
- 强制引用来源，避免编造信息
- 兼容原有工具调用和任务规划能力

## 五、生产环境优化建议
1. **向量库替换**：ChromaDB → Milvus/Qdrant/FAISS
2. **嵌入模型**：all-MiniLM-L6-v2 → 通义千问Embedding API
3. **PDF解析**：扫描版PDF需部署Tesseract OCR
4. **性能优化**：添加Redis缓存、重排序模型（bge-reranker）


## 三、使用说明
### 1. 环境配置
1. 确保Python版本≥3.8
2. 安装依赖：`pip install -r requirements.txt`
3. 配置`.env`文件，添加通义千问API Key（阿里云百炼平台免费获取）

### 2. 运行步骤
1. 执行`python main.py`启动工程
2. 输入`add`自动添加测试文档到知识库
3. 输入问题测试RAG增强能力：
   - 测试记忆：`我喜欢喝无糖拿铁` → 再问`我喜欢喝什么？`
   - 测试知识库：`智能体支持哪些格式的文档？`
   - 测试工具：`计算1+2*3`

### 3. 扩展说明
- 支持自定义文档：将PDF/MD/TXT放入`demo_docs`目录，输入`add`批量添加
- OCR支持：如需解析扫描版PDF，安装Tesseract OCR并开启`OCR_ENABLED=True`

## 四、核心总结
1. 工程完整整合了结构化记忆（第7章）和外部知识库（第8章），代码可直接运行；
2. 支持PDF/MD/TXT多格式文档解析、向量化、检索，具备完整的知识库管理能力；
3. 智能体实现了RAG+结构化记忆+工具调用+任务规划的一体化架构，可直接用于企业私有知识库场景；
4. 包含完善的异常处理、降级方案和工程化设计，兼顾开发便捷性和生产可用性。




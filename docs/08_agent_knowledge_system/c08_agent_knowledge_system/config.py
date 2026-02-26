import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ====================== 基础配置 ======================
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
MAX_BASIC_MEMORY = 100  # 降级用JSON记忆最大条数
MEMORY_FILE_PATH = "./basic_memory.json"

# ====================== 结构化记忆配置 ======================
VECTOR_DB_PATH = "./structured_memory/chroma_db"
SQLITE_DB_PATH = "./structured_memory/metadata.db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 轻量级嵌入模型
TOP_K_MEMORY = 5                      # 记忆检索条数
MEMORY_EXPIRE_DAYS = 90               # 记忆过期天数

# ====================== 外部知识库配置 ======================
TOP_K_KNOWLEDGE = 5                   # 知识库检索条数
MAX_CHUNK_TOKENS = 512                # 文档分段长度
SUPPORTED_FORMATS = [".pdf", ".md", ".txt"]  # 支持的文档格式
OCR_ENABLED = False                   # 是否开启OCR（处理图片PDF）





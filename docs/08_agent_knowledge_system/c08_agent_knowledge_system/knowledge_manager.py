import os
from document_parser import DocumentParserFactory
from structured_memory import VectorMemoryDB
from config import VECTOR_DB_PATH, EMBEDDING_MODEL, SUPPORTED_FORMATS

class KnowledgeManager:
    def __init__(self):
        """外部知识库管理器"""
        self.vector_db = VectorMemoryDB(VECTOR_DB_PATH, EMBEDDING_MODEL)
        self.supported_formats = SUPPORTED_FORMATS

    def add_document(self, file_path: str):
        """添加单个文档到知识库"""
        if not os.path.exists(file_path):
            print(f"文件不存在：{file_path}")
            return False
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.supported_formats:
            print(f"不支持的文件格式：{ext}，支持：{self.supported_formats}")
            return False
        
        try:
            # 获取解析器
            parser = DocumentParserFactory.get_parser(file_path)
            # 解析文档
            document_chunks = parser.parse(file_path)
            if not document_chunks:
                print(f"文档解析无内容：{file_path}")
                return False
            # 入库
            return self.vector_db.add_knowledge_document(file_path, document_chunks)
        except Exception as e:
            print(f"添加文档失败：{e}")
            return False

    def add_batch_documents(self, folder_path: str):
        """批量添加文件夹中的文档"""
        if not os.path.isdir(folder_path):
            print(f"文件夹不存在：{folder_path}")
            return False
        
        success_count = 0
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                ext = os.path.splitext(filename)[1].lower()
                if ext in self.supported_formats:
                    if self.add_document(file_path):
                        success_count += 1
        
        print(f"批量入库完成，成功添加：{success_count} 个文档")
        return True

    def delete_document(self, file_path: str):
        """删除指定文档"""
        return self.vector_db.delete_knowledge_document(file_path)

    def list_documents(self):
        """列出知识库中所有文档"""
        try:
            results = self.vector_db.knowledge_collection.get()
            sources = list(set([meta.get("source", "未知来源") for meta in results["metadatas"]]))
            print("=== 知识库文档列表 ===")
            for idx, s in enumerate(sources, 1):
                print(f"{idx}. {s}")
            return sources
        except Exception as e:
            print(f"获取文档列表失败：{e}")
            return []

    def search_knowledge(self, query: str, top_k: int = 5):
        """检索外部知识库"""
        return self.vector_db.retrieve_knowledge(query, top_k)
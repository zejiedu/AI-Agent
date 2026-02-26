import json
import hashlib
import sqlite3
import os
from datetime import datetime, timedelta
import chromadb
from sentence_transformers import SentenceTransformer
from config import *

# ====================== 元数据数据库类 ======================
class MemoryMetadataDB:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化元数据数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL,
                create_time TEXT NOT NULL,
                user_id TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                expire_time TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def add_metadata(self, content_hash, memory_type, user_id, weight=1.0, expire_days=90):
        """添加记忆元数据"""
        create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expire_time = (datetime.now() + timedelta(days=expire_days)).strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO memory_metadata 
                (content_hash, type, create_time, user_id, weight, expire_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (content_hash, memory_type, create_time, user_id, weight, expire_time))
            conn.commit()
            return True
        except Exception as e:
            print(f"添加元数据失败：{e}")
            return False
        finally:
            conn.close()

    def filter_by_metadata(self, user_id, memory_type=None, days=None):
        """基于元数据筛选记忆哈希"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = '''
            SELECT content_hash FROM memory_metadata 
            WHERE user_id = ? AND expire_time > ?
        '''
        params = [user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        
        if memory_type:
            query += " AND type = ?"
            params.append(memory_type)
        
        if days:
            start_time = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            query += " AND create_time >= ?"
            params.append(start_time)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return [r[0] for r in results]

    def update_weight(self, content_hash, delta=0.1):
        """更新记忆权重"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE memory_metadata 
            SET weight = weight + ? 
            WHERE content_hash = ? AND weight + ? <= 2.0
        ''', (delta, content_hash, delta))
        conn.commit()
        conn.close()

# ====================== 向量数据库类 ======================
class VectorMemoryDB:
    def __init__(self, db_path, embedding_model_name):
        self.use_vector_db = True
        try:
            self.client = chromadb.PersistentClient(path=db_path)
            self.memory_collection = self.client.get_or_create_collection(name="agent_long_term_memory")
            self.knowledge_collection = self.client.get_or_create_collection(name="external_knowledge_base")
            self.embedding_model = SentenceTransformer(embedding_model_name)
        except Exception as e:
            print(f"向量库初始化失败，降级为JSON记忆：{e}")
            self.use_vector_db = False
            self.basic_memory_path = MEMORY_FILE_PATH
            self.max_basic_memory = MAX_BASIC_MEMORY

    def _get_content_hash(self, content):
        """生成内容哈希"""
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    # ---------------- 结构化记忆相关 ----------------
    def add_memory(self, content, metadata_db, user_id, memory_type):
        """添加结构化记忆"""
        if self.use_vector_db:
            content_hash = self._get_content_hash(content)
            embedding = self.embedding_model.encode(content).tolist()
            self.memory_collection.upsert(
                ids=[content_hash],
                embeddings=[embedding],
                documents=[content]
            )
            metadata_db.add_metadata(content_hash, memory_type, user_id)
            return content_hash
        else:
            self._save_basic_memory(content)
            return None

    def _save_basic_memory(self, content):
        """降级：JSON文件存储"""
        if os.path.exists(self.basic_memory_path):
            with open(self.basic_memory_path, "r", encoding="utf-8") as f:
                memories = json.load(f)
        else:
            memories = []
        memories.append({
            "content": content,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        if len(memories) > self.max_basic_memory:
            memories = memories[-self.max_basic_memory:]
        with open(self.basic_memory_path, "w", encoding="utf-8") as f:
            json.dump(memories, f, ensure_ascii=False, indent=2)

    def retrieve_memory(self, query, metadata_db, user_id, memory_type=None, days=None, top_k=5):
        """检索结构化记忆"""
        if not self.use_vector_db:
            return self._retrieve_basic_memory(query)
        
        # 删除过期记忆
        self.delete_expired_memory(metadata_db, user_id)
        
        # 筛选候选哈希
        candidate_hashes = metadata_db.filter_by_metadata(user_id, memory_type, days)
        if not candidate_hashes:
            return []
        
        # 语义检索
        query_embedding = self.embedding_model.encode(query).tolist()
        results = self.memory_collection.query(
            query_embeddings=[query_embedding],
            include=["documents", "distances", "ids"],
            where={"id": {"$in": candidate_hashes}},
            n_results=top_k
        )
        
        # 整理结果
        retrieved_memories = []
        for idx, doc in enumerate(results["documents"][0]):
            memory_id = results["ids"][0][idx]
            distance = results["distances"][0][idx]
            similarity = 1 - distance
            metadata_db.update_weight(memory_id, delta=0.05)
            retrieved_memories.append({
                "content": doc,
                "similarity": round(similarity, 4),
                "memory_id": memory_id
            })
        
        retrieved_memories.sort(key=lambda x: x["similarity"], reverse=True)
        return retrieved_memories

    def _retrieve_basic_memory(self, query):
        """降级：检索JSON记忆"""
        if not os.path.exists(self.basic_memory_path):
            return []
        with open(self.basic_memory_path, "r", encoding="utf-8") as f:
            memories = json.load(f)
        # 简单关键词匹配
        matched = []
        for mem in memories:
            if query in mem["content"]:
                matched.append({
                    "content": mem["content"],
                    "similarity": 1.0,
                    "memory_id": None
                })
        return matched[:TOP_K_MEMORY]

    def delete_expired_memory(self, metadata_db, user_id):
        """删除过期记忆"""
        if not self.use_vector_db:
            return 0
        
        conn = sqlite3.connect(metadata_db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT content_hash FROM memory_metadata 
            WHERE user_id = ? AND expire_time <= ?
        ''', (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        expired_hashes = [r[0] for r in cursor.fetchall()]
        conn.close()
        
        if expired_hashes:
            self.memory_collection.delete(ids=expired_hashes)
        
        conn = sqlite3.connect(metadata_db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM memory_metadata 
            WHERE user_id = ? AND expire_time <= ?
        ''', (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return len(expired_hashes)

    # ---------------- 外部知识库相关 ----------------
    def add_knowledge_document(self, file_path, document_chunks, ocr_enabled=False):
        """添加文档到外部知识库"""
        try:
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for chunk in document_chunks:
                content = chunk["content"]
                metadata = chunk["metadata"]
                # 生成唯一ID
                content_hash = self._get_content_hash(f"{file_path}_{metadata.get('chunk_num', 0)}_{content}")
                # 生成向量
                embedding = self.embedding_model.encode(content).tolist()
                # 收集数据
                ids.append(content_hash)
                embeddings.append(embedding)
                documents.append(content)
                metadatas.append(metadata)
            
            # 批量入库
            self.knowledge_collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            return True
        except Exception as e:
            print(f"知识库入库失败：{e}")
            return False

    def delete_knowledge_document(self, file_path):
        """删除外部知识库中的文档"""
        try:
            results = self.knowledge_collection.get(where={"source": file_path})
            if not results["ids"]:
                print(f"文档不存在于知识库：{file_path}")
                return False
            self.knowledge_collection.delete(ids=results["ids"])
            return True
        except Exception as e:
            print(f"删除文档失败：{e}")
            return False

    def retrieve_knowledge(self, query, top_k=5):
        """检索外部知识库"""
        if not self.use_vector_db:
            return "【外部知识库暂不可用】"
        
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            results = self.knowledge_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # 格式化输出
            knowledge_text = "【外部知识库参考】\n"
            for idx, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][idx]
                source = metadata.get("source", "未知来源")
                page = metadata.get("page_num", "")
                page_info = f" 第{page}页" if page else ""
                knowledge_text += f"{idx+1}. 来源：{os.path.basename(source)}{page_info}\n内容：{doc}\n\n"
            
            return knowledge_text
        except Exception as e:
            print(f"知识库检索失败：{e}")
            return "【外部知识库检索失败】"
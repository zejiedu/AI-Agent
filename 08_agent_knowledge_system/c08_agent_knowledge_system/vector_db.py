# vector_db.py
from structured_memory import VectorMemoryDB
from config import VECTOR_DB_PATH, EMBEDDING_MODEL

def get_external_knowledge_db():
    return VectorMemoryDB(VECTOR_DB_PATH, EMBEDDING_MODEL)
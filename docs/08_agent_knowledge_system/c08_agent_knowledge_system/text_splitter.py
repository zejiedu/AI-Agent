import re
from sentence_transformers import SentenceTransformer
from config import MAX_CHUNK_TOKENS

class TextSplitter:
    def __init__(self, model_name="all-MiniLM-L6-v2", max_chunk_tokens=None, tokenizer=None):
        """
        文本分割器
        :param model_name: 句向量模型名称
        :param max_chunk_tokens: 最大片段token数
        :param tokenizer: 自定义tokenizer
        """
        self.max_chunk_tokens = max_chunk_tokens or MAX_CHUNK_TOKENS
        self.model = SentenceTransformer(model_name)
        self.tokenizer = tokenizer if tokenizer else self.model.tokenizer

    def _split_by_sentences(self, text):
        """按句子分割文本"""
        # 适配中英文标点
        sentence_pattern = r'(?<=[。！？；\.\!\?;])\s*'
        sentences = re.split(sentence_pattern, text)
        # 过滤空句子
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _merge_sentences(self, sentences):
        """合并句子为固定长度片段"""
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_tokens = len(self.tokenizer.encode(sentence))
            # 超过阈值则保存当前片段
            if current_length + sentence_tokens > self.max_chunk_tokens and current_chunk:
                chunks.append("".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_tokens
            else:
                current_chunk.append(sentence)
                current_length += sentence_tokens
        
        # 保存最后一个片段
        if current_chunk:
            chunks.append("".join(current_chunk))
        return chunks

    def split_text(self, text):
        """核心分割方法"""
        if not text or len(text) < 10:
            return []
        # 1. 按句子分割
        sentences = self._split_by_sentences(text)
        if not sentences:
            return []
        # 2. 合并句子
        chunks = self._merge_sentences(sentences)
        # 3. 过滤过短片段
        chunks = [chunk for chunk in chunks if len(chunk) > 10]
        return chunks
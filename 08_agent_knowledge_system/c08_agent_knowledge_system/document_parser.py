import os
import pdfplumber
import markdown
from PIL import Image
import pytesseract
from typing import List, Dict
from text_splitter import TextSplitter
from config import OCR_ENABLED, SUPPORTED_FORMATS

# ====================== PDF解析器 ======================
class PDFParser:
    def __init__(self, ocr_enabled: bool = OCR_ENABLED):
        self.ocr_enabled = ocr_enabled
        self.splitter = TextSplitter()

    def _extract_image_text(self, image) -> str:
        """提取图片中的文字（OCR）"""
        if not self.ocr_enabled:
            return ""
        try:
            return pytesseract.image_to_string(image, lang="chi_sim+eng")
        except Exception as e:
            print(f"OCR解析失败：{e}")
            return ""

    def parse(self, file_path: str) -> List[Dict[str, str]]:
        """解析PDF文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF文件不存在：{file_path}")
        
        chunks = []
        try:
            with pdfplumber.open(file_path) as pdf:
                # 提取元数据
                metadata = {
                    "title": pdf.metadata.get("title", os.path.basename(file_path)),
                    "author": pdf.metadata.get("author", "未知作者"),
                    "total_pages": len(pdf.pages),
                    "format": "PDF",
                    "source": file_path,
                    "doc_type": "external_knowledge"
                }
                # 逐页解析
                for page_num, page in enumerate(pdf.pages, 1):
                    # 提取页面文本
                    page_text = page.extract_text() or ""
                    # 提取页面图片（OCR）
                    if self.ocr_enabled:
                        for img in page.images:
                            try:
                                img_obj = Image.open(img["stream"])
                                img_text = self._extract_image_text(img_obj)
                                page_text += "\n" + img_text
                            except Exception as e:
                                print(f"解析图片失败：{e}")
                    # 分割文本为片段
                    page_chunks = self.splitter.split_text(page_text)
                    # 封装片段
                    for chunk_num, chunk in enumerate(page_chunks, 1):
                        chunks.append({
                            "content": chunk,
                            "metadata": {
                                **metadata,
                                "page_num": page_num,
                                "chunk_num": chunk_num
                            }
                        })
            return chunks
        except Exception as e:
            print(f"PDF解析失败：{e}")
            return []

# ====================== MD/TXT解析器 ======================
class TextParser:
    def __init__(self):
        self.splitter = TextSplitter()

    def parse(self, file_path: str) -> List[Dict[str, str]]:
        """解析MD/TXT文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在：{file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # MD文件处理（保留标题结构）
        if ext == ".md":
            html = markdown.markdown(content)
            # 简单处理：保留原始文本结构
            pass
        
        # 分割文本
        chunks = self.splitter.split_text(content)
        # 封装元数据
        metadata = {
            "title": os.path.basename(file_path),
            "author": "未知作者",
            "format": ext[1:].upper(),
            "source": file_path,
            "doc_type": "external_knowledge"
        }
        
        return [{
            "content": chunk,
            "metadata": {**metadata, "chunk_num": idx+1}
        } for idx, chunk in enumerate(chunks)]

# ====================== 解析器工厂 ======================
class DocumentParserFactory:
    @staticmethod
    def get_parser(file_path: str):
        """根据文件格式获取解析器"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in SUPPORTED_FORMATS:
            raise ValueError(f"不支持的文件格式：{ext}")
        
        if ext == ".pdf":
            return PDFParser()
        else:  # .md/.txt
            return TextParser()
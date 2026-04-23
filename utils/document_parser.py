import os
import logging

logger = logging.getLogger(__name__)

def read_text_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_pdf_file(file_path: str) -> str:
    try:
        import pypdf
        text = ""
        with open(file_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except ImportError:
        logger.error("未安装 pypdf 库")
        return ""
    except Exception as e:
        logger.error(f"解析 PDF 失败: {e}")
        return ""

def read_docx_file(file_path: str) -> str:
    try:
        import docx
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except ImportError:
        logger.error("未安装 python-docx 库")
        return ""
    except Exception as e:
        logger.error(f"解析 Word 失败: {e}")
        return ""

def extract_text_from_file(file_path: str) -> str:
    """
    通用文件文本提取入口。
    支持 .txt, .pdf, .docx
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.txt':
        return read_text_file(file_path)
    elif ext == '.pdf':
        return read_pdf_file(file_path)
    elif ext in ['.doc', '.docx']:
        return read_docx_file(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {ext}。目前仅支持 .txt, .pdf, .docx")

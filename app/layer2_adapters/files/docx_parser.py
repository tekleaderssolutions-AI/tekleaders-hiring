import docx
from typing import Optional

class DocxParser:
    @staticmethod
    def extract_text(file_path: str) -> Optional[str]:
        """
        Step 1: Ingestion - DOCX Parsing using python-docx
        """
        try:
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error parsing DOCX {file_path}: {e}")
            return None

import pdfplumber
from typing import Optional

class PDFParser:
    @staticmethod
    def extract_text(file_path: str) -> Optional[str]:
        """
        Step 1: Ingestion - PDF Parsing using pdfplumber
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join([page.extract_text() or "" for page in pdf.pages])
                return text
        except Exception as e:
            print(f"Error parsing PDF {file_path}: {e}")
            return None

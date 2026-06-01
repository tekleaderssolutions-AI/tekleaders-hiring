import base64
import pdfplumber
from typing import Optional

# OCR threshold: if extracted text is shorter than this, treat as scanned PDF
_OCR_THRESHOLD = 200


class PDFParser:

    @staticmethod
    def extract_text(file_path: str) -> str:
        """Synchronous pdfplumber extraction for text-based PDFs."""
        try:
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            print(f"[PDFParser] pdfplumber failed: {e}")
            return ""

    @staticmethod
    async def extract_text_async(file_path: str, api_key: str = None) -> str:
        """
        Smart extraction:
        1. Try pdfplumber (fast, free, text-based PDFs).
        2. If extracted text < threshold → scanned PDF detected.
        3. Fall back to OCR via OpenAI Vision (gpt-4o-mini) — no Tesseract needed.
        """
        text = PDFParser.extract_text(file_path)
        if len(text.strip()) >= _OCR_THRESHOLD:
            return text

        print(f"[PDFParser] Scanned PDF detected ({len(text.strip())} chars) — running Vision OCR")
        return await PDFParser._ocr_with_vision(file_path, api_key)

    @staticmethod
    async def _ocr_with_vision(file_path: str, api_key: str) -> str:
        """
        Render each PDF page to a PNG image via PyMuPDF, then send to
        GPT-4o-mini Vision to extract text. No Tesseract binary required.
        """
        try:
            import fitz  # pymupdf
        except ImportError:
            print("[PDFParser] pymupdf not installed — OCR unavailable")
            return ""

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=api_key)
            doc = fitz.open(file_path)
            page_texts: list[str] = []

            for page_num, page in enumerate(doc):
                # Render at 150 DPI — good quality without huge memory cost
                mat = fitz.Matrix(150 / 72, 150 / 72)
                pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
                img_b64 = base64.b64encode(pix.tobytes("png")).decode()

                try:
                    resp = await client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "Extract ALL text from this resume page exactly as it appears. "
                                        "Preserve section headers, bullet points, and date ranges. "
                                        "Output only the extracted text — no commentary."
                                    ),
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{img_b64}",
                                        "detail": "high",
                                    },
                                },
                            ],
                        }],
                        max_tokens=2000,
                    )
                    page_texts.append(resp.choices[0].message.content or "")
                except Exception as e:
                    print(f"[PDFParser] Vision OCR page {page_num + 1} failed: {e}")

            doc.close()
            result = "\n\n".join(page_texts)
            print(f"[PDFParser] Vision OCR complete — {len(result)} chars across {len(page_texts)} pages")
            return result

        except Exception as e:
            print(f"[PDFParser] Vision OCR failed: {e}")
            return ""

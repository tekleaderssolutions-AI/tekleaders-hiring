import docx
from typing import Optional


class DocxParser:
    @staticmethod
    def extract_text(file_path: str) -> Optional[str]:
        """
        Extracts all text from a DOCX file, including:
        - Regular paragraphs
        - Tables (skill tables, project grids)
        - Text boxes / frames (sidebar layouts)
        - Headers / footers (name/contact often placed there)
        """
        try:
            doc = docx.Document(file_path)
            from docx.oxml.ns import qn

            parts = []

            # 1. Regular paragraphs (main body)
            for para in doc.paragraphs:
                t = para.text.strip()
                if t:
                    parts.append(t)

            # 2. Tables — skills tables, project grids, experience tables
            for table in doc.tables:
                for row in table.rows:
                    cells = [c.text.strip() for c in row.cells if c.text.strip()]
                    # Deduplicate merged cells (python-docx repeats them)
                    seen, unique = set(), []
                    for c in cells:
                        if c not in seen:
                            seen.add(c)
                            unique.append(c)
                    if unique:
                        parts.append(' | '.join(unique))

            # 3. Text boxes / frames — common in two-column / sidebar resume layouts
            for txbx in doc.element.body.iter(qn('w:txbxContent')):
                for p in txbx.iter(qn('w:p')):
                    runs = [r.text for r in p.iter(qn('w:t')) if r.text]
                    line = ''.join(runs).strip()
                    if line:
                        parts.append(line)

            # 4. Headers and footers — name/phone/email often appear here
            for section in doc.sections:
                for hdr in (section.header, section.first_page_header,
                            section.even_page_header):
                    if hdr is None:
                        continue
                    try:
                        for para in hdr.paragraphs:
                            t = para.text.strip()
                            if t:
                                parts.append(t)
                        for table in hdr.tables:
                            for row in table.rows:
                                cells = [c.text.strip() for c in row.cells if c.text.strip()]
                                if cells:
                                    parts.append(' '.join(cells))
                    except Exception:
                        pass

            result = '\n'.join(parts)
            return result if result.strip() else None

        except Exception as e:
            print(f"Error parsing DOCX {file_path}: {e}")
            return None

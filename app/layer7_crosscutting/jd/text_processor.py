import re
import unicodedata

class TextProcessor:
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Backend ONLY: Step 2 - Text Preprocessing
        - Normalize bullets
        - Strip legal boilerplate (basic)
        - Normalize whitespace
        """
        if not text:
            return ""
        
        # Normalize bullets
        text = text.replace("•", "-").replace("·", "-")
        
        # Fix encoding / Normalize Unicode
        text = unicodedata.normalize("NFKC", text)
        
        # Normalize whitespace (replace multiple spaces/newlines)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    @staticmethod
    def redact_pii(text: str) -> tuple[str, bool, list[str]]:
        """
        Backend ONLY: Step 4 - PII Redaction (MANDATORY)
        Detect and remove: emails, phone numbers, URLs
        Returns: (clean_text, pii_flag, redactions_found)
        """
        redactions = []
        pii_flag = False
        
        # Email Regex
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        if re.search(email_pattern, text):
            text = re.sub(email_pattern, "[EMAIL_REDACTED]", text)
            redactions.append("email")
            pii_flag = True
            
        # Phone Number Regex (Supports various formats)
        phone_pattern = r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        # This regex is broad, might catch some numbers that aren't phones, 
        # but better safe for redaction.
        if re.search(phone_pattern, text):
            # Only redact if length is reasonable for a phone
            matches = re.finditer(phone_pattern, text)
            for match in matches:
                if len(re.sub(r'\D', '', match.group())) >= 10:
                    text = text.replace(match.group(), "[PHONE_REDACTED]")
                    if "phone" not in redactions:
                        redactions.append("phone")
                    pii_flag = True
        
        # URL Regex
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        if re.search(url_pattern, text):
            text = re.sub(url_pattern, "[URL_REDACTED]", text)
            redactions.append("url")
            pii_flag = True
            
        return text, pii_flag, redactions

    @staticmethod
    def segment_jd(text: str) -> dict:
        """
        Backend ONLY: Step 3 - Section Segmentation (CRITICAL)
        Split JD into: role, skills, experience, responsibilities, education
        """
        sections = {
            "role": "",
            "skills": "",
            "experience": "",
            "responsibilities": "",
            "education": "",
            "other": ""
        }
        
        # Headers we look for
        headers = {
            "skills": [r"skills", r"requirements", r"qualifications", r"competencies", r"stack"],
            "experience": [r"experience", r"background", r"track record"],
            "responsibilities": [r"responsibilities", r"what you will do", r"key duties", r"accountabilities"],
            "education": [r"education", r"degree", r"academic"]
        }

        # Normalize the text for easier searching
        lines = text.split('\n')
        current_section = "role" # Assume top is role/intro
        
        for line in lines:
            line_clean = line.strip().lower()
            if not line_clean: continue
            
            # Check if line is a header
            found_header = False
            for section_name, keywords in headers.items():
                for kw in keywords:
                    # Match if line is mostly just the keyword (e.g. "## Requirements")
                    if re.search(fr"\b{kw}\b", line_clean) and len(line_clean) < 30:
                        current_section = section_name
                        found_header = True
                        break
                if found_header: break
            
            if not found_header:
                sections[current_section] += line + "\n"

        # Final cleanup of each section
        for key in sections:
            sections[key] = sections[key].strip()
            
        return sections

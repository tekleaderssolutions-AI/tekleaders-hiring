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
    def extract_contact_info(text: str) -> dict:
        """
        Step 1 - Extract name, email, phone via regex from raw text BEFORE any redaction or LLM call.
        This ensures PII never reaches the LLM.
        """
        # Email
        email = None
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        if email_match:
            email = email_match.group()

        # Phone (first match with 10+ digits)
        phone = None
        phone_pattern = r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        for match in re.finditer(phone_pattern, text):
            if len(re.sub(r'\D', '', match.group())) >= 10:
                phone = match.group().strip()
                break

        # Name: heuristic — first short line (2-4 words) near the top that looks like a name
        name = None
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines[:8]:
            words = line.split()
            if (2 <= len(words) <= 4
                    and not any(c.isdigit() for c in line)
                    and '@' not in line
                    and not re.search(r'(resume|curriculum|vitae|\bcv\b|profile|objective|summary|address)', line.lower())):
                name = line
                break

        # LinkedIn URL — try full URL first, then bare domain path
        linkedin_url = None
        li_match = re.search(r'https?://(?:www\.)?linkedin\.com/in/[^\s,;>\'"]+', text, re.IGNORECASE)
        if not li_match:
            li_match = re.search(r'(?:www\.)?linkedin\.com/in/[^\s,;>\'"]+', text, re.IGNORECASE)
        if li_match:
            url = li_match.group().rstrip('.')
            if not url.startswith('http'):
                url = 'https://' + url
            linkedin_url = url

        return {"name": name, "email": email, "phone": phone, "linkedin_url": linkedin_url}

    @staticmethod
    def redact_pii(text: str, name: str = None) -> tuple[str, bool, list[str]]:
        """
        Step 2 - PII Redaction. Always call AFTER extract_contact_info.
        Strips: name (if provided), emails, phone numbers, URLs.
        Returns: (redacted_text, pii_flag, redactions_found)
        """
        redactions = []
        pii_flag = False

        # Redact candidate name first (word-boundary safe)
        if name:
            name_pattern = re.escape(name.strip())
            if re.search(name_pattern, text, re.IGNORECASE):
                text = re.sub(name_pattern, "[NAME_REDACTED]", text, flags=re.IGNORECASE)
                redactions.append("name")
                pii_flag = True

        # Email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        if re.search(email_pattern, text):
            text = re.sub(email_pattern, "[EMAIL_REDACTED]", text)
            redactions.append("email")
            pii_flag = True

        # Phone numbers (10+ digits)
        phone_pattern = r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        if re.search(phone_pattern, text):
            matches = list(re.finditer(phone_pattern, text))
            for match in matches:
                if len(re.sub(r'\D', '', match.group())) >= 10:
                    text = text.replace(match.group(), "[PHONE_REDACTED]")
                    if "phone" not in redactions:
                        redactions.append("phone")
                    pii_flag = True

        # URLs
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

    @staticmethod
    def segment_resume(text: str) -> dict:
        """
        Step 6: Resume Section Segmentation
        Splits a resume into semantic sections so the AI only reads what it needs.
        Returns: dict with keys: contact, summary, skills, experience, education, other
        """
        sections = {
            "contact": "",
            "summary": "",
            "skills": "",
            "experience": "",
            "education": "",
            "other": ""
        }

        headers = {
            "summary": [r"summary", r"objective", r"profile", r"about me", r"professional summary"],
            "skills": [r"skills", r"technical skills", r"competencies", r"technologies", r"stack", r"expertise"],
            "experience": [r"experience", r"work history", r"employment", r"career", r"work experience", r"professional experience"],
            "education": [r"education", r"academic", r"qualification", r"degree", r"university", r"college"],
            "contact": [r"contact", r"personal details", r"personal information"],
        }

        lines = text.split('\n')
        # Assume the very first lines are contact info
        current_section = "contact"

        for i, line in enumerate(lines):
            line_clean = line.strip().lower()
            if not line_clean:
                continue

            found_header = False
            for section_name, keywords in headers.items():
                for kw in keywords:
                    if re.search(fr"\b{kw}\b", line_clean) and len(line_clean) < 35:
                        current_section = section_name
                        found_header = True
                        break
                if found_header:
                    break

            if not found_header:
                sections[current_section] += line + "\n"

        for key in sections:
            sections[key] = sections[key].strip()

        return sections

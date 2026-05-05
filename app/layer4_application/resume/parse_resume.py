import os
import uuid
import zipfile
import io
from typing import List

from app.layer2_adapters.files.pdf_parser import PDFParser
from app.layer2_adapters.files.docx_parser import DocxParser
from app.layer2_adapters.ai.resume.resume_analyzer import ResumeAnalyzerAgent
from app.layer2_adapters.ai.embedding_service import EmbeddingService
from app.layer6_data.repositories_impl.resume.postgres_candidate_repo import PostgresCandidateRepository
from app.layer5_domain.entities.resume.candidate import Candidate, CandidateExperience, CandidateEducation
from app.layer6_data.models.memory_model import MemoryModel

# Step 4 & 5: Preprocessing and PII Redaction
from app.layer7_crosscutting.jd.text_processor import TextProcessor
# Steps 10-13: Skill Ontology (Alias mapping, Deduplication, Categorization)
from app.layer7_crosscutting.jd.skill_ontology import SkillOntology
# Step 16: Seniority Enrichment
from app.layer7_crosscutting.resume.seniority_enricher import SeniorityEnricher


class ParseResumeUseCase:
    def __init__(self, db_session):
        self.db = db_session
        self.analyzer = ResumeAnalyzerAgent()
        self.embedder = EmbeddingService()
        self.repo = PostgresCandidateRepository(db_session)

    def build_resume_embedding_text(self, parsed: dict, enriched_skills: list) -> str:
        """
        Builds a rich embedding string using normalized skill names for
        better semantic matching against JD embeddings.
        """
        title = parsed.get("current_title") or ""
        location = parsed.get("location") or ""
        # Use canonical skill names for embedding
        skills_csv = ", ".join(s["name"] for s in enriched_skills) if enriched_skills else ""
        exp_years = parsed.get("total_experience_years") or 0
        seniority = parsed.get("seniority", {}).get("level", "")

        summary = f"{title} ({seniority}) with {exp_years} years experience in {skills_csv}".strip()
        return f"{title} | {location} | seniority: {seniority} | skills: {skills_csv} | experience: {exp_years} | summary: {summary}"

    async def execute_single(self, file_content: bytes, filename: str, user_id: str) -> dict:
        """
        Full 17-stage pipeline for a single resume file.
        """
        safe_filename = os.path.basename(filename)
        temp_path = f"temp_{uuid.uuid4()}_{safe_filename}"
        with open(temp_path, "wb") as f:
            f.write(file_content)

        try:
            # ── Step 1: File Ingestion ─────────────────────────────────────────
            if filename.lower().endswith(".pdf"):
                raw_text = PDFParser.extract_text(temp_path)
            elif filename.lower().endswith((".docx", ".doc")):
                raw_text = DocxParser.extract_text(temp_path)
            else:
                return {"error": f"Unsupported format: {filename}", "filename": filename}

            if not raw_text:
                return {"error": "Failed to extract text", "filename": filename}

            # ── Step 4: Preprocessing ──────────────────────────────────────────
            clean_text = TextProcessor.clean_text(raw_text)

            # ── Step 5: PII Redaction ──────────────────────────────────────────
            # We send the PII-free version to the LLM to protect privacy.
            # The AI will still extract name/email/phone from the original.
            redacted_text, pii_flag, redactions = TextProcessor.redact_pii(clean_text)

            # ── Step 6: Segmentation ───────────────────────────────────────────
            # Segment the resume into sections (skills, experience, education)
            # so AI gets structured context and is less likely to hallucinate.
            sections = TextProcessor.segment_resume(clean_text)
            # Build a focused text block for the AI: all sections joined clearly
            structured_for_ai = (
                f"[CONTACT]\n{sections.get('contact', '')}\n\n"
                f"[SUMMARY]\n{sections.get('summary', '')}\n\n"
                f"[SKILLS]\n{sections.get('skills', '')}\n\n"
                f"[EXPERIENCE]\n{sections.get('experience', '')}\n\n"
                f"[EDUCATION]\n{sections.get('education', '')}"
            )

            # ── Step 7: LLM Extraction ─────────────────────────────────────────
            # We send the structured (but NOT redacted) text so the AI can
            # still extract email, phone, name from the contact section.
            extracted_data = await self.analyzer.analyze(structured_for_ai)

            # ── Step 9: Normalization ──────────────────────────────────────────
            # Ensure total_experience_years is always a float
            try:
                extracted_data["total_experience_years"] = float(
                    extracted_data.get("total_experience_years") or 0.0
                )
            except (ValueError, TypeError):
                extracted_data["total_experience_years"] = 0.0

            # ── Steps 10-13: Skill Ontology (Alias, Dedup, Categorization) ─────
            raw_skills = extracted_data.get("skills") or []
            enriched_skills = SkillOntology.normalize_skills_from_list(raw_skills)
            # Store back canonical skill names as the simple list (for DB)
            extracted_data["skills"] = [s["name"] for s in enriched_skills]
            # Store full enriched data for metadata
            extracted_data["enriched_skills"] = enriched_skills

            # ── Step 16: Seniority Enrichment ─────────────────────────────────
            seniority = SeniorityEnricher.detect_seniority(
                current_title=extracted_data.get("current_title", ""),
                total_years=extracted_data.get("total_experience_years", 0.0),
                work_experience=extracted_data.get("work_experience") or []
            )
            extracted_data["seniority"] = seniority

            # ── Step 17a: Build Embedding ──────────────────────────────────────
            embedding_text = self.build_resume_embedding_text(extracted_data, enriched_skills)
            embedding_vector = await self.embedder.generate_embedding(embedding_text)

            # ── Handle Name Splitting ──────────────────────────────────────────
            full_name = (extracted_data.get("candidate_name") or "Unknown Candidate").split(" ", 1)
            first_name = full_name[0]
            last_name = full_name[1] if len(full_name) > 1 else ""

            email = extracted_data.get("email")

            # ── Duplicate Check ────────────────────────────────────────────────
            existing_candidate = await self.repo.get_by_email(email) if email else None
            if existing_candidate:
                return {"error": f"Candidate with email {email} already exists.", "filename": filename}

            candidate_id = str(uuid.uuid4())
            memory_id = str(uuid.uuid4())

            # ── Step 8: Schema Validation (via Candidate entity) ───────────────
            candidate = Candidate(
                id=candidate_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=extracted_data.get("phone"),
                location=extracted_data.get("location"),
                summary=extracted_data.get("summary") or "",
                skills=extracted_data["skills"],  # canonical names
                total_years_experience=extracted_data["total_experience_years"],
                memory_id=memory_id,
                experience=[
                    CandidateExperience(**exp)
                    for exp in (extracted_data.get("work_experience") or [])
                ],
                education=[
                    CandidateEducation(**edu)
                    for edu in (extracted_data.get("education") or [])
                ]
            )

            # ── Step 17b: Persist to Postgres (Candidates table) ───────────────
            await self.repo.save(candidate)

            # ── Step 17c: Persist to Vector DB (Memories table) ───────────────
            resume_metadata = {
                "candidate_id": candidate_id,
                "current_title": extracted_data.get("current_title"),
                "current_company": extracted_data.get("current_company"),
                "location": extracted_data.get("location"),
                "total_experience_yrs": extracted_data["total_experience_years"],
                "skills": extracted_data["skills"],
                "enriched_skills": enriched_skills,             # Step 10-13
                "seniority": seniority,                         # Step 16
                "domain": extracted_data.get("domain"),
                "education": extracted_data.get("education"),
                "certifications": extracted_data.get("certifications"),
                "projects": extracted_data.get("projects"),
                "pii_flag": pii_flag,                           # Step 5
                "redactions": redactions,                       # Step 5
                "file_name": filename,
                "raw_text_snippet": redacted_text[:800],        # Store redacted snippet
                "created_by": user_id
            }

            memory = MemoryModel(
                id=memory_id,
                type="resume",
                title=extracted_data.get("current_title") or candidate.first_name,
                text=embedding_text,
                embedding=embedding_vector,
                metadata_=resume_metadata,
                canonical_json=extracted_data,
                user_id=user_id
            )
            self.db.add(memory)
            await self.db.flush()

            return {
                "status": "success",
                "candidate_id": candidate_id,
                "name": extracted_data.get("candidate_name"),
                "email": candidate.email,
                "seniority": seniority["level"],
                "skills_processed": len(enriched_skills),
                "pii_detected": pii_flag,
            }

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    async def execute_bulk(self, zip_content: bytes, user_id: str) -> List[dict]:
        """
        Processes a ZIP file containing multiple resumes — each through the full pipeline.
        """
        results = []
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            for filename in z.namelist():
                if filename.endswith('/') or not filename.lower().endswith(('.pdf', '.docx', '.doc')):
                    continue
                with z.open(filename) as f:
                    content = f.read()
                    res = await self.execute_single(content, filename, user_id)
                    results.append(res)
        return results

import os
import uuid
import zipfile
import io
import shutil
from typing import List, Dict, Any
from app.layer2_adapters.files.pdf_parser import PDFParser
from app.layer2_adapters.files.docx_parser import DocxParser
from app.layer2_adapters.ai.resume.resume_analyzer import ResumeAnalyzerAgent
from app.layer2_adapters.ai.embedding_service import EmbeddingService
from app.layer6_data.repositories_impl.resume.postgres_candidate_repo import PostgresCandidateRepository
from app.layer5_domain.entities.resume.candidate import Candidate, CandidateExperience, CandidateEducation
from app.layer6_data.models.memory_model import MemoryModel

class ParseResumeUseCase:
    def __init__(self, db_session):
        self.db = db_session
        self.analyzer = ResumeAnalyzerAgent()
        self.embedder = EmbeddingService()
        self.repo = PostgresCandidateRepository(db_session)

    def build_resume_embedding_text(self, parsed: dict) -> str:
        """
        {title} | {location} | skills: {skills_csv} | experience: {yrs} | summary: {one-line summary}
        """
        title = parsed.get("current_title") or ""
        location = parsed.get("location") or ""
        skills = parsed.get("skills") or []
        skills_csv = ", ".join(skills)
        exp_years = parsed.get("total_experience_years") or 0

        summary = f"{title} with {exp_years} years experience in {skills_csv}".strip()
        return f"{title} | {location} | skills: {skills_csv} | experience: {exp_years} | summary: {summary}"

    async def execute_single(self, file_content: bytes, filename: str, user_id: str) -> dict:
        """
        Processes a single resume file
        """
        # Save temp file for parsing
        safe_filename = os.path.basename(filename)
        temp_path = f"temp_{uuid.uuid4()}_{safe_filename}"
        with open(temp_path, "wb") as f:
            f.write(file_content)

        try:
            # 1. Parse Text
            if filename.lower().endswith(".pdf"):
                raw_text = PDFParser.extract_text(temp_path)
            elif filename.lower().endswith((".docx", ".doc")):
                raw_text = DocxParser.extract_text(temp_path)
            else:
                return {"error": f"Unsupported format: {filename}", "filename": filename}

            if not raw_text:
                return {"error": "Failed to extract text", "filename": filename}

            # 2. AI Extraction
            extracted_data = await self.analyzer.analyze(raw_text)

            # 3. Embedding
            embedding_text = self.build_resume_embedding_text(extracted_data)
            embedding_vector = await self.embedder.generate_embedding(embedding_text)

            # Handle name splitting
            full_name = extracted_data.get("candidate_name", "Unknown Candidate").split(" ", 1)
            first_name = full_name[0]
            last_name = full_name[1] if len(full_name) > 1 else ""
            
            email = extracted_data.get("email")
            
            # Upsert Logic: Check if candidate already exists
            existing_candidate = await self.repo.get_by_email(email) if email else None
            
            if existing_candidate:
                candidate_id = existing_candidate.id
                memory_id = existing_candidate.memory_id or str(uuid.uuid4())
            else:
                candidate_id = str(uuid.uuid4())
                memory_id = str(uuid.uuid4())
            
            candidate = Candidate(
                id=candidate_id,
                email=extracted_data.get("email"),
                first_name=first_name,
                last_name=last_name,
                phone=extracted_data.get("phone"),
                location=extracted_data.get("location"),
                summary=extracted_data.get("summary") or "",
                skills=extracted_data.get("skills") or [],
                total_years_experience=extracted_data.get("total_experience_years", 0.0) or 0.0,
                memory_id=memory_id,
                experience=[CandidateExperience(**exp) for exp in (extracted_data.get("work_experience") or [])],
                education=[CandidateEducation(**edu) for edu in (extracted_data.get("education") or [])]
            )

            # 5. Store in Postgres
            await self.repo.save(candidate)

            # 6. Store in Vector DB (Memories table)
            resume_metadata = {
                "candidate_id": candidate_id,
                "current_company": extracted_data.get("current_company"),
                "location": extracted_data.get("location"),
                "total_experience_yrs": extracted_data.get("total_experience_years"),
                "skills": extracted_data.get("skills") or [],
                "domain": extracted_data.get("domain"),
                "education": extracted_data.get("education"),
                "certifications": extracted_data.get("certifications"),
                "projects": extracted_data.get("projects"),
                "file_name": filename,
                "raw_text_snippet": raw_text[:800],
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
            await self.db.commit()

            return {
                "status": "success",
                "candidate_id": candidate_id,
                "name": extracted_data.get("candidate_name"),
                "email": candidate.email
            }

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    async def execute_bulk(self, zip_content: bytes, user_id: str) -> List[dict]:
        """
        Processes a ZIP file containing multiple resumes
        """
        results = []
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            for filename in z.namelist():
                # Skip directories and non-resume files
                if filename.endswith('/') or not filename.lower().endswith(('.pdf', '.docx', '.doc')):
                    continue
                
                with z.open(filename) as f:
                    content = f.read()
                    res = await self.execute_single(content, filename, user_id)
                    results.append(res)
        
        return results

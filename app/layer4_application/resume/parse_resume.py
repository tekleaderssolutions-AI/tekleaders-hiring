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
            skills_list = extracted_data.get("skills") or []
            summary_text = extracted_data.get("summary") or ""
            
            embedding_text = f"{extracted_data.get('first_name')} {extracted_data.get('last_name')} | skills: {', '.join(skills_list)} | summary: {summary_text}"
            embedding_vector = await self.embedder.generate_embedding(embedding_text)

            # 4. Create Candidate Entity
            candidate_id = str(uuid.uuid4())
            memory_id = str(uuid.uuid4())
            
            candidate = Candidate(
                id=candidate_id,
                email=extracted_data.get("email"),
                first_name=extracted_data.get("first_name"),
                last_name=extracted_data.get("last_name"),
                phone=extracted_data.get("phone"),
                location=extracted_data.get("location"),
                summary=summary_text,
                skills=skills_list,
                total_years_experience=extracted_data.get("total_years_experience", 0.0) or 0.0,
                memory_id=memory_id,
                experience=[CandidateExperience(**exp) for exp in (extracted_data.get("experience") or [])],
                education=[CandidateEducation(**edu) for edu in (extracted_data.get("education") or [])]
            )

            # 5. Store in Postgres
            await self.repo.save(candidate)

            # 6. Store in Vector DB (Memories table)
            memory = MemoryModel(
                id=memory_id,
                type="resume",
                title=f"{candidate.first_name} {candidate.last_name}",
                text=embedding_text,
                embedding=embedding_vector,
                metadata={
                    "candidate_id": candidate_id,
                    "email": candidate.email,
                    "skills": candidate.skills,
                    "created_by": user_id
                }
            )
            self.db.add(memory)
            await self.db.commit()

            return {
                "status": "success",
                "candidate_id": candidate_id,
                "name": f"{candidate.first_name} {candidate.last_name}",
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

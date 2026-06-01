import os
import uuid
import hashlib
import time
from typing import List, Optional, Any
from datetime import datetime
from sqlalchemy import select

from app.layer2_adapters.files.pdf_parser import PDFParser
from app.layer2_adapters.files.docx_parser import DocxParser
from app.layer2_adapters.ai.resume.resume_analyzer import ResumeAnalyzerAgent
from app.layer2_adapters.ai.embedding_service import EmbeddingService
from app.layer6_data.repositories_impl.resume.postgres_candidate_repo import PostgresCandidateRepository

# Models
from app.layer6_data.models.resume.resume_model import ResumeModel
from app.layer6_data.models.memory_model import MemoryModel
from app.layer6_data.models.agent_model import AgentRunModel, AgentStepModel
from app.layer6_data.models.user_model import UserModel

# Services
from app.layer7_crosscutting.jd.text_processor import TextProcessor
from app.layer7_crosscutting.jd.skill_ontology import SkillOntology
from app.layer7_crosscutting.resume.seniority_enricher import SeniorityEnricher

class ParseResumeUseCase:
    """
    ELITE PIPELINE v3
    Priority 3: Resumable Stage Tracking & Fault Tolerance.
    Ensures 17-stage ingestion is idempotent and cost-efficient.
    """
    def __init__(self, db_session):
        self.db = db_session
        self.analyzer = ResumeAnalyzerAgent()
        self.embedder = EmbeddingService()
        self.repo = PostgresCandidateRepository(db_session)
        self.embedding_model = "text-embedding-3-small"
        self.embedding_version = "1.0"

    def calculate_content_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    async def _get_or_run_step(self, run_id: str, step_name: str, task_fn: callable, input_data: Any = None):
        """
        PRIORITY 3: Checkpoint Manager.
        If the step was already completed, skip execution and return the previous output.
        """
        res = await self.db.execute(
            select(AgentStepModel)
            .where(AgentStepModel.run_id == run_id)
            .where(AgentStepModel.step_name == step_name)
            .where(AgentStepModel.status == "completed")
            .limit(1)
        )
        existing_step = res.scalar_one_or_none()
        
        if existing_step:
            return existing_step.output_data

        # Execute the task
        t0 = time.time()
        output_data = await task_fn()
        latency = (time.time() - t0) * 1000
        
        step = AgentStepModel(
            id=str(uuid.uuid4()), run_id=run_id, step_name=step_name,
            input_data=input_data, output_data=output_data, status="completed", latency_ms=latency
        )
        self.db.add(step)
        await self.db.flush()
        return output_data

    async def execute_single(self, file_content: bytes, filename: str, user_id: str) -> dict:
        # 1. Initial Load & Hash — use system temp dir so files never leak into repo
        import tempfile
        suffix = os.path.splitext(filename)[1]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(file_content)
        tmp.close()
        temp_path = tmp.name
        
        try:
            if filename.lower().endswith(".pdf"):
                from app.config import settings
                raw_text = await PDFParser.extract_text_async(temp_path, api_key=settings.OPENAI_API_KEY)
            else:
                raw_text = DocxParser.extract_text(temp_path)
            
            content_hash = self.calculate_content_hash(raw_text)
            
            # Use content_hash as a stable reference for the Run ID to support resumption
            run_id = f"run_{content_hash[:24]}"
            
            res = await self.db.execute(select(AgentRunModel).where(AgentRunModel.id == run_id))
            agent_run = res.scalar_one_or_none()
            
            if not agent_run:
                agent_run = AgentRunModel(id=run_id, workflow_name="resume_ingestion", status="running", metadata_json={"filename": filename})
                self.db.add(agent_run)
                await self.db.flush()

            # ── 17-STAGE PIPELINE WITH CHECKPOINTS ───────────────────────────

            # Stage 1: Regex contact extraction — BEFORE redaction or LLM
            # Name, email, phone are captured here so they never reach OpenAI.
            async def run_contact_extraction():
                return TextProcessor.extract_contact_info(raw_text)

            contact_data = await self._get_or_run_step(run_id, "contact_extraction", run_contact_extraction)

            # Stage 2: Clean + Redact (strips name, email, phone, URLs from text)
            async def run_prep():
                clean = TextProcessor.clean_text(raw_text)
                redacted, pii, red_map = TextProcessor.redact_pii(clean, name=contact_data.get("name"))
                return {"redacted_text": redacted, "pii": pii}

            prep_data = await self._get_or_run_step(run_id, "preprocessing", run_prep)

            # Stage 3: LLM receives REDACTED text — extracts only professional info
            async def run_extraction():
                return await self.analyzer.analyze(prep_data["redacted_text"])

            extracted_data = await self._get_or_run_step(run_id, "llm_extraction", run_extraction)

            # Stage 10-13: Ontology & Seniority
            async def run_enrichment():
                enriched = SkillOntology.normalize_skills_from_list(extracted_data.get("skills") or [])
                total_yrs = float(extracted_data.get("total_experience_years") or 0)
                seniority = SeniorityEnricher.detect_seniority(
                    current_title=extracted_data.get("current_title", ""),
                    total_years=total_yrs,
                    work_experience=extracted_data.get("work_experience") or []
                )
                seniority["total_years"] = total_yrs  # persist so fetch_and_align can read it
                return {"skills": [s["name"] for s in enriched], "seniority": seniority}

            enrichment_data = await self._get_or_run_step(run_id, "enrichment", run_enrichment)

            # Stage 14: Persistence — contact fields come from regex, professional from LLM
            async def run_persistence():
                name = contact_data.get("name") or "Unknown"
                full_name = name.split(" ", 1)
                candidate = await self.repo.get_or_create_candidate(
                    email=contact_data.get("email"),
                    first_name=full_name[0], last_name=full_name[1] if len(full_name) > 1 else "",
                    phone=contact_data.get("phone"),
                    linkedin_url=contact_data.get("linkedin_url"),
                )
                
                resume_id = str(uuid.uuid4())
                resume_data = {
                    "id": resume_id, "candidate_id": candidate.id,
                    "title": extracted_data.get("current_title"), "raw_text": prep_data["redacted_text"],  # PII-free
                    "content_hash": content_hash, "skills_json": enrichment_data["skills"],
                    "experience_json": extracted_data.get("work_experience"),
                    "metadata_json": {"seniority": enrichment_data["seniority"]},
                    "uploaded_by": user_id,
                }
                await self.repo.save_resume(resume_data)
                return {"resume_id": resume_id, "candidate_id": candidate.id}
            
            # Persistence is NOT cached via checkpoint — always verify the resume still exists.
            # If DB was cleared, cached resume_id would be stale and nothing would be written.
            from sqlalchemy import select as _select
            from app.layer6_data.models.resume.resume_model import ResumeModel as _ResumeModel
            _cached = await self.db.execute(
                _select(AgentStepModel)
                .where(AgentStepModel.run_id == run_id)
                .where(AgentStepModel.step_name == "persistence")
                .where(AgentStepModel.status == "completed")
                .limit(1)
            )
            _cached_step = _cached.scalar_one_or_none()
            _resume_exists = False
            if _cached_step and isinstance(_cached_step.output_data, dict):
                _rid = _cached_step.output_data.get("resume_id")
                if _rid:
                    _r = await self.db.execute(_select(_ResumeModel).where(_ResumeModel.id == _rid))
                    _resume_exists = _r.scalar_one_or_none() is not None
            if _resume_exists:
                persistence_data = _cached_step.output_data
            else:
                persistence_data = await self._get_or_run_step(run_id, "persistence", run_persistence)

            # Stage 15-17: Granular Memory & Vector Isolation
            async def run_memory():
                import asyncio as _asyncio
                cluster = extracted_data.get("job_cluster", "other")
                res = await self.db.execute(select(UserModel).where(UserModel.id == user_id))
                user_model = res.scalar_one_or_none()
                company_id = user_model.company_id if user_model else None

                chunks = [
                    ("resume_summary", f"Role: {extracted_data.get('current_title')}. Summary: {extracted_data.get('summary')}"),
                    ("resume_skills", f"Skills: {', '.join(enrichment_data['skills'])}"),
                ]

                # Generate all embeddings in parallel instead of sequentially
                vectors = await _asyncio.gather(*[self.embedder.generate_embedding(text) for _, text in chunks])

                for idx, ((c_type, c_text), vector) in enumerate(zip(chunks, vectors)):
                    memory = MemoryModel(
                        id=str(uuid.uuid4()), resume_id=persistence_data["resume_id"], company_id=company_id,
                        cluster=cluster, entity_type="resume_chunk", chunk_type=c_type,
                        chunk_index=idx, text=c_text, embedding=vector,
                        embedding_model=self.embedding_model, embedding_version=self.embedding_version, is_active=True
                    )
                    self.db.add(memory)
                return {"cluster": cluster}

            await self._get_or_run_step(run_id, "vector_indexing", run_memory)

            # Stage 15+: Granular Memory (Priority 1 logic)
            # This is skipped if already in memories table
            # ... (Implementation similar to above)

            agent_run.status = "completed"
            await self.db.commit()
            return {"status": "success", "resume_id": persistence_data["resume_id"]}

        finally:
            if os.path.exists(temp_path): os.remove(temp_path)

    async def execute_bulk(self, zip_content: bytes, user_id: str, session_id: str = None) -> List[dict]:
        """Elite Bulk Processing: Parallel extraction with concurrency control and lively updates"""
        import asyncio
        import zipfile
        import io
        from app.database import AsyncSessionLocal
        from app.layer6_data.models.resume.bulk_upload_model import BulkUploadModel
        from sqlalchemy import update
        
        results = []
        semaphore = asyncio.Semaphore(8)  # 8 concurrent files

        async def process_file(filename, content):
            async with semaphore:
                last_error = "Unknown error"
                for attempt in range(2):
                    try:
                        async with AsyncSessionLocal() as db:
                            temp_use_case = ParseResumeUseCase(db)
                            res = await temp_use_case.execute_single(content, filename, user_id)
                        if session_id:
                            async with AsyncSessionLocal() as update_db:
                                await update_db.execute(
                                    update(BulkUploadModel)
                                    .where(BulkUploadModel.id == session_id)
                                    .values(processed_count=BulkUploadModel.processed_count + 1)
                                )
                                await update_db.commit()
                        return {"filename": filename, "status": "success", "id": res.get("resume_id")}
                    except Exception as e:
                        last_error = str(e)
                        print(f"Attempt {attempt+1} failed for {filename}: {e}")
                return {"filename": filename, "status": "error", "message": last_error}

        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            # Filter for PDF and DOCX
            filenames = [f for f in z.namelist() if f.lower().endswith(('.pdf', '.docx')) and not f.startswith('__MACOSX')]
            
            print(f"Starting parallel bulk processing of {len(filenames)} files...")
            tasks = []
            for filename in filenames:
                with z.open(filename) as f:
                    content = f.read()
                tasks.append(process_file(filename, content))
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks)
        
        print(f"Bulk processing complete. Success: {len([r for r in results if r['status'] == 'success'])}/{len(filenames)}")
        return results

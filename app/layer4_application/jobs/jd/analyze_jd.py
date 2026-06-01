import re
import uuid
import time
import hashlib
from datetime import datetime
from sqlalchemy import select, desc
from app.layer2_adapters.files.pdf_parser import PDFParser
from app.layer2_adapters.files.docx_parser import DocxParser
from app.layer7_crosscutting.jd.text_processor import TextProcessor
from app.layer2_adapters.ai.jd.jd_analyzer import JDAnalyzerAgent
from app.layer4_application.jobs.jd.normalize_jd import JDNormalizer
from app.layer4_application.jobs.jd.enrich_jd import JDEnricher
from app.layer7_crosscutting.jd.skill_ontology import SkillOntology
from app.layer7_crosscutting.resume.seniority_enricher import SeniorityEnricher
from app.layer2_adapters.ai.embedding_service import EmbeddingService


def _skill_in_jd_text(skill: str, text_lower: str) -> bool:
    """
    Verify a skill (or any of its aliases) literally appears in the JD text.
    Prevents LLM from keeping inferred skills not written in the JD.
    """
    candidates = {skill}
    for alias, canon in SkillOntology.ALIASES.items():
        if canon == skill and len(alias) >= 2:
            candidates.add(alias)
    for s in candidates:
        if re.search(r'\b' + re.escape(s) + r'\b', text_lower):
            return True
    return False

# Models
from app.layer6_data.models.memory_model import MemoryModel
from app.layer6_data.models.jd.job_model import JobModel, JobStatus
from app.layer6_data.models.jd.job_version_model import JobVersionModel
from app.layer6_data.models.agent_model import AgentRunModel, AgentStepModel
from app.layer6_data.models.user_model import UserModel

from app.layer6_data.repositories_impl.jd.postgres_job_repo import PostgresJobRepository

class AnalyzeJDUseCase:
    def __init__(self, db_session):
        self.db = db_session
        self.analyzer = JDAnalyzerAgent()
        self.embedder = EmbeddingService()
        self.job_repo = PostgresJobRepository(db_session)
        
        # Priority 2 Specs
        self.embedding_model = "text-embedding-3-small"
        self.embedding_version = "1.0"

    async def _log_step(self, run_id: str, step_name: str, status: str = "completed", input_data=None, output_data=None, start_time=None):
        latency = (time.time() - start_time) * 1000 if start_time else 0
        step = AgentStepModel(
            id=str(uuid.uuid4()), run_id=run_id, step_name=step_name,
            input_data=input_data, output_data=output_data, status=status, latency_ms=latency
        )
        self.db.add(step)
        await self.db.flush()

    def calculate_content_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    async def execute(self, file_path: str, user_id: str, job_id: str = None) -> dict:
        run_id = str(uuid.uuid4())
        agent_run = AgentRunModel(
            id=run_id, workflow_name="jd_analysis", status="running",
            metadata_json={"file_path": file_path, "user_id": user_id}
        )
        self.db.add(agent_run)

        try:
            # 1. Ingestion
            t0 = time.time()
            if file_path.endswith(".pdf"): raw_text = PDFParser.extract_text(file_path)
            elif file_path.endswith(".docx"): raw_text = DocxParser.extract_text(file_path)
            else: raise Exception("Unsupported file format")
            await self._log_step(run_id, "file_ingestion", start_time=t0)

            # 2. Idempotency Check (Priority 2)
            # If we already have this exact JD version for this job, we can skip or link.
            content_hash = self.calculate_content_hash(raw_text)
            # (Optional: check if latest version hash matches to avoid redundant work)

            # 4. Preprocessing (no PII redaction — JDs are company documents, not personal data)
            t0 = time.time()
            clean_text = TextProcessor.clean_text(raw_text)
            await self._log_step(run_id, "preprocessing", start_time=t0)

            # 7. LLM Extraction (Priority 2: Retries included in service)
            t0 = time.time()
            extracted_data = await self.analyzer.extract_structured_jd(clean_text)
            await self._log_step(run_id, "llm_extraction", start_time=t0)

            # 9-14. Normalization & Ontology
            extracted_data["experience"] = JDNormalizer.normalize_experience(extracted_data.get("experience"))

            # Support both new schema (must_have_skills) and legacy (primary_skills)
            must_have_raw   = extracted_data.get("must_have_skills") or extracted_data.get("primary_skills") or []
            nice_to_have_raw = extracted_data.get("nice_to_have_skills") or []

            enriched_must   = SkillOntology.normalize_skills([{"name": s, "importance": "must-have"} for s in must_have_raw])
            enriched_nice   = SkillOntology.normalize_skills([{"name": s, "importance": "preferred"} for s in nice_to_have_raw])

            canonical_must_have    = [s["name"] for s in enriched_must]
            canonical_nice_to_have = [s["name"] for s in enriched_nice]

            # Post-LLM validation: drop any skill not literally present in the JD text.
            # Prevents the LLM from inferring skills never written in the document.
            jd_text_lower = clean_text.lower()
            canonical_must_have    = [s for s in canonical_must_have    if _skill_in_jd_text(s, jd_text_lower)]
            canonical_nice_to_have = [s for s in canonical_nice_to_have if _skill_in_jd_text(s, jd_text_lower)]

            # Persist normalized + validated skill lists back into requirements_json
            extracted_data["must_have_skills"]   = canonical_must_have
            extracted_data["nice_to_have_skills"] = canonical_nice_to_have
            extracted_data["primary_skills"]      = canonical_must_have  # legacy fallback

            # 16. Seniority
            seniority = SeniorityEnricher.detect_seniority(
                current_title=extracted_data.get("role", ""),
                total_years=float((extracted_data.get("experience") or {}).get("min") or 0),
                work_experience=[]
            )

            # Identity & Version Layers (Priority 2: Archive Others)
            res = await self.db.execute(select(UserModel).filter(UserModel.id == user_id))
            user_model = res.scalar_one_or_none()
            company_id = user_model.company_id if user_model else None

            job = await self.job_repo.get_by_id(job_id) if job_id else None
            
            if not job:
                from app.layer5_domain.entities.jd.job import Job
                job_entity = Job(
                    title=extracted_data.get("role") or "Untitled Job",
                    description=clean_text,
                    employment_type=extracted_data.get("employment_type"),
                    experience_level=extracted_data.get("experience_level"),
                    company_id=company_id,
                    created_by=user_id,
                    requirements=extracted_data.get("requirements"),
                    benefits=extracted_data.get("benefits"),
                    industry=extracted_data.get("industry"),
                    job_function=extracted_data.get("job_function"),
                    keywords=extracted_data.get("skills") or [],
                    status=JobStatus.OPEN.value
                )
                job_entity = await self.job_repo.create(job_entity)
                actual_job_id = job_entity.id
            else:
                actual_job_id = job.id
                job.current_title = extracted_data.get("role") or job.current_title

            # Create Version & Archive Old (Priority 2)
            res = await self.db.execute(select(JobVersionModel.version).where(JobVersionModel.job_id == actual_job_id).order_by(desc(JobVersionModel.version)).limit(1))
            latest_version = res.scalar_one_or_none() or 0
            job_version_id = str(uuid.uuid4())
            job_version = JobVersionModel(
                id=job_version_id, job_id=actual_job_id, title=extracted_data.get("role"),
                description=clean_text, requirements_json=extracted_data, version=latest_version + 1,
                embedding_model=self.embedding_model, embedding_version=self.embedding_version, 
                scoring_weights=extracted_data.get("scoring_weights"), # Save dynamic weights
                is_active=True
            )
            await self.job_repo.save_job_version(job_version, archive_others=True)

            # Granular Chunked Embeddings
            t0 = time.time()
            chunks = [
                ("job_summary",      f"Role: {extracted_data.get('role')}. Seniority: {seniority.get('level')}. Summary: {extracted_data.get('summary')}"),
                ("mandatory_skills", f"Must-Have Skills: {', '.join(canonical_must_have)}. Preferred: {', '.join(canonical_nice_to_have)}"),
                ("responsibilities", f"Responsibilities: {'; '.join(extracted_data.get('responsibilities') or [])}"),
            ]

            for idx, (c_type, c_text) in enumerate(chunks):
                vector = await self.embedder.generate_embedding(c_text)
                memory = MemoryModel(
                    id=str(uuid.uuid4()), job_version_id=job_version_id, company_id=company_id,
                    cluster=extracted_data.get("job_cluster", "other"),
                    entity_type="job_chunk",
                    chunk_type=c_type, chunk_index=idx, text=c_text, embedding=vector,
                    embedding_model=self.embedding_model, embedding_version=self.embedding_version, is_active=True
                )
                self.db.add(memory)
            
            await self.db.flush()
            await self._log_step(run_id, "granular_chunking", start_time=t0)

            agent_run.status = "completed"
            agent_run.completed_at = datetime.now()
            return {"job_id": actual_job_id, "version": job_version.version, "status": "success"}

        except Exception as e:
            # Rollback the aborted transaction before attempting any writes
            try:
                await self.db.rollback()
                agent_run.status = "failed"
                agent_run.completed_at = datetime.now()
                await self.db.flush()
                await self.db.commit()
            except Exception:
                pass
            raise e

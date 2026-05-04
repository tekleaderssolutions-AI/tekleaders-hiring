import uuid
from sqlalchemy import select
from app.layer2_adapters.files.pdf_parser import PDFParser
from app.layer2_adapters.files.docx_parser import DocxParser
from app.layer7_crosscutting.jd.text_processor import TextProcessor
from app.layer2_adapters.ai.jd.jd_analyzer import JDAnalyzerAgent
from app.layer4_application.jobs.jd.normalize_jd import JDNormalizer
from app.layer4_application.jobs.jd.enrich_jd import JDEnricher
from app.layer7_crosscutting.jd.skill_ontology import SkillOntology
from app.layer2_adapters.ai.embedding_service import EmbeddingService
from app.layer6_data.models.memory_model import MemoryModel

from app.layer6_data.repositories_impl.postgres_memory_repo import PostgresMemoryRepository

class AnalyzeJDUseCase:
    def __init__(self, db_session):
        self.db = db_session
        self.analyzer = JDAnalyzerAgent()
        self.embedder = EmbeddingService()
        self.memory_repo = PostgresMemoryRepository(db_session)

    def build_summary(self, structured_jd: dict, raw_jd_text: str) -> str:
        role = structured_jd.get("role") or "Unknown role"
        location = structured_jd.get("location") or "Unspecified location"
        employment_type = structured_jd.get("employment_type") or "unspecified"
        exp = structured_jd.get("experience") or {}
        exp_text = ""
        if exp.get("min") is not None or exp.get("max") is not None:
            exp_text = f"{exp.get('min') or ''}-{exp.get('max') or ''} years"

        primary = ", ".join(structured_jd.get("primary_skills") or [])
        responsibilities = structured_jd.get("responsibilities") or []

        parts = [
            f"{role} opportunity based in {location} ({employment_type}).",
        ]

        if exp_text:
            parts.append(f"Experience: {exp_text}.")

        if primary:
            parts.append(f"Primary skills: {primary}.")

        if responsibilities:
            resp_sentence = "Responsibilities include " + "; ".join(responsibilities[:4]) + "."
            parts.append(resp_sentence)

        summary = " ".join(parts).strip()

        if len(summary) < 150:
            filler = raw_jd_text[: max(0, 150 - len(summary))]
            summary = f"{summary} {filler}".strip()

        if len(summary) > 800:
            summary = summary[:800].rsplit(" ", 1)[0]

        return summary

    def build_embedding_text(self, structured_jd: dict, summary: str = None) -> str:
        role = structured_jd.get("role") or ""
        location = structured_jd.get("location") or ""
        primary_skills = structured_jd.get("primary_skills") or []
        exp = structured_jd.get("experience") or {}
        exp_min = exp.get("min")
        exp_max = exp.get("max")

        primary_csv = ", ".join(primary_skills)

        if exp_min is not None or exp_max is not None:
            exp_str = f"{exp_min or ''}-{exp_max or ''}".strip("-")
        else:
            exp_str = ""

        if not summary:
            summary = f"{role} in {location} with skills {primary_csv}".strip()

        return f"{role} | {location} | skills: {primary_csv} | experience: {exp_str} | summary: {summary}"

    async def execute(self, file_path: str, user_id: str, job_id: str = None) -> dict:
        # 1. Ingestion
        if file_path.endswith(".pdf"):
            raw_text = PDFParser.extract_text(file_path)
        elif file_path.endswith(".docx"):
            raw_text = DocxParser.extract_text(file_path)
        else:
            raise Exception("Unsupported file format")

        if not raw_text:
            raise Exception("Failed to parse file")

        # 2. Preprocessing
        clean_text = TextProcessor.clean_text(raw_text)

        # 4. PII Redaction
        redacted_text, pii_flag, redactions = TextProcessor.redact_pii(clean_text)

        # 5. LLM Extraction
        extracted_data = await self.analyzer.extract_structured_jd(redacted_text)

        # 7. Normalization
        extracted_data["experience"] = JDNormalizer.normalize_experience(extracted_data.get("experience"))
        extracted_data["salary"] = JDNormalizer.normalize_salary(extracted_data.get("salary"))
        extracted_data["location"] = JDNormalizer.normalize_location(extracted_data.get("location"))

        # 12. Quality Scoring
        quality_score = JDEnricher.calculate_quality_score(extracted_data)
        extracted_data["quality_score"] = quality_score

        # 13. Embedding & Summary
        summary = self.build_summary(extracted_data, redacted_text)
        embedding_text = self.build_embedding_text(extracted_data, summary=summary)
        embedding_vector = await self.embedder.generate_embedding(embedding_text)

        # 14. Sequential ID Generation (for Memory/Matching)
        short_id = await self.memory_repo.get_next_short_id()

        # 15. Create High-Level Job Record (for Dashboard)
        # We need a company_id. If not provided, we'll assume the user has one.
        from app.layer6_data.repositories_impl.jd.postgres_job_repo import PostgresJobRepository
        from app.layer5_domain.entities.jd.job import Job
        job_repo = PostgresJobRepository(self.db)
        
        # Determine job_id
        actual_job_id = job_id or str(uuid.uuid4())
        
        # Get next business job_code (e.g. TEK-001)
        # Note: We need company_id for this. If not passed, we'll need to fetch it from the user.
        from app.layer6_data.models.user_model import UserModel
        res = await self.db.execute(select(UserModel).filter(UserModel.id == user_id))
        user_model = res.scalar_one_or_none()
        company_id = user_model.company_id if user_model else None

        job_code = await job_repo.get_next_job_code(company_id) if company_id else f"TEK-{short_id[-3:]}"

        # 16. Storage - Memory (AI Matching)
        memory_id = str(uuid.uuid4())
        
        exp = extracted_data.get("experience") or {}
        salary = extracted_data.get("salary") or {}
        
        metadata = {
            "job_id": actual_job_id,
            "job_code": job_code,
            "location": extracted_data.get("location"),
            "employment_type": extracted_data.get("employment_type"),
            "experience_min": exp.get("min"),
            "experience_max": exp.get("max"),
            "primary_skills": extracted_data.get("primary_skills") or [],
            "secondary_skills": extracted_data.get("secondary_skills") or [],
            "salary_min": salary.get("min"),
            "salary_max": salary.get("max"),
            "version": 1,
            "created_by": user_id,
            "pii_flag": pii_flag,
            "raw_text_snippet": redacted_text[:800],
            "short_id": short_id,
            "quality_score": quality_score
        }

        memory = MemoryModel(
            id=memory_id,
            type="job",
            title=extracted_data.get("role") or "Untitled role",
            text=embedding_text,
            embedding=embedding_vector,
            metadata_=metadata,
            canonical_json=extracted_data,
            short_id=short_id,
            user_id=user_id
        )
        
        await self.memory_repo.save(memory)

        # 17. Storage - Job Posting (Dashboard)
        from app.layer6_data.models.jd.job_model import JobModel
        
        job_model = JobModel(
            id=actual_job_id,
            company_id=company_id,
            created_by=user_id,
            title=extracted_data.get("role") or "Untitled Role",
            job_code=job_code,
            short_id=short_id,
            location=extracted_data.get("location"),
            description=redacted_text,
            employment_type=extracted_data.get("employment_type") or "Full-time",
            experience_level="Mid Level", # Default or map from experience min
            primary_skills=extracted_data.get("primary_skills"),
            salary_min=salary.get("min"),
            salary_max=salary.get("max"),
            salary_currency=salary.get("currency") or "INR",
            status="open"
        )
        self.db.add(job_model)
        await self.db.flush()

        return {
            "job_id": actual_job_id,
            "job_code": job_code,
            "short_id": short_id,
            "memory_id": memory_id,
            "structured_data": extracted_data,
            "summary": summary,
            "quality_score": quality_score
        }

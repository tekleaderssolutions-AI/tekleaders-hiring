import uuid
from app.layer2_adapters.files.pdf_parser import PDFParser
from app.layer2_adapters.files.docx_parser import DocxParser
from app.layer7_crosscutting.jd.text_processor import TextProcessor
from app.layer2_adapters.ai.jd.jd_analyzer import JDAnalyzerAgent
from app.layer4_application.jobs.jd.normalize_jd import JDNormalizer
from app.layer4_application.jobs.jd.enrich_jd import JDEnricher
from app.layer7_crosscutting.jd.skill_ontology import SkillOntology
from app.layer2_adapters.ai.embedding_service import EmbeddingService
from app.layer6_data.models.memory_model import MemoryModel

class AnalyzeJDUseCase:
    def __init__(self, db_session):
        self.db = db_session
        self.analyzer = JDAnalyzerAgent()
        self.embedder = EmbeddingService()

    async def execute(self, file_path: str, user_id: str, job_id: str = None) -> dict:
        # 1. Ingestion (Step 1)
        if file_path.endswith(".pdf"):
            raw_text = PDFParser.extract_text(file_path)
        elif file_path.endswith(".docx"):
            raw_text = DocxParser.extract_text(file_path)
        else:
            raise Exception("Unsupported file format")

        if not raw_text:
            raise Exception("Failed to parse file")

        # 2. Preprocessing (Step 2)
        clean_text = TextProcessor.clean_text(raw_text)

        # 3. Section Segmentation (Step 3 - CRITICAL)
        segmented_jd = TextProcessor.segment_jd(clean_text)

        # 4. PII Redaction (Step 4 - MANDATORY)
        redacted_text, pii_flag, redactions = TextProcessor.redact_pii(clean_text)

        # 5. LLM Extraction (Step 5)
        extracted_data = await self.analyzer.extract_structured_jd(redacted_text)

        # 7. Normalization (Step 7)
        extracted_data["experience"] = JDNormalizer.normalize_experience(extracted_data.get("experience"))
        extracted_data["salary"] = JDNormalizer.normalize_salary(extracted_data.get("salary"))
        extracted_data["location"] = JDNormalizer.normalize_location(extracted_data.get("location"))

        # 8. Skill Ontology System (Step 8 - Core Intelligence)
        raw_primary_skills = extracted_data.get("primary_skills", [])
        extracted_data["ontology_skills"] = SkillOntology.normalize_skills(raw_primary_skills)

        # 9-11. Enrichment (Hybrid)
        extracted_data["categorized_responsibilities"] = JDEnricher.classify_responsibilities(extracted_data.get("responsibilities", []))
        extracted_data["seniority"] = JDEnricher.detect_seniority(
            extracted_data.get("seniority_hints", []), 
            extracted_data["experience"].get("min", 0)
        )

        # 12. Quality Scoring (Step 12)
        quality_score = JDEnricher.calculate_quality_score(extracted_data)
        extracted_data["quality_score"] = quality_score

        # 13. Embedding (Step 13)
        embedding_text = self.embedder.build_embedding_text(extracted_data)
        embedding_vector = await self.embedder.generate_embedding(embedding_text)

        # 14. Storage (Step 14)
        memory_id = str(uuid.uuid4())
        memory = MemoryModel(
            id=memory_id,
            type="job",
            title=extracted_data.get("role"),
            text=embedding_text,
            embedding=embedding_vector,
            metadata={
                "job_id": job_id,
                "location": extracted_data.get("location"),
                "experience_min": extracted_data.get("experience", {}).get("min"),
                "seniority": extracted_data["seniority"],
                "quality_score": quality_score,
                "created_by": user_id,
                "pii_flag": pii_flag,
                "redactions": redactions,
                "audit_log": { # Step 17 Audit & Traceability
                    "ingestion": "success",
                    "redaction": "pii_removed" if pii_flag else "none_found",
                    "extraction": "llm_complete",
                    "ontology": "applied"
                }
            },
            canonical_json=extracted_data
        )
        
        self.db.add(memory)

        return {
            "memory_id": memory_id,
            "structured_data": extracted_data,
            "quality_score": quality_score,
            "pii_redacted": pii_flag
        }

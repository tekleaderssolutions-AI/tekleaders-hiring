import uuid
from typing import List, Dict
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

# Models
from app.layer6_data.models.resume.resume_model import ResumeModel
from app.layer6_data.models.jd.job_model import JobModel
from app.layer6_data.models.jd.job_version_model import JobVersionModel
from app.layer6_data.models.memory_model import MemoryModel
from app.layer6_data.models.application_model import ApplicationModel, ApplicationStage
from app.layer6_data.models.evaluation_model import CandidateEvaluationModel

# Agents
from app.layer2_adapters.ai.resume.resume_analyzer import ResumeAnalyzerAgent

class FetchAndAlignUseCase:
    """
    ELITE MATCHING ENGINE v3.2
    Priority: Scaling Economics & Trust.
    Implements Gating, Caching, and Decision-Level Metrics.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.reranker = ResumeAnalyzerAgent()

    async def execute(self, job_id: str, company_id: str, top_k: int = 10, rerank_threshold: float = 60.0) -> List[Dict]:
        # 1. Fetch Active JD Version
        res = await self.db.execute(
            select(JobVersionModel).where(JobVersionModel.job_id == job_id, JobVersionModel.is_active == True)
            .order_by(JobVersionModel.version.desc()).limit(1)
        )
        job_version = res.scalar_one_or_none()
        if not job_version: raise ValueError("No active job version found")

        # 2. Get JD Embedding
        res = await self.db.execute(
            select(MemoryModel.embedding, MemoryModel.cluster).where(MemoryModel.job_version_id == job_version.id, MemoryModel.chunk_type == "job_summary").limit(1)
        )
        jd_memory = res.first()
        if not jd_memory: raise ValueError("JD embedding missing.")
        jd_embedding, jd_cluster = jd_memory

        # 3. Aggregated Vector Retrieval (Max-Pooling)
        vector_query = text("""
            SELECT 
                r.id as resume_id, r.candidate_id, r.skills_json, r.raw_text, r.metadata_json as resume_metadata,
                MAX(1 - (m.embedding <=> :jd_vector)) as best_similarity
            FROM memories m
            JOIN resumes r ON m.resume_id = r.id
            WHERE m.entity_type = 'resume_chunk' AND m.company_id = :company_id AND m.cluster = :cluster
              AND r.is_active = True AND m.is_active = True
            GROUP BY r.id, r.candidate_id, r.skills_json, r.raw_text, r.metadata_json
            ORDER BY best_similarity DESC LIMIT :limit
        """)

        result_proxy = await self.db.execute(vector_query, {"jd_vector": jd_embedding, "company_id": company_id, "cluster": jd_cluster, "limit": top_k * 5})
        candidates = result_proxy.mappings().all()

        # 4. Hybrid Scoring & Gating
        matches = []
        reqs = job_version.requirements_json or {}
        primary_skills = set(reqs.get("primary_skills") or [])
        min_exp = float((reqs.get("experience") or {}).get("min") or 0)

        for cand in candidates:
            cand_skills = set(cand["skills_json"] or [])
            p_match_count = len(cand_skills.intersection(primary_skills))
            skills_score = (p_match_count / len(primary_skills)) if primary_skills else 1.0
            
            # Penalties
            penalty = 1.0
            if len(primary_skills) > 0 and p_match_count < (len(primary_skills) / 2): penalty *= 0.7 
            cand_exp = float((cand["resume_metadata"] or {}).get("seniority", {}).get("total_years") or 0)
            if cand_exp < min_exp: penalty *= 0.8

            semantic_score = float(cand["best_similarity"])
            hybrid_score = ((0.4 * semantic_score) + (0.6 * skills_score)) * penalty
            hybrid_score_100 = round(hybrid_score * 100, 2)

            matches.append({
                "resume_id": cand["resume_id"], "candidate_id": cand["candidate_id"],
                "raw_text": cand["raw_text"], "initial_score": hybrid_score_100,
                "semantic_score": semantic_score, "skills_score": skills_score,
                "penalty_applied": 1.0 - penalty
            })

        # 5. ── ELITE GATING & CACHING (Cost Control) ───────────────────
        # Sort and take top candidates for possible reranking
        final_results = sorted(matches, key=lambda x: x["initial_score"], reverse=True)
        top_candidates = final_results[:top_k]
        
        for match in top_candidates:
            # Check Cache: Have we already reranked this resume for this job version?
            res = await self.db.execute(
                select(CandidateEvaluationModel)
                .join(ApplicationModel)
                .where(ApplicationModel.resume_id == match["resume_id"])
                .where(ApplicationModel.job_version_id == job_version.id)
                .where(CandidateEvaluationModel.model_version != None) # Indicates an LLM eval was done
                .limit(1)
            )
            cached_eval = res.scalar_one_or_none()
            
            if cached_eval:
                match["final_score"] = cached_eval.final_score
                match["elite_reasoning"] = cached_eval.reasoning
                match["is_cached"] = True
                continue

            # Gating: Only rerank if score is high enough (rerank_threshold)
            if match["initial_score"] < rerank_threshold:
                match["final_score"] = match["initial_score"]
                match["elite_reasoning"] = "System match based on hybrid similarity and skill alignment."
                continue

            # Execute Reranker
            rerank_result = await self.reranker.evaluate_match(jd_text=job_version.description, resume_text=match["raw_text"])
            refined_relevance = rerank_result.get("relevance_score", 0.5)
            elite_score = (match["initial_score"] * 0.6) + (refined_relevance * 100 * 0.4)
            
            match["final_score"] = round(elite_score, 2)
            match["elite_reasoning"] = rerank_result.get("reasoning")
            match["strengths"] = rerank_result.get("top_strengths")
            match["gaps"] = rerank_result.get("critical_gaps")

            # Persist
            app_id = str(uuid.uuid4())
            application = ApplicationModel(
                id=app_id, candidate_id=match["candidate_id"], resume_id=match["resume_id"],
                job_id=job_id, job_version_id=job_version.id, company_id=company_id,
                current_stage=ApplicationStage.SCREENING, match_score=match["final_score"],
                score_breakdown={"hybrid": match["initial_score"], "rerank": round(refined_relevance * 100, 2)}
            )
            self.db.add(application)
            self.db.add(CandidateEvaluationModel(
                id=str(uuid.uuid4()), application_id=app_id, skills_score=round(match["skills_score"] * 100, 2),
                semantic_score=round(match["semantic_score"] * 100, 2), final_score=match["final_score"],
                reasoning=match["elite_reasoning"], strengths=match.get("strengths"), gaps=match.get("gaps"),
                model_version="gpt-4o"
            ))

        await self.db.flush()
        return sorted(top_candidates, key=lambda x: x.get("final_score", 0), reverse=True)

from typing import List, Optional
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.layer6_data.models.resume.candidate_model import CandidateModel
from app.layer6_data.models.resume.resume_model import ResumeModel

class PostgresCandidateRepository:
    """
    Handles persistence for Candidates (Identity) and Resumes (Versions).
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_candidate(self, email: str, first_name: str = None, last_name: str = None, phone: str = None) -> CandidateModel:
        """
        Ensures a global identity exists for the given email.
        """
        result = await self.session.execute(select(CandidateModel).where(CandidateModel.email == email))
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            candidate = CandidateModel(
                id=str(hashlib.md5(email.lower().encode()).hexdigest()[:12]), # Stable ID based on email
                email=email.lower(),
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            self.session.add(candidate)
            await self.session.flush()
        else:
            # Update info if provided and missing
            if first_name: candidate.first_name = first_name
            if last_name: candidate.last_name = last_name
            if phone: candidate.phone = phone
            
        return candidate

    async def get_resume_by_hash(self, content_hash: str) -> Optional[ResumeModel]:
        """
        Used for deduplication (Step 1b).
        """
        result = await self.session.execute(select(ResumeModel).where(ResumeModel.content_hash == content_hash))
        return result.scalar_one_or_none()

    async def save_resume(self, resume_data: dict, archive_others: bool = True) -> ResumeModel:
        """
        Saves a new versioned resume for a candidate.
        """
        candidate_id = resume_data["candidate_id"]
        
        # ── PRIORITY 2: Lifecycle Management ────────────────────────────────
        if archive_others:
            from sqlalchemy import update
            from app.layer6_data.models.memory_model import MemoryModel
            
            # 1. Archive old resumes
            await self.session.execute(
                update(ResumeModel)
                .where(ResumeModel.candidate_id == candidate_id)
                .values(is_active=False)
            )
            # 2. Archive associated memories
            # This ensures only the latest resume's chunks are active in the matching engine
            resume_ids_query = select(ResumeModel.id).where(ResumeModel.candidate_id == candidate_id)
            await self.session.execute(
                update(MemoryModel)
                .where(MemoryModel.resume_id.in_(resume_ids_query))
                .values(is_active=False)
            )

        # Get latest version number
        result = await self.session.execute(
            select(ResumeModel.version)
            .where(ResumeModel.candidate_id == candidate_id)
            .order_by(desc(ResumeModel.version))
            .limit(1)
        )
        latest_version = result.scalar_one_or_none() or 0
        
        resume = ResumeModel(
            **resume_data,
            version=latest_version + 1,
            is_active=True
        )
        self.session.add(resume)
        await self.session.flush()
        return resume

    async def get_candidate_with_resumes(self, candidate_id: str) -> Optional[CandidateModel]:
        result = await self.session.execute(
            select(CandidateModel).where(CandidateModel.id == candidate_id)
        )
        return result.scalar_one_or_none()

    async def list_candidates(self, limit: int = 100, offset: int = 0) -> List[CandidateModel]:
        result = await self.session.execute(select(CandidateModel).limit(limit).offset(offset))
        return result.scalars().all()

    async def count_candidates(self) -> int:
        """
        Returns total count of candidates for progress tracking.
        """
        from sqlalchemy import func
        result = await self.session.execute(select(func.count(CandidateModel.id)))
        return result.scalar_one()

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.layer5_domain.entities.resume.candidate import Candidate, CandidateExperience, CandidateEducation
from app.layer5_domain.repositories.resume.candidate_repository import CandidateRepository
from app.layer6_data.models.resume.candidate_model import CandidateModel

class PostgresCandidateRepository(CandidateRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: CandidateModel) -> Candidate:
        return Candidate(
            id=model.id,
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            phone=model.phone,
            location=model.location,
            summary=model.summary,
            skills=model.skills or [],
            experience=[CandidateExperience(**exp) for exp in (model.experience or [])],
            education=[CandidateEducation(**edu) for edu in (model.education or [])],
            total_years_experience=model.total_years_experience or 0.0,
            memory_id=model.memory_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            metadata=model.candidate_metadata or {}
        )

    async def save(self, candidate: Candidate) -> Candidate:
        model = CandidateModel(
            id=candidate.id,
            email=candidate.email,
            first_name=candidate.first_name,
            last_name=candidate.last_name,
            phone=candidate.phone,
            location=candidate.location,
            summary=candidate.summary,
            skills=candidate.skills,
            experience=[vars(exp) for exp in candidate.experience],
            education=[vars(edu) for edu in candidate.education],
            total_years_experience=candidate.total_years_experience,
            memory_id=candidate.memory_id,
            candidate_metadata=candidate.metadata
        )
        await self.session.merge(model)
        await self.session.flush()
        return candidate

    async def get_by_id(self, candidate_id: str) -> Optional[Candidate]:
        result = await self.session.execute(select(CandidateModel).where(CandidateModel.id == candidate_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[Candidate]:
        result = await self.session.execute(select(CandidateModel).where(CandidateModel.email == email))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_candidates(self, limit: int = 100, offset: int = 0) -> List[Candidate]:
        result = await self.session.execute(select(CandidateModel).limit(limit).offset(offset))
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def delete(self, candidate_id: str) -> bool:
        model = await self.session.get(CandidateModel, candidate_id)
        if model:
            await self.session.delete(model)
            await self.session.flush()
            return True
        return False

from abc import ABC, abstractmethod
from typing import List, Optional
from app.layer5_domain.entities.resume.candidate import Candidate

class CandidateRepository(ABC):
    @abstractmethod
    async def save(self, candidate: Candidate) -> Candidate:
        pass

    @abstractmethod
    async def get_by_id(self, candidate_id: str) -> Optional[Candidate]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Candidate]:
        pass

    @abstractmethod
    async def list_candidates(self, limit: int = 100, offset: int = 0) -> List[Candidate]:
        pass

    @abstractmethod
    async def delete(self, candidate_id: str) -> bool:
        pass

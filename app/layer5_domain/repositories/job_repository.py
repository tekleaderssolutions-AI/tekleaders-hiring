from abc import ABC, abstractmethod
from typing import Optional, List
from app.layer5_domain.entities.job import Job

class JobRepository(ABC):
    @abstractmethod
    async def create(self, job: Job) -> Job:
        pass

    @abstractmethod
    async def get_by_id(self, job_id: str) -> Optional[Job]:
        pass

    @abstractmethod
    async def list_by_company(self, company_id: str) -> List[Job]:
        pass

    @abstractmethod
    async def update(self, job: Job) -> Job:
        pass

    @abstractmethod
    async def get_next_job_code(self, company_id: str) -> str:
        pass

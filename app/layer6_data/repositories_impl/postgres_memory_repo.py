from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.layer6_data.models.memory_model import MemoryModel

class PostgresMemoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_next_short_id(self, prefix: str = "tek") -> str:
        """
        Generates the next sequential short ID based on existing memories.
        Follows reference logic: tek0001, tek0002, etc.
        """
        # Search for the latest short_id with the prefix
        query = select(MemoryModel.short_id)\
            .filter(MemoryModel.entity_type == "job")\
            .filter(MemoryModel.short_id.like(f"{prefix}%"))\
            .order_by(desc(MemoryModel.short_id))\
            .limit(1)
            
        result = await self.session.execute(query)
        last_id = result.scalar_one_or_none()
        
        if last_id:
            try:
                # Extract number from last short_id (e.g., 'tek0001' -> 1)
                last_num = int(last_id.replace(prefix, ''))
                next_num = last_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1
            
        return f"{prefix}{next_num:04d}"

    async def get_by_id(self, memory_id: str) -> Optional[MemoryModel]:
        result = await self.session.execute(select(MemoryModel).where(MemoryModel.id == memory_id))
        return result.scalar_one_or_none()

    async def save(self, memory_model: MemoryModel) -> MemoryModel:
        self.session.add(memory_model)
        await self.session.flush()
        return memory_model

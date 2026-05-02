from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
import uuid

from app.layer5_domain.entities.user import User
from app.layer5_domain.repositories.user_repository import UserRepository
from app.layer6_data.models.user_model import UserModel

class PostgresUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        user_model = result.scalars().first()
        if user_model:
            return self._map_to_entity(user_model)
        return None

    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        user_model = result.scalars().first()
        if user_model:
            return self._map_to_entity(user_model)
        return None

    async def create(self, user: User) -> User:
        user_id = str(uuid.uuid4())
        user_model = UserModel(
            id=user_id,
            email=user.email,
            hashed_password=user.hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            google_id=user.google_id,
            is_active=user.is_active
        )
        self.session.add(user_model)
        await self.session.flush()
        user.id = user_id
        return user

    async def update(self, user: User) -> User:
        # Implementation for update
        pass

    def _map_to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            first_name=model.first_name,
            last_name=model.last_name,
            google_id=model.google_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

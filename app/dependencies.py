from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import AsyncGenerator

from app.config import settings
from app.database import AsyncSessionLocal, engine
from app.layer6_data.repositories_impl.postgres_user_repo import PostgresUserRepository
from app.layer2_adapters.auth.google_auth_adapter import GoogleAuthAdapter
from app.layer5_domain.entities.user import User

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

# ─── Repository Dependencies ──────────────────────────────────────────────────
def get_user_repo(db: AsyncSession = Depends(get_db)) -> PostgresUserRepository:
    return PostgresUserRepository(db)

# ─── Adapter Dependencies ─────────────────────────────────────────────────────
def get_google_auth_adapter() -> GoogleAuthAdapter:
    return GoogleAuthAdapter()

# ─── Auth Guard ───────────────────────────────────────────────────────────────
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = PostgresUserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user

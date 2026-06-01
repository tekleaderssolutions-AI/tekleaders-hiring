from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# ─── Database Engine ──────────────────────────────────────────────────────────
# Neon (and most cloud DBs) require SSL — controlled via DATABASE_SSL env var
_connect_args = {"ssl": "require"} if settings.DATABASE_SSL else {}

engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=15,
    pool_timeout=30,
    pool_recycle=1800,
    connect_args=_connect_args,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

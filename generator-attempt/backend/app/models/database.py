from collections.abc import AsyncGenerator

from sqlalchemy import Column, JSON
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import Field, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import get_settings
from app.core.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

# PostgreSQL connection pooling for production
# SQLite uses NullPool to avoid connection issues
if settings.database_url.startswith("postgresql"):
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        future=True,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,   # Recycle connections after 1 hour
    )
    logger.info("database_engine_postgresql", pool_size=10)
else:
    # SQLite with NullPool for development
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        future=True,
        poolclass=NullPool,
    )
    logger.info("database_engine_sqlite")

SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class WorkflowRecord(SQLModel, table=True):
    __tablename__ = "workflows"

    id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    topic: str
    target_platforms: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: str = Field(index=True)
    state_snapshot: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_ts: int = Field(index=True)
    updated_ts: int = Field(index=True)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

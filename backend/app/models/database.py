from collections.abc import AsyncGenerator

from sqlalchemy import JSON, String, Integer
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import NullPool

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


class Base(DeclarativeBase):
    pass


class WorkflowRecord(Base):
    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    topic: Mapped[str] = mapped_column(String)
    target_platforms: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String, index=True)
    state_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    created_ts: Mapped[int] = mapped_column(Integer, index=True)
    updated_ts: Mapped[int] = mapped_column(Integer, index=True)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

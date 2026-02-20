from collections.abc import AsyncGenerator
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_session
from app.orchestration.workflow import ContentWorkflow
from app.services.redis_client import RedisCache


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


def get_workflow_engine(request: Request) -> ContentWorkflow:
    return request.app.state.workflow_engine


def get_cache(request: Request) -> RedisCache:
    return request.app.state.redis_cache

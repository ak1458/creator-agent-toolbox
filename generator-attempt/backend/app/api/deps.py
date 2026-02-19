from fastapi import Request
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.database import get_session
from app.orchestration.workflow import ContentWorkflow


async def get_db_session() -> AsyncSession:
    async for session in get_session():
        yield session


def get_workflow_engine(request: Request) -> ContentWorkflow:
    return request.app.state.workflow_engine

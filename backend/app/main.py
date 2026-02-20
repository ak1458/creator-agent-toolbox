from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.logger import configure_logging, get_logger
from app.models.database import init_db
from app.orchestration.workflow import ContentWorkflow
from app.services.redis_client import close_redis_cache, get_redis_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.ensure_data_dir()
    configure_logging(debug=settings.debug)

    logger = get_logger(__name__)
    logger.info("startup", database_url=settings.database_url, redis_url=settings.redis_url)

    # Initialize database
    await init_db()

    # Initialize Redis cache
    redis_cache = await get_redis_cache()
    app.state.redis_cache = redis_cache

    # Initialize workflow engine
    workflow_engine = ContentWorkflow()
    await workflow_engine.initialize()
    app.state.workflow_engine = workflow_engine

    try:
        yield
    finally:
        await workflow_engine.close()
        await close_redis_cache()
        logger.info("shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()

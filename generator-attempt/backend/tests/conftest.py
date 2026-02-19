import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    backend_dir = Path(__file__).resolve().parents[1]
    project_root = backend_dir.parent
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{(data_dir / 'test_app.db').as_posix()}"
    os.environ["CHECKPOINT_DB_URL"] = f"sqlite+aiosqlite:///{(data_dir / 'test_checkpoints.db').as_posix()}"
    os.environ["OPENAI_API_KEY"] = ""
    os.environ["LLM_PROVIDER"] = "mock"

    for file_name in ("test_app.db", "test_checkpoints.db"):
        file_path = data_dir / file_name
        if file_path.exists():
            file_path.unlink()

    # Delayed imports so env vars are in place first.
    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.main import create_app

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_DATABASE_PATH = DATA_DIR / "app.db"
DEFAULT_CHECKPOINT_PATH = DATA_DIR / "checkpoints.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Creator Agent Toolbox API"
    api_v1_prefix: str = "/api/v1"
    debug: bool = Field(default=False, alias="DEBUG")

    openai_api_key: str
    openai_base_url: str = Field(default="https://api.groq.com/openai/v1", alias="OPENAI_BASE_URL")
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    
    # Database - use Render disk path in production
    database_url: str = Field(
        default="sqlite:///./data/app.db",
        alias="DATABASE_URL",
    )
    checkpoint_db: str = Field(
        default="./data/checkpoints.db",
        alias="CHECKPOINT_DB",
    )

    # Redis configuration
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    cache_ttl_seconds: int = Field(default=300, alias="CACHE_TTL_SECONDS")  # 5 minutes default
    enable_cache: bool = Field(default=True, alias="ENABLE_CACHE")

    # Security
    secret_key: str = Field(default="change-this-in-production", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=10080, alias="ACCESS_TOKEN_EXPIRE_MINUTES")  # 7 days

    trend_model: str = "gpt-3.5-turbo-0125"
    script_model: str = "gpt-4-0125-preview"

    @field_validator("debug", mode="before")
    @classmethod
    def _coerce_debug(cls, value):
        if isinstance(value, bool):
            return value
        if value is None:
            return True

        normalized = str(value).strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
        return True

    @field_validator("llm_provider", mode="before")
    @classmethod
    def _normalize_provider(cls, value):
        if value is None:
            return "ollama"

        normalized = str(value).strip().lower()
        if normalized in {"openai", "ollama", "mock"}:
            return normalized
        return "ollama"

    @property
    def cors_list(self):
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @staticmethod
    def _sqlite_file_path(url: str) -> Path | None:
        for prefix in ("sqlite+aiosqlite:///", "sqlite:///"):
            if url.startswith(prefix):
                return Path(url.replace(prefix, "", 1))
        return None

    def ensure_data_dir(self) -> None:
        # Keep original project-level data dir behavior.
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Also honor explicit sqlite URLs from env so relative paths never fail.
        for url in (self.database_url, self.checkpoint_db_url):
            sqlite_path = self._sqlite_file_path(url)
            if sqlite_path is None:
                continue

            resolved = sqlite_path if sqlite_path.is_absolute() else (Path.cwd() / sqlite_path)
            resolved.parent.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()

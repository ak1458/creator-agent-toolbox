import json
import pickle
from typing import Any

import redis.asyncio as redis

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class RedisCache:
    """
    Redis cache client for the Creator Agent Toolbox.
    
    Provides caching for:
    - Workflow status lookups (frequent polling)
    - A/B test metrics (real-time data)
    - Trend analysis results (expensive LLM calls)
    - Rate limiting counters
    """

    def __init__(self):
        self.settings = get_settings()
        self._client: redis.Redis | None = None
        self._enabled = self.settings.enable_cache

    async def initialize(self) -> None:
        """Initialize Redis connection."""
        if not self._enabled:
            logger.info("redis_cache_disabled")
            return

        try:
            self._client = redis.from_url(
                self.settings.redis_url,
                decode_responses=False,  # We'll handle encoding manually for flexibility
            )
            # Test connection
            await self._client.ping()
            logger.info("redis_connected", url=self.settings.redis_url)
        except Exception as e:
            logger.warning("redis_connection_failed", error=str(e))
            self._enabled = False
            self._client = None

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            logger.info("redis_disconnected")

    def _make_key(self, key: str, namespace: str = "cat") -> str:
        """Create a namespaced key."""
        return f"{namespace}:{key}"

    async def get(self, key: str, namespace: str = "cat") -> Any | None:
        """Get value from cache."""
        if not self._enabled or not self._client:
            return None

        try:
            full_key = self._make_key(key, namespace)
            data = await self._client.get(full_key)
            if data is None:
                return None
            return pickle.loads(data)
        except Exception as e:
            logger.warning("redis_get_error", key=key, error=str(e))
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        namespace: str = "cat",
    ) -> bool:
        """Set value in cache with optional TTL."""
        if not self._enabled or not self._client:
            return False

        try:
            full_key = self._make_key(key, namespace)
            serialized = pickle.dumps(value)
            ttl = ttl or self.settings.cache_ttl_seconds
            await self._client.setex(full_key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning("redis_set_error", key=key, error=str(e))
            return False

    async def delete(self, key: str, namespace: str = "cat") -> bool:
        """Delete value from cache."""
        if not self._enabled or not self._client:
            return False

        try:
            full_key = self._make_key(key, namespace)
            result = await self._client.delete(full_key)
            return result > 0
        except Exception as e:
            logger.warning("redis_delete_error", key=key, error=str(e))
            return False

    async def delete_pattern(self, pattern: str, namespace: str = "cat") -> int:
        """Delete all keys matching pattern."""
        if not self._enabled or not self._client:
            return 0

        try:
            full_pattern = self._make_key(pattern, namespace)
            keys = await self._client.keys(full_pattern)
            if keys:
                return await self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning("redis_delete_pattern_error", pattern=pattern, error=str(e))
            return 0

    async def exists(self, key: str, namespace: str = "cat") -> bool:
        """Check if key exists in cache."""
        if not self._enabled or not self._client:
            return False

        try:
            full_key = self._make_key(key, namespace)
            result = await self._client.exists(full_key)
            return result > 0
        except Exception as e:
            logger.warning("redis_exists_error", key=key, error=str(e))
            return False

    async def increment(self, key: str, amount: int = 1, namespace: str = "cat") -> int:
        """Increment counter. Useful for rate limiting."""
        if not self._enabled or not self._client:
            return 0

        try:
            full_key = self._make_key(key, namespace)
            return await self._client.incrby(full_key, amount)
        except Exception as e:
            logger.warning("redis_increment_error", key=key, error=str(e))
            return 0

    async def expire(self, key: str, seconds: int, namespace: str = "cat") -> bool:
        """Set expiration on existing key."""
        if not self._enabled or not self._client:
            return False

        try:
            full_key = self._make_key(key, namespace)
            return await self._client.expire(full_key, seconds)
        except Exception as e:
            logger.warning("redis_expire_error", key=key, error=str(e))
            return False

    async def get_json(self, key: str, namespace: str = "cat") -> dict | list | None:
        """Get JSON value from cache."""
        if not self._enabled or not self._client:
            return None

        try:
            full_key = self._make_key(key, namespace)
            data = await self._client.get(full_key)
            if data is None:
                return None
            return json.loads(data.decode('utf-8'))
        except Exception as e:
            logger.warning("redis_get_json_error", key=key, error=str(e))
            return None

    async def set_json(
        self,
        key: str,
        value: dict | list,
        ttl: int | None = None,
        namespace: str = "cat",
    ) -> bool:
        """Set JSON value in cache."""
        if not self._enabled or not self._client:
            return False

        try:
            full_key = self._make_key(key, namespace)
            serialized = json.dumps(value).encode('utf-8')
            ttl = ttl or self.settings.cache_ttl_seconds
            await self._client.setex(full_key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning("redis_set_json_error", key=key, error=str(e))
            return False


# Global instance
_redis_cache: RedisCache | None = None


async def get_redis_cache() -> RedisCache:
    """Get or create Redis cache instance."""
    global _redis_cache
    if _redis_cache is None:
        _redis_cache = RedisCache()
        await _redis_cache.initialize()
    return _redis_cache


async def close_redis_cache() -> None:
    """Close global Redis cache instance."""
    global _redis_cache
    if _redis_cache:
        await _redis_cache.close()
        _redis_cache = None

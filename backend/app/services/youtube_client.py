from typing import Any
import googleapiclient.discovery
import googleapiclient.errors

from app.core.config import get_settings
from app.core.logger import get_logger
from app.services.redis_client import get_redis_cache

logger = get_logger(__name__)


class YouTubeClient:
    """Real client for fetching competitor analytics using YouTube Data API v3."""

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.youtube_api_key
        
        if self.api_key:
            self.youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=self.api_key)
        else:
            self.youtube = None

    async def get_analytics(self, query: str) -> dict[str, Any]:
        """Fetch real data from YouTube API and aggregate metrics."""
        
        # 1. Fallback to mock if API key missing
        if not self.youtube:
            logger.warning("youtube_api_key_missing_falling_back_to_mock")
            return self._mock_analytics(query)

        # 2. Try Cache first
        cache = await get_redis_cache()
        cache_key = f"youtube_analytics:{query.replace(' ', '_')}"
        
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            logger.info("using_cached_youtube_analytics", query=query)
            return cached_data

        # 3. Fetch from Real API
        try:
            # Step A: Search for videos
            search_request = self.youtube.search().list(
                part="id,snippet",
                q=query,
                type="video",
                maxResults=5,
                order="viewCount"
            )
            search_response = search_request.execute()

            if not search_response.get("items"):
                return self._mock_analytics(query)

            video_ids = [item["id"]["videoId"] for item in search_response["items"]]
            titles = [item["snippet"]["title"] for item in search_response["items"]]
            thumbnails = [item["snippet"]["thumbnails"]["high"]["url"] for item in search_response["items"]]

            # Step B: Get statistics for those videos
            stats_request = self.youtube.videos().list(
                part="statistics,contentDetails",
                id=",".join(video_ids)
            )
            stats_response = stats_request.execute()

            # Aggregate statistics
            total_views = 0
            for item in stats_response.get("items", []):
                views = int(item["statistics"].get("viewCount", 0))
                total_views += views

            avg_views = total_views // len(video_ids) if video_ids else 0

            # Approximation given we don't have accurate CTR/view duration from public API
            # But we can provide real top titles, thumbnails, and average top view counts
            analytics_data = {
                "views": avg_views,
                "ctr": 0.08,  # Default decent CTR,
                "avg_view_duration": 45, # Default estimation
                "top_competitor_titles": titles,
                "top_competitor_thumbnails": thumbnails,
                "source": "youtube_data_api"
            }

            # Cache successful result for 24h
            await cache.set_json(cache_key, analytics_data, ttl=86400)
            logger.info("cached_youtube_analytics", query=query)
            
            return analytics_data

        except googleapiclient.errors.HttpError as e:
            logger.error("youtube_api_error", error=str(e))
            return self._mock_analytics(query)
        except Exception as e:
            logger.error("youtube_unexpected_error", error=str(e))
            return self._mock_analytics(query)

    def _mock_analytics(self, query: str) -> dict[str, Any]:
        """Return fake data if API fails or is not configured."""
        import random
        rng = random.Random(query)
        return {
            "views": rng.randint(1000, 50000),
            "ctr": round(rng.uniform(0.04, 0.12), 4),
            "avg_view_duration": rng.randint(30, 55),
            "source": "mock_static_json"
        }

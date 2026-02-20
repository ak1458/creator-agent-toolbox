from __future__ import annotations

import time

from app.agents.base import BaseAgent
from app.models.state import ContentWorkflowState
from app.services.perplexity_client import PerplexityClient
from app.services.redis_client import get_redis_cache
from app.services.youtube_client import YouTubeClient


class TrendAnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="trend_analyst")
        self.client = PerplexityClient()
        self.youtube_client = YouTubeClient()

    async def run(self, state: ContentWorkflowState) -> ContentWorkflowState:
        topic = state["topic"]
        primary_platform = state["target_platforms"][0] if state["target_platforms"] else "youtube"

        cache = await get_redis_cache()
        cache_key = f"trends:{topic}:{primary_platform}"

        # 1. Try cache first
        cached_trends = await cache.get_json(cache_key)
        if cached_trends:
            self.logger.info("using_cached_trends", topic=topic)
            trend_data = cached_trends
        else:
            self.logger.info("fetching_real_trends", topic=topic)
            # 2. Try real API
            api_trends_task = self.client.fetch_trends(topic, primary_platform)
            youtube_stats_task = self.youtube_client.get_analytics(topic)

            import asyncio
            api_trends, youtube_stats = await asyncio.gather(api_trends_task, youtube_stats_task)
            
            if api_trends:
                trend_data = api_trends
                trend_data["platform"] = primary_platform
                trend_data["source"] = "perplexity_api"
                trend_data["competitor_analysis"] = youtube_stats

                # Cache successful result for 24h
                await cache.set_json(cache_key, trend_data, ttl=86400)
                self.logger.info("cached_real_trends", topic=topic)
            else:
                self.logger.warning("perplexity_api_failed_falling_back_to_mock")
                # 3. Fallback to mock data
                trend_data = {
                    "primary_trend": "educational_hacks",
                    "confidence": 0.84,
                    "suggested_hooks": [
                        f"Stop scrolling if you care about {topic}",
                        f"The biggest mistake creators make about {topic}",
                        f"POV: You finally figured out {topic}",
                    ],
                    "audio_recommendations": ["trending_sound_stub_01", "original_audio"],
                    "saturation_level": "medium",
                    "optimal_posting_window": "18:00-20:00 EST",
                    "platform": primary_platform,
                    "source": "mock_static_json",
                    "competitor_analysis": youtube_stats
                }

        state["trend_data"] = trend_data
        state["current_step"] = "trend_analysis_complete"
        state["updated_ts"] = int(time.time())

        self.logger.info("trend_analysis_complete", workflow_id=state["workflow_id"])
        return state

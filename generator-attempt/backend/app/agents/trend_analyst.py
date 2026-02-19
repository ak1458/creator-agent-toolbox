from __future__ import annotations

import time

from app.agents.base import BaseAgent
from app.models.state import ContentWorkflowState


class TrendAnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="trend_analyst")

    async def run(self, state: ContentWorkflowState) -> ContentWorkflowState:
        topic = state["topic"]
        primary_platform = state["target_platforms"][0] if state["target_platforms"] else "youtube"

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
        }

        state["trend_data"] = trend_data
        state["current_step"] = "trend_analysis_complete"
        state["updated_ts"] = int(time.time())

        self.logger.info("trend_analysis_complete", workflow_id=state["workflow_id"])
        return state

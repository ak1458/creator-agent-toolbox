import json
from typing import Any

import httpx
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class TrendAnalysisResult(BaseModel):
    primary_trend: str
    confidence: float
    suggested_hooks: list[str]
    audio_recommendations: list[str]
    saturation_level: str
    optimal_posting_window: str


class PerplexityClient:
    """Client for fetching real-time trends using the Perplexity API."""

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.perplexity_api_key
        self.base_url = "https://api.perplexity.com/chat/completions"

    async def fetch_trends(self, topic: str, platform: str) -> dict[str, Any] | None:
        """Fetch trends from Perplexity API and return structured JSON."""
        if not self.api_key:
            logger.warning("perplexity_api_key_missing")
            return None

        prompt = f"""
        You are a social media trend analyst. Analyze the current viral trends for the topic: "{topic}" on the platform: "{platform}".
        Return ONLY a JSON object with the following schema:
        {{
            "primary_trend": "String describing the main trend currently",
            "confidence": 0.0 to 1.0 float representing your confidence,
            "suggested_hooks": ["Hook 1", "Hook 2", "Hook 3"],
            "audio_recommendations": ["Audio 1", "Audio 2"],
            "saturation_level": "low", "medium", or "high",
            "optimal_posting_window": "Time range, e.g., 18:00-20:00 EST"
        }}
        Do not include markdown blocks or any other text before/after the JSON. Just the raw JSON object.
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Use the Sonar model, configured specifically for structured search responses
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a specialized trend analyzer. Always reply with valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()

                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()
                
                # Strip markdown code blocks if the API still includes them
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                    
                parsed_json = json.loads(content.strip())
                return parsed_json

        except httpx.HTTPError as e:
            logger.error("perplexity_api_error", error=str(e))
            return None
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("perplexity_parsing_error", error=str(e), api_response=locals().get('content', ''))
            return None
        except Exception as e:
            logger.error("perplexity_unexpected_error", error=str(e))
            return None

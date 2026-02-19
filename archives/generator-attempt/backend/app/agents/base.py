from __future__ import annotations

from typing import Any

from app.core.logger import get_logger


class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(name)

    @staticmethod
    def extract_token_usage(response: Any) -> dict[str, int]:
        usage: dict[str, int] = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

        if response is None:
            return usage

        usage_metadata = getattr(response, "usage_metadata", None)
        if isinstance(usage_metadata, dict):
            usage["prompt_tokens"] = int(usage_metadata.get("input_tokens", 0))
            usage["completion_tokens"] = int(usage_metadata.get("output_tokens", 0))
            usage["total_tokens"] = int(usage_metadata.get("total_tokens", 0))
            return usage

        response_metadata = getattr(response, "response_metadata", None)
        if isinstance(response_metadata, dict):
            token_usage = response_metadata.get("token_usage", {})
            usage["prompt_tokens"] = int(token_usage.get("prompt_tokens", 0))
            usage["completion_tokens"] = int(token_usage.get("completion_tokens", 0))
            usage["total_tokens"] = int(token_usage.get("total_tokens", 0))

        return usage

    @staticmethod
    def merge_token_usage(current: dict[str, int], update: dict[str, int]) -> dict[str, int]:
        merged = {
            "prompt_tokens": int(current.get("prompt_tokens", 0)) + int(update.get("prompt_tokens", 0)),
            "completion_tokens": int(current.get("completion_tokens", 0)) + int(update.get("completion_tokens", 0)),
            "total_tokens": int(current.get("total_tokens", 0)) + int(update.get("total_tokens", 0)),
        }
        return merged

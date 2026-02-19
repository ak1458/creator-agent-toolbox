from __future__ import annotations

import json
import time
import uuid
from typing import Any

import httpx
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.models.state import ContentWorkflowState, ScriptVariant


class ScriptArchitectAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="script_architect")
        settings = get_settings()
        self.provider = settings.llm_provider
        self.model_name = settings.script_model
        self.ollama_model = settings.ollama_script_model
        self.ollama_base_url = settings.ollama_base_url.rstrip("/")
        self.ollama_timeout_seconds = settings.ollama_timeout_seconds

        self.openai_llm = None
        if self.provider == "openai" and settings.openai_api_key:
            # Support custom base URL (e.g., Groq, Azure, etc.)
            llm_kwargs = {
                "model": self.model_name,
                "temperature": 0.7,
                "api_key": settings.openai_api_key,
            }
            # Add base_url if it's not the default OpenAI URL
            if settings.openai_base_url and "openai.com" not in settings.openai_base_url:
                llm_kwargs["base_url"] = settings.openai_base_url
                self.logger.info("using_custom_openai_endpoint", base_url=settings.openai_base_url)
            
            self.openai_llm = ChatOpenAI(**llm_kwargs)
        elif self.provider == "openai":
            self.logger.warning("openai_key_missing", fallback="mock")

    async def run(self, state: ContentWorkflowState) -> ContentWorkflowState:
        variants: list[ScriptVariant]
        usage: dict[str, int] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        try:
            if self.provider == "openai" and self.openai_llm:
                variants, usage = await self._generate_with_openai(state)
            elif self.provider == "ollama":
                variants, usage = await self._generate_with_ollama(state)
            else:
                variants = self._generate_fallback_variants(state)
        except Exception as exc:  # pragma: no cover - guarded fallback
            self.logger.warning(
                "script_generation_fallback",
                workflow_id=state["workflow_id"],
                provider=self.provider,
                reason=str(exc),
            )
            variants = self._generate_fallback_variants(state)

        state["script_variants"] = variants
        state["selected_script_id"] = None
        state["human_approval_status"]["scripts_approved"] = False
        state["human_approval_status"]["scripts_rejected"] = False
        state["human_approval_status"]["thumbnails_approved"] = False
        state["thumbnail_variants"] = []
        state["selected_thumbnail_id"] = None
        state["token_usage"] = self.merge_token_usage(state.get("token_usage", {}), usage)
        state["current_step"] = "scripts_generated"
        state["updated_ts"] = int(time.time())

        self.logger.info(
            "scripts_generated",
            workflow_id=state["workflow_id"],
            variants=len(variants),
            provider=self.provider,
            tokens=state["token_usage"],
        )
        return state

    async def _generate_with_openai(
        self, state: ContentWorkflowState
    ) -> tuple[list[ScriptVariant], dict[str, int]]:
        system_prompt, user_prompt = self._build_prompts(state)

        response = await self.openai_llm.ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=json.dumps(user_prompt)),
            ]
        )

        parsed = self._parse_llm_output(response.content, state)
        usage = self.extract_token_usage(response)
        return parsed, usage

    async def _generate_with_ollama(
        self, state: ContentWorkflowState
    ) -> tuple[list[ScriptVariant], dict[str, int]]:
        system_prompt, user_prompt = self._build_prompts(state)

        payload = {
            "model": self.ollama_model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_prompt)},
            ],
            "options": {"temperature": 0.7},
        }

        async with httpx.AsyncClient(timeout=self.ollama_timeout_seconds) as client:
            response = await client.post(f"{self.ollama_base_url}/api/chat", json=payload)
            response.raise_for_status()
            response_json = response.json()

        content = str((response_json.get("message") or {}).get("content") or "")
        parsed = self._parse_llm_output(content, state)
        usage = {
            "prompt_tokens": int(response_json.get("prompt_eval_count", 0)),
            "completion_tokens": int(response_json.get("eval_count", 0)),
            "total_tokens": int(response_json.get("prompt_eval_count", 0))
            + int(response_json.get("eval_count", 0)),
        }
        return parsed, usage

    def _build_prompts(self, state: ContentWorkflowState) -> tuple[str, dict[str, Any]]:
        trend_data = state.get("trend_data") or {}

        system_prompt = (
            "You are a short-form script architect. Return ONLY valid JSON with key 'variants'. "
            "Generate exactly 3 distinct 60-second scripts. "
            "Each item must include id, tone, hook, body, cta, predicted_retention."
        )

        user_prompt = {
            "topic": state["topic"],
            "platforms": state["target_platforms"],
            "trend_data": trend_data,
            "constraints": {
                "variant_a": "pattern_interrupt",
                "variant_b": "curiosity_gap",
                "variant_c": "authority_play",
            },
        }

        return system_prompt, user_prompt

    def _parse_llm_output(self, content: Any, state: ContentWorkflowState) -> list[ScriptVariant]:
        if isinstance(content, list):
            content = "\n".join(str(item) for item in content)

        text = str(content)
        data = self._safe_json_load(text)
        variants = data.get("variants", [])

        normalized: list[ScriptVariant] = []
        for item in variants[:3]:
            retention = float(item.get("predicted_retention") or 0.75)
            if retention < 0.60:
                retention = 0.60
            if retention > 0.90:
                retention = 0.90
            normalized.append(
                {
                    "id": str(item.get("id") or uuid.uuid4()),
                    "tone": str(item.get("tone") or "custom"),
                    "hook": str(item.get("hook") or f"Here is what matters about {state['topic']}"),
                    "body": str(item.get("body") or f"Breaking down the key insight for {state['topic']}."),
                    "cta": str(item.get("cta") or "Follow for more."),
                    "predicted_retention": retention,
                }
            )

        if len(normalized) != 3:
            return self._generate_fallback_variants(state)

        return normalized

    @staticmethod
    def _safe_json_load(text: str) -> dict[str, Any]:
        candidate = text.strip()

        if candidate.startswith("```"):
            lines = candidate.splitlines()
            lines = [line for line in lines if not line.strip().startswith("```")]
            candidate = "\n".join(lines).strip()

        try:
            loaded = json.loads(candidate)
            if isinstance(loaded, dict):
                return loaded
        except json.JSONDecodeError:
            pass

        start = candidate.find("{")
        end = candidate.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Unable to parse JSON response from model")

        loaded = json.loads(candidate[start : end + 1])
        if not isinstance(loaded, dict):
            raise ValueError("Parsed response is not a JSON object")
        return loaded

    def _generate_fallback_variants(self, state: ContentWorkflowState) -> list[ScriptVariant]:
        topic = state["topic"]
        hooks = (state.get("trend_data") or {}).get("suggested_hooks", [])

        def hook_at(index: int, default: str) -> str:
            return hooks[index] if index < len(hooks) else default

        return [
            {
                "id": str(uuid.uuid4()),
                "tone": "pattern_interrupt",
                "hook": hook_at(0, f"You are doing {topic} wrong."),
                "body": f"Most creators miss this: one concrete mistake in {topic}, then the fix in 3 steps.",
                "cta": "Comment 'fix' and I will share the checklist.",
                "predicted_retention": 0.78,
            },
            {
                "id": str(uuid.uuid4()),
                "tone": "curiosity_gap",
                "hook": hook_at(1, f"I found the hidden shortcut for {topic}."),
                "body": f"Set up the problem, tease the missing piece, reveal it with a quick before/after.",
                "cta": "Save this for your next post.",
                "predicted_retention": 0.81,
            },
            {
                "id": str(uuid.uuid4()),
                "tone": "authority_play",
                "hook": hook_at(2, f"As a creator, here is what actually works for {topic}."),
                "body": "Use one proof point, one framework, then one tactical action viewers can apply today.",
                "cta": "Follow for weekly breakdowns.",
                "predicted_retention": 0.76,
            },
        ]

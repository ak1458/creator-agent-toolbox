from __future__ import annotations

import hashlib
import time
import uuid
from urllib.parse import quote, urlencode

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.models.state import ContentWorkflowState, ScriptVariant, ThumbnailVariant


class VisualEngineerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="visual_engineer")
        settings = get_settings()
        self.pollinations_base_url = settings.pollinations_base_url.rstrip("/")
        self.thumbnail_width = settings.thumbnail_width
        self.thumbnail_height = settings.thumbnail_height

    async def run(self, state: ContentWorkflowState) -> ContentWorkflowState:
        script = self._resolve_script(state)
        hook = script.get("hook", f"{state['topic']} explained")

        prompt_specs = [
            (
                "face_focused",
                f"Close-up expressive creator face, cinematic lighting, dramatic emotion, topic {state['topic']}. Hook text: {hook}.",
            ),
            (
                "product_focused",
                f"Hero product/object composition, clean background, high contrast, visual metaphor for {state['topic']}. Hook text: {hook}.",
            ),
            (
                "text_heavy",
                f"Bold typography thumbnail with 3-5 punchy words, dynamic arrows/shapes, clear hierarchy around {state['topic']}. Hook text: {hook}.",
            ),
        ]

        thumbnails: list[ThumbnailVariant] = []
        for index, (style, visual_direction) in enumerate(prompt_specs):
            prompt = (
                "YouTube thumbnail, 16:9, ultra-sharp, high CTR composition, "
                "no watermark, no logos, no signatures. "
                f"{visual_direction}"
            )
            seed = self._seed_for(state["workflow_id"], index)
            thumbnails.append(
                {
                    "id": str(uuid.uuid4()),
                    "style": style,
                    "prompt": prompt,
                    "image_url": self._build_image_url(prompt, seed),
                    "seed": seed,
                }
            )

        state["thumbnail_variants"] = thumbnails
        state["selected_thumbnail_id"] = None
        state["human_approval_status"]["thumbnails_approved"] = False
        state["current_step"] = "thumbnails_generated"
        state["updated_ts"] = int(time.time())

        self.logger.info("thumbnails_generated", workflow_id=state["workflow_id"], variants=3)
        return state

    @staticmethod
    def _resolve_script(state: ContentWorkflowState) -> ScriptVariant:
        selected_script_id = state.get("selected_script_id")
        scripts = state.get("script_variants", [])

        if selected_script_id:
            for script in scripts:
                if script.get("id") == selected_script_id:
                    return script

        if scripts:
            return scripts[0]

        return {
            "id": str(uuid.uuid4()),
            "hook": f"{state['topic']} made simple",
            "body": f"Practical explanation for {state['topic']}.",
            "cta": "Follow for more.",
            "predicted_retention": 0.75,
            "tone": "fallback",
        }

    def _build_image_url(self, prompt: str, seed: int) -> str:
        encoded_prompt = quote(prompt, safe="")
        query = urlencode(
            {
                "seed": seed,
                "width": self.thumbnail_width,
                "height": self.thumbnail_height,
                "nologo": "true",
                "enhance": "true",
            }
        )
        return f"{self.pollinations_base_url}/{encoded_prompt}?{query}"

    @staticmethod
    def _seed_for(workflow_id: str, index: int) -> int:
        digest = hashlib.sha256(f"{workflow_id}:{index}".encode("utf-8")).hexdigest()
        seed = int(digest[:8], 16)
        return max(1, seed)

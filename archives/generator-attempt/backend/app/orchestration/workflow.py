from __future__ import annotations

import time
from pathlib import Path
from typing import Literal

from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.agents.ab_test_orchestrator import ABTestOrchestratorAgent
from app.agents.script_architect import ScriptArchitectAgent
from app.agents.trend_analyst import TrendAnalystAgent
from app.agents.visual_engineer import VisualEngineerAgent
from app.core.config import get_settings
from app.core.logger import get_logger
from app.models.state import ContentWorkflowState


class ContentWorkflow:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.settings = get_settings()

        self.trend_analyst = TrendAnalystAgent()
        self.script_architect = ScriptArchitectAgent()
        self.visual_engineer = VisualEngineerAgent()
        self.ab_orchestrator = ABTestOrchestratorAgent()

        self.builder = StateGraph(ContentWorkflowState)
        self._build_graph()

        self._checkpointer_cm = None
        self._checkpointer = None
        self.app = None

    async def initialize(self) -> None:
        if self.app is not None:
            return

        checkpoint_target = self._checkpoint_target(self.settings.checkpoint_db_url)
        Path(checkpoint_target).parent.mkdir(parents=True, exist_ok=True)

        try:
            self._checkpointer_cm = AsyncSqliteSaver.from_conn_string(checkpoint_target)
            if hasattr(self._checkpointer_cm, "__aenter__"):
                self._checkpointer = await self._checkpointer_cm.__aenter__()
            else:  # pragma: no cover - compatibility fallback
                self._checkpointer = self._checkpointer_cm
        except Exception as exc:  # pragma: no cover - startup fallback
            self.logger.warning("checkpointer_fallback", reason=str(exc))
            self._checkpointer_cm = None
            self._checkpointer = MemorySaver()

        self.app = self.builder.compile(checkpointer=self._checkpointer)
        self.logger.info("workflow_initialized", checkpoint=checkpoint_target)

    async def close(self) -> None:
        if self._checkpointer_cm and hasattr(self._checkpointer_cm, "__aexit__"):
            await self._checkpointer_cm.__aexit__(None, None, None)

    async def run(self, state: ContentWorkflowState, thread_id: str) -> ContentWorkflowState:
        if self.app is None:
            await self.initialize()

        config = {"configurable": {"thread_id": thread_id}}
        result = await self.app.ainvoke(state, config=config)
        return result

    def _build_graph(self) -> None:
        self.builder.add_node("entry_router", self._entry_router)
        self.builder.add_node("analyze_trends", self.trend_analyst.run)
        self.builder.add_node("generate_scripts", self.script_architect.run)
        self.builder.add_node("human_gate_scripts", self._human_gate_scripts)
        self.builder.add_node("generate_thumbnails", self.visual_engineer.run)
        self.builder.add_node("human_gate_thumbnails", self._human_gate_thumbnails)
        self.builder.add_node("run_ab_test", self._run_ab_test)
        self.builder.add_node("check_ab_status", self._check_ab_status)
        self.builder.add_node("finalize", self._finalize)

        self.builder.set_entry_point("entry_router")

        self.builder.add_conditional_edges(
            "entry_router",
            self._route_from_entry,
            {
                "from_start": "analyze_trends",
                "from_script_gate": "human_gate_scripts",
                "from_thumbnail_gate": "human_gate_thumbnails",
                "from_ab_test": "run_ab_test",
            },
        )

        self.builder.add_edge("analyze_trends", "generate_scripts")
        self.builder.add_edge("generate_scripts", "human_gate_scripts")

        self.builder.add_conditional_edges(
            "human_gate_scripts",
            self._route_after_script_gate,
            {
                "approved": "generate_thumbnails",
                "rejected": "generate_scripts",
                "pending": END,
            },
        )

        self.builder.add_edge("generate_thumbnails", "human_gate_thumbnails")
        self.builder.add_conditional_edges(
            "human_gate_thumbnails",
            self._route_after_thumbnail_gate,
            {
                "selected": "run_ab_test",
                "pending": END,
            },
        )

        # A/B Test loop
        self.builder.add_edge("run_ab_test", "check_ab_status")
        self.builder.add_conditional_edges(
            "check_ab_status",
            self._route_after_ab_check,
            {
                "running": END,  # Exit to allow polling, will re-enter via entry_router
                "completed": "finalize",
                "error": END,
            },
        )

        self.builder.add_edge("finalize", END)

    async def _entry_router(self, state: ContentWorkflowState) -> ContentWorkflowState:
        state["updated_ts"] = int(time.time())
        return state

    def _route_from_entry(
        self, state: ContentWorkflowState
    ) -> Literal["from_start", "from_script_gate", "from_thumbnail_gate", "from_ab_test"]:
        approval = state.get("human_approval_status", {})
        has_scripts = bool(state.get("script_variants"))
        has_thumbnails = bool(state.get("thumbnail_variants"))
        selected_thumbnail = state.get("selected_thumbnail_id")
        ab_test = state.get("ab_test")

        # Check if we're in A/B testing phase
        if ab_test is not None:
            return "from_ab_test"

        if state.get("current_step") in ["ab_testing", "ab_test_complete"]:
            return "from_ab_test"

        if selected_thumbnail and ab_test is None:
            # Just selected thumbnail, need to start AB test
            return "from_thumbnail_gate"

        if state.get("current_step") == "awaiting_thumbnail_selection":
            return "from_thumbnail_gate"

        if has_thumbnails and approval.get("scripts_approved"):
            return "from_thumbnail_gate"

        if has_scripts:
            return "from_script_gate"

        if approval.get("scripts_approved") or approval.get("scripts_rejected"):
            return "from_script_gate"

        return "from_start"

    async def _human_gate_scripts(self, state: ContentWorkflowState) -> ContentWorkflowState:
        approval = state.get("human_approval_status", {})

        if approval.get("scripts_approved"):
            state["current_step"] = "approved"
        elif approval.get("scripts_rejected"):
            state["current_step"] = "scripts_rejected"
            state["thumbnail_variants"] = []
            state["selected_thumbnail_id"] = None
            state["human_approval_status"]["thumbnails_approved"] = False
        else:
            state["current_step"] = "awaiting_approval"

        state["updated_ts"] = int(time.time())
        return state

    def _route_after_script_gate(
        self, state: ContentWorkflowState
    ) -> Literal["approved", "rejected", "pending"]:
        approval = state.get("human_approval_status", {})
        if approval.get("scripts_approved"):
            return "approved"
        if approval.get("scripts_rejected"):
            return "rejected"
        return "pending"

    async def _human_gate_thumbnails(self, state: ContentWorkflowState) -> ContentWorkflowState:
        selected_thumbnail_id = state.get("selected_thumbnail_id")

        if selected_thumbnail_id:
            state["human_approval_status"]["thumbnails_approved"] = True
            state["current_step"] = "thumbnail_selected"
        else:
            state["human_approval_status"]["thumbnails_approved"] = False
            state["current_step"] = "awaiting_thumbnail_selection"

        state["updated_ts"] = int(time.time())
        return state

    def _route_after_thumbnail_gate(self, state: ContentWorkflowState) -> Literal["selected", "pending"]:
        if state.get("selected_thumbnail_id"):
            return "selected"
        return "pending"

    async def _run_ab_test(self, state: ContentWorkflowState) -> ContentWorkflowState:
        """Execute one iteration of A/B test (initialize or update)"""
        return await self.ab_orchestrator.process(state)

    async def _check_ab_status(self, state: ContentWorkflowState) -> ContentWorkflowState:
        """Check A/B test status - node just passes through"""
        state["updated_ts"] = int(time.time())
        return state

    def _route_after_ab_check(
        self, state: ContentWorkflowState
    ) -> Literal["running", "completed", "error"]:
        """Check if A/B test should continue or end"""
        ab_test = state.get("ab_test", {})
        status = ab_test.get("status", "running") if ab_test else "running"

        if status in ["completed", "timeout", "manual_override"]:
            return "completed"
        elif state.get("errors"):
            return "error"
        else:
            return "running"

    async def _finalize(self, state: ContentWorkflowState) -> ContentWorkflowState:
        """Finalize workflow with winner"""
        state["current_step"] = "completed"
        # Ensure selected_thumbnail_id is set to winner
        if state.get("ab_test", {}).get("winner_id"):
            state["selected_thumbnail_id"] = state["ab_test"]["winner_id"]
        state["updated_ts"] = int(time.time())
        return state

    @staticmethod
    def _checkpoint_target(conn: str) -> str:
        prefix = "sqlite+aiosqlite:///"
        if conn.startswith(prefix):
            return conn.replace(prefix, "", 1)
        return conn

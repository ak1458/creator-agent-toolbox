import time
from typing import Any, Dict, Optional

from app.agents.base import BaseAgent
from app.services.analytics_mock import MockAnalyticsProvider
from app.services.statistics import ABTestStatistics


class ABTestOrchestratorAgent(BaseAgent):
    """
    Manages A/B test lifecycle:
    - Initialize experiment
    - Poll for metrics (simulated)
    - Check statistical significance
    - Declare winner or timeout
    """

    def __init__(self):
        super().__init__(name="ab_test_orchestrator")
        self.statistics = ABTestStatistics()
        self.check_interval_seconds = 30  # Check every 30s (accelerated for demo)
        self.max_test_duration_hours = 72  # Auto-stop after 72h

    def log_step(self, step: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log a step in the AB test process."""
        self.logger.info(
            f"ab_test_{step}",
            step=step,
            **(extra or {}),
        )

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point - called when entering ab_test node"""

        if "ab_test" not in state or state["ab_test"] is None:
            # Initialize new test
            state = await self._initialize_test(state)
        else:
            # Continue existing test
            state = await self._update_test(state)

        return state

    async def _initialize_test(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Set up initial test state"""
        self.log_step("initialize_ab_test")

        thumbnails = state.get("thumbnail_variants", [])
        if not thumbnails or len(thumbnails) < 2:
            state["errors"].append("Need at least 2 thumbnails for A/B test")
            state["current_step"] = "error"
            return state

        # Initialize metrics for all variants
        variants_metrics = [
            {
                "thumbnail_id": t["id"],
                "style": t["style"],
                "impressions": 0,
                "clicks": 0,
                "ctr": 0.0,
                "avg_view_duration": 0,
            }
            for t in thumbnails
        ]

        state["ab_test"] = {
            "started_at": time.time(),
            "last_updated": time.time(),
            "status": "running",
            "variants": variants_metrics,
            "winner_id": None,
            "confidence": 0.0,
            "total_impressions": 0,
            "check_count": 0,
        }

        state["current_step"] = "ab_testing"
        return state

    async def _update_test(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Update metrics and check for significance"""
        ab_test = state["ab_test"]
        thumbnails = state.get("thumbnail_variants", [])

        # Calculate elapsed time
        elapsed_seconds = time.time() - ab_test["started_at"]
        elapsed_minutes = elapsed_seconds / 60

        # Get mock analytics
        provider = MockAnalyticsProvider(state["workflow_id"])
        current_metrics = await provider.simulate_batch(thumbnails, int(elapsed_minutes))

        # Update state with new metrics
        ab_test["variants"] = current_metrics
        ab_test["last_updated"] = time.time()
        ab_test["check_count"] += 1
        ab_test["total_impressions"] = sum(v["impressions"] for v in current_metrics)

        # Check for statistical significance (compare best vs control)
        stats_result = self.statistics.calculate_multi_variant(current_metrics)

        ab_test["confidence"] = stats_result.get("winner_confidence", 0.0)

        # Determine if we should declare winner
        recommendation = stats_result.get("recommendation", "wait")

        if recommendation == "declare_winner" and stats_result.get("winner_id"):
            ab_test["winner_id"] = stats_result["winner_id"]
            ab_test["status"] = "completed"
            ab_test["final_stats"] = stats_result
            state["current_step"] = "ab_test_complete"
            self.log_step(
                "winner_declared",
                {
                    "winner_id": stats_result["winner_id"],
                    "confidence": ab_test["confidence"],
                    "uplift": stats_result.get("uplift", 0),
                },
            )

        elif elapsed_minutes > (self.max_test_duration_hours * 60):
            # Timeout - pick best performer even if not significant
            best = max(current_metrics, key=lambda x: x["ctr"])
            ab_test["winner_id"] = best["thumbnail_id"]
            ab_test["status"] = "timeout"
            ab_test["final_stats"] = {"reason": "timeout", "best_ctr": best["ctr"]}
            state["current_step"] = "ab_test_complete"
            self.log_step("timeout_declared", {"winner_id": best["thumbnail_id"]})

        else:
            # Continue testing
            state["current_step"] = "ab_testing"
            self.log_step(
                "test_continues",
                {
                    "check": ab_test["check_count"],
                    "confidence": ab_test["confidence"],
                    "impressions": ab_test["total_impressions"],
                },
            )

        return state

    async def force_winner(self, state: Dict[str, Any], thumbnail_id: str) -> Dict[str, Any]:
        """Manual override for human decision"""
        if "ab_test" in state and state["ab_test"]:
            state["ab_test"]["winner_id"] = thumbnail_id
            state["ab_test"]["status"] = "manual_override"
            state["ab_test"]["final_stats"] = {"reason": "manual_override"}
            state["current_step"] = "ab_test_complete"
        return state

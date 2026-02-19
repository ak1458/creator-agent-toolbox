import random
import hashlib
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class MockMetrics:
    impressions: int
    clicks: int
    ctr: float
    avg_view_duration: int  # seconds
    engagement_rate: float  # likes + comments / views


class MockAnalyticsProvider:
    """
    Simulates YouTube Analytics API with realistic CTR distributions.
    Deterministic per workflow_id (same inputs = same outputs for testing).
    """

    # Baseline CTRs by thumbnail style (research-backed approximations)
    STYLE_BASELINES = {
        "face_focus": {"ctr_mean": 0.085, "ctr_std": 0.015, "view_duration": 45},
        "face_focused": {"ctr_mean": 0.085, "ctr_std": 0.015, "view_duration": 45},
        "product_demo": {"ctr_mean": 0.062, "ctr_std": 0.012, "view_duration": 38},
        "product_focused": {"ctr_mean": 0.062, "ctr_std": 0.012, "view_duration": 38},
        "viral": {"ctr_mean": 0.095, "ctr_std": 0.025, "view_duration": 52},  # Higher variance
        "text_heavy": {"ctr_mean": 0.058, "ctr_std": 0.010, "view_duration": 35},
    }

    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        # Seed random for deterministic results per workflow
        self.seed = int(hashlib.md5(workflow_id.encode()).hexdigest(), 16)
        self.rng = random.Random(self.seed)

    async def get_metrics(self, thumbnail_id: str, style: str, elapsed_minutes: int) -> MockMetrics:
        """
        Simulates metrics accumulation over time.
        elapsed_minutes: how long the test has been running
        """
        baseline = self.STYLE_BASELINES.get(style, self.STYLE_BASELINES["face_focus"])

        # Simulate impressions growing over time (viral curve)
        # First hour: slow, then acceleration, then plateau
        if elapsed_minutes < 60:
            impressions = int(elapsed_minutes * self.rng.gauss(50, 10))
        elif elapsed_minutes < 360:
            impressions = int(3000 + (elapsed_minutes - 60) * self.rng.gauss(80, 15))
        else:
            impressions = int(30000 + (elapsed_minutes - 360) * self.rng.gauss(20, 5))

        # CTR converges to true value over time (law of large numbers simulation)
        true_ctr = self.rng.gauss(baseline["ctr_mean"], baseline["ctr_std"])
        # Early data has more variance
        noise_factor = max(0.1, 1.0 - (elapsed_minutes / 1440))  # Decreases over 24h
        observed_ctr = true_ctr + self.rng.gauss(0, baseline["ctr_std"] * noise_factor)
        observed_ctr = max(0.01, min(0.35, observed_ctr))  # Clamp realistic bounds

        clicks = int(impressions * observed_ctr)
        avg_duration = int(self.rng.gauss(baseline["view_duration"], 8))

        return MockMetrics(
            impressions=max(100, impressions),
            clicks=max(1, clicks),
            ctr=round(observed_ctr, 4),
            avg_view_duration=avg_duration,
            engagement_rate=round(self.rng.gauss(0.04, 0.01), 4),
        )

    async def simulate_batch(self, variants: List[Dict], test_duration_minutes: int) -> List[Dict]:
        """Get current metrics for all variants"""
        results = []
        for variant in variants:
            metrics = await self.get_metrics(
                variant["id"],
                variant["style"],
                test_duration_minutes,
            )
            results.append(
                {
                    "thumbnail_id": variant["id"],
                    "style": variant["style"],
                    "impressions": metrics.impressions,
                    "clicks": metrics.clicks,
                    "ctr": metrics.ctr,
                    "avg_view_duration": metrics.avg_view_duration,
                    "confidence": 0.0,  # Will be calculated separately
                }
            )
        return results

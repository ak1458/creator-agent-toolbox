import math
from typing import Optional, Dict, Literal, List
from dataclasses import dataclass


@dataclass
class SignificanceResult:
    winner_id: Optional[str]
    winner_confidence: float  # 0.0 to 1.0
    is_significant: bool
    uplift: float  # percentage improvement
    recommendation: Literal["wait", "declare_winner", "inconclusive"]
    p_value: float


class ABTestStatistics:
    """
    Statistical significance testing for A/B tests using Z-test for proportions.
    """

    @staticmethod
    def calculate_significance(
        control_clicks: int,
        control_impressions: int,
        treatment_clicks: int,
        treatment_impressions: int,
        min_confidence: float = 0.95,
    ) -> SignificanceResult:
        """
        Two-proportion Z-test.
        Returns significance result with winner determination.
        """
        # Prevent division by zero
        if control_impressions == 0 or treatment_impressions == 0:
            return SignificanceResult(
                winner_id=None,
                winner_confidence=0.0,
                is_significant=False,
                uplift=0.0,
                recommendation="wait",
                p_value=1.0,
            )

        # Calculate proportions
        p1 = control_clicks / control_impressions
        p2 = treatment_clicks / treatment_impressions

        # Pooled proportion
        p_pool = (control_clicks + treatment_clicks) / (control_impressions + treatment_impressions)

        # Standard error
        se = math.sqrt(p_pool * (1 - p_pool) * (1 / control_impressions + 1 / treatment_impressions))

        if se == 0:
            return SignificanceResult(
                winner_id=None,
                winner_confidence=0.0,
                is_significant=False,
                uplift=0.0,
                recommendation="wait",
                p_value=1.0,
            )

        # Z-score
        z = (p2 - p1) / se

        # Two-tailed p-value
        p_value = 2 * (1 - ABTestStatistics._normal_cdf(abs(z)))

        # Confidence level
        confidence = 1 - p_value

        # Determine winner (if significant)
        winner_id = None
        uplift = 0.0

        if confidence >= min_confidence:
            if p2 > p1:
                winner_id = "treatment"  # Will map to actual ID externally
                uplift = (p2 - p1) / p1 if p1 > 0 else 0
            else:
                winner_id = "control"
                uplift = (p1 - p2) / p2 if p2 > 0 else 0

        # Recommendation logic
        if confidence >= min_confidence:
            recommendation = "declare_winner"
        elif control_impressions < 1000 or treatment_impressions < 1000:
            recommendation = "wait"  # Need more data
        else:
            recommendation = "inconclusive"  # Enough data, no significant difference

        return SignificanceResult(
            winner_id=winner_id,
            winner_confidence=confidence,
            is_significant=confidence >= min_confidence,
            uplift=round(uplift, 4),
            recommendation=recommendation,
            p_value=round(p_value, 6),
        )

    @staticmethod
    def _normal_cdf(x: float) -> float:
        """
        Approximation of standard normal CDF (Abramowitz and Stegun).
        """
        # Constants
        a1 = 0.254829592
        a2 = -0.284496736
        a3 = 1.421413741
        a4 = -1.453152027
        a5 = 1.061405429
        p = 0.3275911

        sign = 1 if x >= 0 else -1
        x = abs(x) / math.sqrt(2.0)

        t = 1.0 / (1.0 + p * x)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)

        return 0.5 * (1.0 + sign * y)

    @staticmethod
    def calculate_multi_variant(
        variants: List[Dict],
        min_confidence: float = 0.95,
    ) -> Dict:
        """
        For >2 variants, compare best performer against control (first variant).
        Returns winner analysis.
        """
        if len(variants) < 2:
            return {"error": "Need at least 2 variants"}

        # Sort by CTR to find best performer
        sorted_variants = sorted(variants, key=lambda x: x["ctr"], reverse=True)
        best = sorted_variants[0]
        control = variants[0]  # Assume first is control

        # If best is control, compare control vs second best
        if best["thumbnail_id"] == control["thumbnail_id"] and len(variants) > 1:
            best = sorted_variants[1]

        result = ABTestStatistics.calculate_significance(
            control_clicks=control["clicks"],
            control_impressions=control["impressions"],
            treatment_clicks=best["clicks"],
            treatment_impressions=best["impressions"],
            min_confidence=min_confidence,
        )

        # Map generic winner_id to actual thumbnail_id
        winner_thumbnail_id = None
        if result.winner_id == "treatment":
            winner_thumbnail_id = best["thumbnail_id"]
        elif result.winner_id == "control":
            winner_thumbnail_id = control["thumbnail_id"]

        return {
            "comparison": f"{control['thumbnail_id']} vs {best['thumbnail_id']}",
            "control_ctr": control["ctr"],
            "treatment_ctr": best["ctr"],
            "winner_id": winner_thumbnail_id,
            "winner_confidence": result.winner_confidence,
            "is_significant": result.is_significant,
            "uplift": result.uplift,
            "recommendation": result.recommendation,
            "p_value": result.p_value,
        }

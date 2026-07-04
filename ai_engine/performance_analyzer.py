"""
ai_engine/performance_analyzer.py
Computes 0-100 health score for every campaign.
No ML frameworks. Pure math.
"""
import logging
from config.constants import (
    HEALTH_WEIGHT_ROI, HEALTH_WEIGHT_CTR, HEALTH_WEIGHT_CPC,
    BENCHMARK_CTR_GOOD, BENCHMARK_CTR_POOR,
    BENCHMARK_ROI_GOOD, BENCHMARK_ROI_POOR,
    BENCHMARK_CPC_HIGH
)
from database.repositories.analytics_repository import AnalyticsRepository
from database.repositories.campaign_repository import CampaignRepository

logger = logging.getLogger("ai_engine.performance_analyzer")


def _score_ctr(ctr: float) -> float:
    """Convert CTR% to 0-100 score."""
    if ctr >= BENCHMARK_CTR_GOOD:
        return min(100.0, 50 + (ctr - BENCHMARK_CTR_GOOD) * 20)
    elif ctr >= BENCHMARK_CTR_POOR:
        return 50 * (ctr - BENCHMARK_CTR_POOR) / (BENCHMARK_CTR_GOOD - BENCHMARK_CTR_POOR)
    return max(0.0, ctr * 10)


def _score_roi(roi: float) -> float:
    """Convert ROI multiplier to 0-100 score."""
    if roi >= BENCHMARK_ROI_GOOD:
        return min(100.0, 50 + (roi - BENCHMARK_ROI_GOOD) * 15)
    elif roi >= BENCHMARK_ROI_POOR:
        return 50 * (roi - BENCHMARK_ROI_POOR)
    return 0.0


def _score_cpc(cpc: float) -> float:
    """Lower CPC = better score."""
    if cpc <= 0:
        return 50.0
    if cpc <= 10:
        return 100.0
    if cpc >= BENCHMARK_CPC_HIGH:
        return max(0.0, 100 - (cpc - 10) * 2)
    return max(0.0, 100 - cpc)


class PerformanceAnalyzer:

    def __init__(self):
        self.analytics_repo = AnalyticsRepository()
        self.camp_repo      = CampaignRepository()

    def compute_health_score(self, campaign_id: int, days: int = 7) -> float:
        """
        Compute 0-100 health score for one campaign.
        Weights: ROI 40%, CTR 30%, CPC 30%
        """
        summary = self.analytics_repo.get_campaign_summary(campaign_id)
        if not summary or not summary.get("avg_ctr"):
            return 0.0

        ctr_score = _score_ctr(summary.get("avg_ctr", 0))
        roi_score = _score_roi(summary.get("avg_roi", 0))
        cpc_score = _score_cpc(summary.get("avg_cpc", 0))

        health = (
            ctr_score * HEALTH_WEIGHT_CTR +
            roi_score * HEALTH_WEIGHT_ROI +
            cpc_score * HEALTH_WEIGHT_CPC
        )
        return round(min(100.0, max(0.0, health)), 2)

    def score_all_campaigns(self) -> list[dict]:
        """Score every campaign and save to DB. Returns list of results."""
        campaigns = self.camp_repo.get_all()
        results   = []
        for camp in campaigns:
            score = self.compute_health_score(camp["id"])
            self.camp_repo.update_health_score(camp["id"], score)
            results.append({"id": camp["id"], "name": camp["name"],
                            "health_score": score})
            logger.info("Health score: %s → %.1f", camp["name"], score)
        return results
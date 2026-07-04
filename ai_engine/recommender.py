"""
ai_engine/recommender.py
Generates actionable recommendations for each campaign.
"""
import logging
from database.repositories.analytics_repository import AnalyticsRepository
from database.repositories.campaign_repository import CampaignRepository
from database.repositories.base_repository import BaseRepository
from config.constants import BENCHMARK_ROI_GOOD, BENCHMARK_CTR_POOR, BENCHMARK_CPC_HIGH

logger = logging.getLogger("ai_engine.recommender")


class Recommender:

    def __init__(self):
        self.analytics_repo = AnalyticsRepository()
        self.camp_repo      = CampaignRepository()

    def recommend_all(self) -> list[dict]:
        """Generate recommendations for all campaigns."""
        recommendations = []
        campaigns = self.camp_repo.get_all()
        for camp in campaigns:
            rec = self.recommend_for_campaign(camp)
            if rec:
                recommendations.append(rec)
        return recommendations

    def recommend_for_campaign(self, camp: dict) -> dict | None:
        """
        Analyse one campaign and return a recommendation dict, or None
        if the campaign is performing well and needs no action.
        """
        summary = self.analytics_repo.get_campaign_summary(camp["id"])
        if not summary:
            return None

        avg_roi = summary.get("avg_roi", 0) or 0
        avg_ctr = summary.get("avg_ctr", 0) or 0
        avg_cpc = summary.get("avg_cpc", 0) or 0

        # ── Great campaign: recommend budget increase ──────────────────────────
        if avg_roi >= BENCHMARK_ROI_GOOD and avg_ctr >= 2.0:
            return {
                "campaign_id":    camp["id"],
                "campaign_name":  camp["name"],
                "platform":       camp["platform"],
                "decision_type":  "recommend",
                "title":          "Increase Budget",
                "reason":         f"ROI is {avg_roi:.1f}x and CTR is {avg_ctr:.2f}% — well above benchmarks.",
                "suggested_action": "Increase daily budget by 20-30% to scale results.",
                "expected_impact":  "Projected 20-30% increase in conversions.",
                "confidence":     0.87,
            }

        # ── Losing money: recommend pause ─────────────────────────────────────
        if avg_roi < 1.0 and camp["status"] == "active":
            return {
                "campaign_id":    camp["id"],
                "campaign_name":  camp["name"],
                "platform":       camp["platform"],
                "decision_type":  "recommend",
                "title":          "Pause Campaign — Negative ROI",
                "reason":         f"ROI is {avg_roi:.2f}x. Spending more than earning.",
                "suggested_action": "Pause immediately. Review targeting and creatives.",
                "expected_impact":  f"Save ₹{camp.get('daily_budget', 0):.0f}/day until fixed.",
                "confidence":     0.92,
            }

        # ── High CPC: cost issue ───────────────────────────────────────────────
        if avg_cpc >= BENCHMARK_CPC_HIGH:
            return {
                "campaign_id":    camp["id"],
                "campaign_name":  camp["name"],
                "platform":       camp["platform"],
                "decision_type":  "recommend",
                "title":          "Reduce CPC — Too Expensive",
                "reason":         f"CPC is ₹{avg_cpc:.2f} — above ₹{BENCHMARK_CPC_HIGH} benchmark.",
                "suggested_action": "Add negative keywords, tighten audience targeting.",
                "expected_impact":  "Expected 15-25% CPC reduction.",
                "confidence":     0.78,
            }

        # ── Low CTR: ad relevance issue ───────────────────────────────────────
        if avg_ctr < BENCHMARK_CTR_POOR:
            return {
                "campaign_id":    camp["id"],
                "campaign_name":  camp["name"],
                "platform":       camp["platform"],
                "decision_type":  "recommend",
                "title":          "Improve Ad Creative — Low CTR",
                "reason":         f"CTR is {avg_ctr:.2f}% — below {BENCHMARK_CTR_POOR}% minimum.",
                "suggested_action": "A/B test new headlines and ad copy.",
                "expected_impact":  "Expected 2x CTR improvement with fresh creatives.",
                "confidence":     0.74,
            }

        return None
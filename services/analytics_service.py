"""
services/analytics_service.py
Computes KPIs, trends, comparisons for analytics dashboard.
"""
import logging
from database.repositories.analytics_repository import AnalyticsRepository
from database.repositories.campaign_repository import CampaignRepository

logger = logging.getLogger(__name__)


class AnalyticsService:

    def __init__(self):
        self.analytics_repo = AnalyticsRepository()
        self.camp_repo      = CampaignRepository()

    def get_dashboard_kpis(self, days: int = 30) -> dict:
        rows   = self.analytics_repo.get_all_platform_summary(days)
        totals = {
            "total_spend": 0.0, "total_revenue": 0.0,
            "total_clicks": 0,  "total_impressions": 0,
            "total_conversions": 0, "avg_roi": 0.0,
            "avg_ctr": 0.0, "platforms": []
        }
        for row in rows:
            totals["total_spend"]       += row.get("total_spend", 0) or 0
            totals["total_revenue"]     += row.get("total_revenue", 0) or 0
            totals["total_clicks"]      += row.get("total_clicks", 0) or 0
            totals["total_impressions"] += row.get("total_impressions", 0) or 0
            totals["total_conversions"] += row.get("total_conversions", 0) or 0
            totals["platforms"].append(row)

        if totals["total_spend"] > 0:
            totals["avg_roi"] = round(
                totals["total_revenue"] / totals["total_spend"], 2
            )
        if totals["total_impressions"] > 0:
            totals["avg_ctr"] = round(
                totals["total_clicks"] / totals["total_impressions"] * 100, 2
            )

        totals["total_spend"]   = round(totals["total_spend"], 2)
        totals["total_revenue"] = round(totals["total_revenue"], 2)
        return totals

    def get_daily_trend(self, days: int = 30) -> list[dict]:
        return self.analytics_repo.get_daily_totals(days)

    def get_top_campaigns(self, days: int = 30) -> list[dict]:
        return self.analytics_repo.get_top_campaigns_by_roi(days)

    def get_worst_campaigns(self, days: int = 7) -> list[dict]:
        return self.analytics_repo.get_worst_campaigns(days)

    def get_campaign_detail(self, campaign_id: int) -> dict:
        return {
            "summary": self.analytics_repo.get_campaign_summary(campaign_id),
            "history": self.analytics_repo.get_last_n_days(campaign_id, 30)
        }

    def get_platform_comparison(self, days: int = 30) -> list[dict]:
        return self.analytics_repo.get_all_platform_summary(days)
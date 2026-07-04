"""
services/budget_service.py
===========================
Tracks daily, weekly, and monthly spend across all campaigns.
Detects overspending and budget pacing issues.
"""

import logging
from database.repositories.analytics_repository import AnalyticsRepository
from database.repositories.campaign_repository import CampaignRepository

logger = logging.getLogger(__name__)


class BudgetService:

    def __init__(self):
        self.analytics_repo = AnalyticsRepository()
        self.camp_repo      = CampaignRepository()

    def get_spend_summary(self) -> dict:
        """
        Return spend totals for today, this week, and this month.

        Returns:
            Dict with daily_spend, weekly_spend, monthly_spend per platform.
        """
        daily   = self.analytics_repo.get_daily_totals(days=1)
        weekly  = self.analytics_repo.get_daily_totals(days=7)
        monthly = self.analytics_repo.get_daily_totals(days=30)

        def _sum_spend(rows):
            return round(sum(r.get("spend", 0) for r in rows), 2)

        return {
            "daily_spend":   _sum_spend(daily),
            "weekly_spend":  _sum_spend(weekly),
            "monthly_spend": _sum_spend(monthly),
        }

    def get_budget_pacing(self) -> list[dict]:
        """
        Check if each active campaign is on pace to use its budget.

        Pacing = (spend so far) / (budget × days elapsed / total days)
        > 1.2 = overspending
        < 0.8 = underspending
        0.8-1.2 = on pace

        Returns:
            List of dicts with campaign name, pacing status, and spend info.
        """
        campaigns = self.camp_repo.get_active()
        results   = []

        for camp in campaigns:
            summary = self.analytics_repo.get_campaign_summary(camp["id"])
            if not summary:
                continue

            total_spend  = summary.get("total_spend", 0) or 0
            total_budget = camp.get("total_budget", 0) or 0

            if total_budget <= 0:
                continue

            pacing_ratio = total_spend / total_budget

            if pacing_ratio > 1.0:
                status = "over_budget"
            elif pacing_ratio > 0.85:
                status = "on_pace"
            elif pacing_ratio > 0.5:
                status = "underspending"
            else:
                status = "severely_underspending"

            results.append({
                "campaign_id":   camp["id"],
                "campaign_name": camp["name"],
                "platform":      camp["platform"],
                "total_budget":  total_budget,
                "total_spend":   total_spend,
                "pacing_ratio":  round(pacing_ratio, 4),
                "pacing_status": status,
                "remaining":     round(total_budget - total_spend, 2),
            })

        return results

    def get_overspending_campaigns(self) -> list[dict]:
        """Return campaigns that have exceeded their total budget."""
        pacing = self.get_budget_pacing()
        return [p for p in pacing if p["pacing_status"] == "over_budget"]
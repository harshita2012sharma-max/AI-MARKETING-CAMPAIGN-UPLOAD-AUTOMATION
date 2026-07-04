"""
ai_engine/executive_summary.py
================================
Generates a boardroom-ready plain English summary of all campaign performance.
Non-technical managers can read this without understanding marketing metrics.
"""

import logging
from datetime import date
from services.analytics_service import AnalyticsService
from services.campaign_service import CampaignService
from ai_engine.anomaly_detector import AnomalyDetector
from ai_engine.recommender import Recommender

logger = logging.getLogger("ai_engine.executive_summary")


class ExecutiveSummary:
    """Generates plain English executive summaries for non-technical stakeholders."""

    def __init__(self):
        self.analytics  = AnalyticsService()
        self.campaigns  = CampaignService()
        self.detector   = AnomalyDetector()
        self.recommender = Recommender()

    def generate(self, days: int = 7) -> dict:
        """
        Generate a complete executive summary.

        Args:
            days: Number of days to analyse (default 7 = weekly summary).

        Returns:
            Dict with headline, sections, kpis, alerts, and recommendations.
        """
        try:
            kpis         = self.analytics.get_dashboard_kpis(days)
            top_camps    = self.analytics.get_top_campaigns(days)
            worst_camps  = self.analytics.get_worst_campaigns(days)
            anomalies    = self.detector.detect_all()
            counts       = self.campaigns.get_dashboard_counts()
            recs         = self.recommender.recommend_all()

            total_spend    = kpis.get("total_spend", 0)
            total_revenue  = kpis.get("total_revenue", 0)
            avg_roi        = kpis.get("avg_roi", 0)
            total_clicks   = kpis.get("total_clicks", 0)
            total_conv     = kpis.get("total_conversions", 0)
            active_count   = counts.get("by_status", {}).get("active", 0)

            # ── Headline ──────────────────────────────────────────────────────
            if avg_roi >= 2.0:
                headline = f"Strong performance this period — ROI at {avg_roi:.1f}x across all platforms."
                sentiment = "positive"
            elif avg_roi >= 1.0:
                headline = f"Moderate performance — ROI at {avg_roi:.1f}x. Optimisation opportunities exist."
                sentiment = "neutral"
            else:
                headline = f"Attention required — ROI at {avg_roi:.1f}x. Campaigns need immediate review."
                sentiment = "negative"

            # ── Performance paragraph ─────────────────────────────────────────
            performance_text = (
                f"Over the last {days} days, your {active_count} active campaigns across "
                f"Google Ads, Meta Ads, and Bing Ads generated {total_clicks:,} clicks "
                f"and {total_conv:,} conversions at a total spend of ₹{total_spend:,.2f}. "
                f"Total revenue attributed to ads was ₹{total_revenue:,.2f}, "
                f"delivering an average return of ₹{avg_roi:.2f} for every ₹1 spent."
            )

            # ── Best performer ────────────────────────────────────────────────
            best_text = ""
            if top_camps:
                best = top_camps[0]
                best_text = (
                    f"Your best performing campaign is '{best['name']}' on "
                    f"{best['platform'].title()} Ads with an ROI of {best.get('avg_roi',0):.2f}x "
                    f"and {best.get('total_conversions',0)} conversions this period."
                )

            # ── Worst performer ───────────────────────────────────────────────
            worst_text = ""
            if worst_camps:
                worst = worst_camps[0]
                worst_text = (
                    f"Your lowest performing campaign is '{worst['name']}' on "
                    f"{worst['platform'].title()} Ads with an ROI of {worst.get('avg_roi',0):.2f}x. "
                    f"This campaign requires immediate review."
                )

            # ── Alerts summary ────────────────────────────────────────────────
            alert_text = ""
            if anomalies:
                alert_text = (
                    f"The AI engine detected {len(anomalies)} anomal{'y' if len(anomalies)==1 else 'ies'} "
                    f"this period that require your attention."
                )
            else:
                alert_text = "No anomalies detected this period. All campaigns are behaving normally."

            # ── Recommendations summary ───────────────────────────────────────
            rec_text = ""
            if recs:
                rec_text = (
                    f"The AI engine has generated {len(recs)} recommendation"
                    f"{'s' if len(recs)>1 else ''} to improve campaign performance. "
                    f"Key action: {recs[0]['suggested_action']}"
                )

            return {
                "generated_at":   date.today().isoformat(),
                "period_days":    days,
                "sentiment":      sentiment,
                "headline":       headline,
                "performance":    performance_text,
                "best_performer": best_text,
                "worst_performer": worst_text,
                "alerts":         alert_text,
                "recommendations": rec_text,
                "kpis": {
                    "total_spend":    total_spend,
                    "total_revenue":  total_revenue,
                    "avg_roi":        avg_roi,
                    "total_clicks":   total_clicks,
                    "total_conversions": total_conv,
                    "active_campaigns":  active_count,
                },
                "top_campaigns":   top_camps[:3],
                "worst_campaigns": worst_camps[:3],
                "anomaly_count":   len(anomalies),
                "rec_count":       len(recs),
            }

        except Exception as exc:
            logger.error("Executive summary generation failed: %s", exc)
            return {
                "generated_at": date.today().isoformat(),
                "headline":     "Summary unavailable — data error.",
                "sentiment":    "neutral",
                "error":        str(exc),
            }

    def generate_text_report(self, days: int = 7) -> str:
        """
        Generate a plain text version of the executive summary.
        Used by the PDF report generator.

        Returns:
            Multi-line plain text string.
        """
        data = self.generate(days)
        lines = [
            "=" * 60,
            "ADPULSE — EXECUTIVE SUMMARY",
            f"Period: Last {days} days  |  Generated: {data.get('generated_at','')}",
            "=" * 60,
            "",
            data.get("headline", ""),
            "",
            "PERFORMANCE OVERVIEW",
            "-" * 40,
            data.get("performance", ""),
            "",
            "BEST PERFORMER",
            "-" * 40,
            data.get("best_performer", "N/A"),
            "",
            "NEEDS ATTENTION",
            "-" * 40,
            data.get("worst_performer", "N/A"),
            "",
            "ALERTS",
            "-" * 40,
            data.get("alerts", ""),
            "",
            "AI RECOMMENDATIONS",
            "-" * 40,
            data.get("recommendations", "No recommendations at this time."),
            "",
            "=" * 60,
        ]
        return "\n".join(lines)
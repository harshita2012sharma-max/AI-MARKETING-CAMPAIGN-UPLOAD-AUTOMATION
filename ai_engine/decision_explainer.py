"""
ai_engine/decision_explainer.py
================================
Converts raw AI scores and numbers into plain English explanations.
Every recommendation the AI makes goes through this before showing to user.
No ML needed — pure string formatting + business logic.
"""

import logging
from config.constants import (
    HEALTH_EXCELLENT, HEALTH_GOOD, HEALTH_WARNING,
    BENCHMARK_ROI_GOOD, BENCHMARK_CTR_GOOD, BENCHMARK_CPC_HIGH
)

logger = logging.getLogger("ai_engine.decision_explainer")


class DecisionExplainer:
    """Turns numbers into human-readable marketing advice."""

    def explain_health_score(self, score: float, campaign_name: str) -> str:
        """
        Return a plain English sentence explaining a campaign health score.

        Args:
            score: Health score 0-100.
            campaign_name: Name of the campaign.

        Returns:
            Human-readable explanation string.
        """
        if score >= HEALTH_EXCELLENT:
            return (
                f"'{campaign_name}' is performing excellently with a health score of "
                f"{score:.0f}/100. ROI, CTR, and CPC are all above industry benchmarks. "
                f"Consider increasing the budget to scale results."
            )
        elif score >= HEALTH_GOOD:
            return (
                f"'{campaign_name}' is performing well with a health score of {score:.0f}/100. "
                f"There is room for minor optimisations in targeting or ad creative "
                f"to push performance higher."
            )
        elif score >= HEALTH_WARNING:
            return (
                f"'{campaign_name}' needs attention. Health score is {score:.0f}/100. "
                f"Review your CTR and CPC — one or more KPIs are below benchmark. "
                f"Consider refreshing ad creative or narrowing audience targeting."
            )
        else:
            return (
                f"'{campaign_name}' is in critical condition with a health score of "
                f"{score:.0f}/100. This campaign is likely losing money. "
                f"Immediate action required: pause, review targeting, and rebuild strategy."
            )

    def explain_roi(self, roi: float, campaign_name: str) -> str:
        """Return plain English explanation of a campaign's ROI."""
        if roi >= BENCHMARK_ROI_GOOD:
            return (
                f"'{campaign_name}' has a strong ROI of {roi:.2f}x — for every ₹1 spent, "
                f"₹{roi:.2f} is returned. This campaign is profitable and worth scaling."
            )
        elif roi >= 1.0:
            return (
                f"'{campaign_name}' has a marginal ROI of {roi:.2f}x. "
                f"The campaign is breaking even but not generating strong returns. "
                f"Optimise targeting and landing pages to improve conversion rate."
            )
        else:
            return (
                f"'{campaign_name}' has a negative ROI of {roi:.2f}x — spending more "
                f"than earning. Pause this campaign and audit the funnel immediately."
            )

    def explain_ctr(self, ctr: float, campaign_name: str) -> str:
        """Return plain English explanation of a campaign's CTR."""
        if ctr >= BENCHMARK_CTR_GOOD:
            return (
                f"'{campaign_name}' has a strong CTR of {ctr:.2f}%. "
                f"Your ads are resonating well with the target audience."
            )
        elif ctr >= 0.5:
            return (
                f"'{campaign_name}' has an average CTR of {ctr:.2f}%. "
                f"Test new headlines and descriptions to improve click-through rate."
            )
        else:
            return (
                f"'{campaign_name}' has a very low CTR of {ctr:.2f}%. "
                f"Ad creative or targeting may be misaligned with the audience. "
                f"A/B test new ad copy urgently."
            )

    def explain_anomaly(self, anomaly_type: str, value: float,
                        avg_value: float, campaign_name: str) -> str:
        """
        Return plain English explanation of a detected anomaly.

        Args:
            anomaly_type: 'ctr_drop' | 'spend_spike' | 'conversion_drop'
            value: Today's value.
            avg_value: 7-day average value.
            campaign_name: Campaign name.

        Returns:
            Human-readable anomaly description.
        """
        change_pct = abs((value - avg_value) / avg_value * 100) if avg_value else 0

        if anomaly_type == "ctr_drop":
            return (
                f"CTR anomaly detected on '{campaign_name}'. "
                f"Today's CTR is {value:.2f}% vs the 7-day average of {avg_value:.2f}% "
                f"— a drop of {change_pct:.1f}%. "
                f"Possible causes: ad fatigue, increased competition, or audience saturation. "
                f"Recommended action: refresh ad creative and check bid strategy."
            )
        elif anomaly_type == "spend_spike":
            return (
                f"Unusual spend spike on '{campaign_name}'. "
                f"Today's spend is ₹{value:.2f} vs average of ₹{avg_value:.2f} "
                f"— an increase of {change_pct:.1f}%. "
                f"Possible causes: broad match keywords, competitor bidding war, or budget setting error. "
                f"Recommended action: review keyword match types and set a daily spend cap."
            )
        elif anomaly_type == "conversion_drop":
            return (
                f"Conversion drop detected on '{campaign_name}'. "
                f"Today's conversions are {value:.0f} vs average of {avg_value:.1f} "
                f"— a drop of {change_pct:.1f}%. "
                f"Possible causes: landing page issue, offer expired, or tracking broken. "
                f"Recommended action: verify landing page and conversion tracking immediately."
            )
        else:
            return (
                f"Anomaly detected on '{campaign_name}': "
                f"{anomaly_type} changed by {change_pct:.1f}% vs 7-day average."
            )

    def explain_forecast(self, metric: str, current: float,
                         predicted: float, days: int) -> str:
        """Return plain English explanation of a forecast."""
        direction = "increase" if predicted > current else "decrease"
        change    = abs(predicted - current)
        pct       = abs((predicted - current) / current * 100) if current else 0

        return (
            f"Based on current trends, {metric} is projected to {direction} by "
            f"{pct:.1f}% over the next {days} days "
            f"(from {current:.2f} to {predicted:.2f}). "
            f"{'This is a positive trend — maintain current strategy.' if predicted > current else 'Monitor closely and consider optimisation.'}"
        )

    def explain_budget_recommendation(self, campaign_name: str,
                                       current_budget: float,
                                       recommended_budget: float,
                                       reason: str) -> str:
        """Return plain English budget recommendation."""
        direction = "increase" if recommended_budget > current_budget else "decrease"
        diff      = abs(recommended_budget - current_budget)
        return (
            f"Budget recommendation for '{campaign_name}': "
            f"{direction.capitalize()} daily budget from ₹{current_budget:.0f} "
            f"to ₹{recommended_budget:.0f} (change of ₹{diff:.0f}/day). "
            f"Reason: {reason}"
        )
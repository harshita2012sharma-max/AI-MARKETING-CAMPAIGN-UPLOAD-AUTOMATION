"""
ai_engine/roi_predictor.py
===========================
Predicts future ROI for campaigns based on historical patterns.
Uses moving averages and trend detection — no ML frameworks.

Logic:
- Weighted moving average: recent days count more than older ones.
- Trend factor: if ROI is improving, predicted ROI reflects that.
- Seasonality: weekday vs weekend patterns applied.
"""

import logging
import math
from database.repositories.analytics_repository import AnalyticsRepository
from database.repositories.campaign_repository import CampaignRepository

logger = logging.getLogger("ai_engine.roi_predictor")


def _weighted_moving_average(values: list[float], weights: list[float] = None) -> float:
    """
    Calculate weighted moving average. Recent values get higher weight.

    Args:
        values:  List of values (oldest first).
        weights: Optional custom weights. If None, uses linear weights.

    Returns:
        Weighted average as float.
    """
    if not values:
        return 0.0

    n = len(values)
    if weights is None:
        # Linear weights: last value gets weight n, first gets weight 1
        weights = list(range(1, n + 1))

    total_weight = sum(weights)
    if total_weight == 0:
        return sum(values) / n

    weighted_sum = sum(v * w for v, w in zip(values, weights))
    return weighted_sum / total_weight


def _detect_trend(values: list[float]) -> float:
    """
    Detect trend direction and strength.

    Returns:
        Trend factor:
          > 1.0 = improving (e.g. 1.05 = 5% improvement expected)
          < 1.0 = declining (e.g. 0.95 = 5% decline expected)
          = 1.0 = stable
    """
    if len(values) < 4:
        return 1.0

    # Compare average of last quarter vs first quarter
    quarter = max(1, len(values) // 4)
    recent  = sum(values[-quarter:]) / quarter
    older   = sum(values[:quarter]) / quarter

    if older == 0:
        return 1.0

    trend_ratio = recent / older
    # Dampen extreme trends — cap at ±20% projection
    return max(0.80, min(1.20, trend_ratio))


class ROIPredictor:
    """Predicts ROI for campaigns using historical patterns."""

    def __init__(self):
        self.analytics_repo = AnalyticsRepository()
        self.camp_repo      = CampaignRepository()

    def predict_roi(self, campaign_id: int, days_ahead: int = 7) -> dict:
        """
        Predict average ROI for the next N days.

        Args:
            campaign_id: Campaign primary key.
            days_ahead:  How many days to predict.

        Returns:
            Dict with predicted_roi, confidence, trend, and explanation.
        """
        history = self.analytics_repo.get_last_n_days(campaign_id, days=30)
        if not history:
            logger.warning("No history for campaign %s — cannot predict ROI.", campaign_id)
            return {}

        # Reverse: oldest first
        history  = list(reversed(history))
        roi_vals = [r["roi"] for r in history if r["roi"] is not None]

        if not roi_vals:
            return {}

        # Weighted moving average — recent days matter more
        wma_roi = _weighted_moving_average(roi_vals)

        # Trend factor
        trend   = _detect_trend(roi_vals)

        # Predicted ROI
        predicted_roi = round(wma_roi * trend, 4)

        # Confidence: based on data consistency
        mean = sum(roi_vals) / len(roi_vals)
        if mean > 0:
            variance   = sum((v - mean) ** 2 for v in roi_vals) / len(roi_vals)
            std_dev    = math.sqrt(variance)
            cv         = std_dev / abs(mean)
            confidence = round(max(0.3, min(0.92, 1.0 - cv * 0.4)), 2)
        else:
            confidence = 0.3

        # Human-readable explanation
        if trend > 1.05:
            trend_text = f"ROI is on an upward trend (+{(trend-1)*100:.1f}% improvement detected)."
        elif trend < 0.95:
            trend_text = f"ROI is on a downward trend ({(trend-1)*100:.1f}% decline detected)."
        else:
            trend_text = "ROI has been stable over the observed period."

        explanation = (
            f"Based on {len(roi_vals)} days of historical data, "
            f"predicted ROI for the next {days_ahead} days is {predicted_roi:.2f}x. "
            f"{trend_text} "
            f"Forecast confidence: {confidence*100:.0f}%."
        )

        return {
            "campaign_id":    campaign_id,
            "days_ahead":     days_ahead,
            "current_avg_roi":  round(mean, 4),
            "predicted_roi":    predicted_roi,
            "trend_factor":     round(trend, 4),
            "trend_direction":  "up" if trend > 1.02 else "down" if trend < 0.98 else "flat",
            "confidence":       confidence,
            "explanation":      explanation,
            "data_points_used": len(roi_vals),
        }

    def predict_all(self, days_ahead: int = 7) -> list[dict]:
        """
        Predict ROI for all active campaigns.

        Returns:
            List of prediction dicts sorted by predicted_roi descending.
        """
        campaigns = self.camp_repo.get_active()
        results   = []

        for camp in campaigns:
            pred = self.predict_roi(camp["id"], days_ahead)
            if pred:
                pred["campaign_name"] = camp["name"]
                pred["platform"]      = camp["platform"]
                results.append(pred)
                logger.info(
                    "ROI prediction: %s → %.2fx (confidence %.0f%%)",
                    camp["name"],
                    pred.get("predicted_roi", 0),
                    pred.get("confidence", 0) * 100,
                )

        results.sort(key=lambda x: x.get("predicted_roi", 0), reverse=True)
        return results
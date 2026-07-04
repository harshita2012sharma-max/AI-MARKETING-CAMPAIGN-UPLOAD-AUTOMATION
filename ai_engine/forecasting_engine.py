"""
ai_engine/forecasting_engine.py
=================================
Predicts future campaign performance using linear regression.
No ML libraries — built with Python standard library math only.

How it works:
1. Takes last N days of a metric (spend, clicks, conversions, ROI).
2. Fits a straight line through the data using least squares formula.
3. Extends that line forward by the requested number of days.
4. Returns predicted values with confidence interval.
"""

import logging
import math
from database.repositories.analytics_repository import AnalyticsRepository
from database.repositories.campaign_repository import CampaignRepository

logger = logging.getLogger("ai_engine.forecasting_engine")


def _linear_regression(values: list[float]) -> tuple[float, float]:
    """
    Fit a linear trend line through a list of values.
    Returns (slope, intercept) of the best-fit line.

    Uses the standard least squares formula:
    slope = (n*Σxy - Σx*Σy) / (n*Σx² - (Σx)²)
    """
    n = len(values)
    if n < 2:
        return 0.0, values[0] if values else 0.0

    x_vals = list(range(n))
    sum_x  = sum(x_vals)
    sum_y  = sum(values)
    sum_xy = sum(x * y for x, y in zip(x_vals, values))
    sum_xx = sum(x * x for x in x_vals)

    denominator = n * sum_xx - sum_x ** 2
    if denominator == 0:
        return 0.0, sum_y / n

    slope     = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n
    return slope, intercept


def _predict_next(values: list[float], days_ahead: int) -> list[float]:
    """
    Predict the next N values based on historical trend.

    Args:
        values:     Historical values (oldest first).
        days_ahead: How many future values to predict.

    Returns:
        List of predicted values (length = days_ahead).
    """
    slope, intercept = _linear_regression(values)
    n = len(values)
    predictions = []
    for i in range(days_ahead):
        predicted = intercept + slope * (n + i)
        predictions.append(max(0.0, round(predicted, 4)))
    return predictions


def _calculate_confidence(values: list[float], slope: float) -> float:
    """
    Estimate forecast confidence (0-1) based on data consistency.
    More consistent historical data = higher confidence.
    High slope variance = lower confidence.

    Returns:
        Confidence score 0.0 to 1.0.
    """
    if len(values) < 3:
        return 0.5

    mean = sum(values) / len(values)
    if mean == 0:
        return 0.5

    # Coefficient of variation: lower = more consistent = higher confidence
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std_dev  = math.sqrt(variance)
    cv       = std_dev / abs(mean)

    confidence = max(0.3, min(0.95, 1.0 - cv * 0.5))
    return round(confidence, 2)


class ForecastingEngine:
    """Generates short and long-term performance forecasts for campaigns."""

    def __init__(self):
        self.analytics_repo = AnalyticsRepository()
        self.camp_repo      = CampaignRepository()

    def forecast_campaign(self, campaign_id: int,
                          days_ahead: int = 7) -> dict:
        """
        Generate a forecast for one campaign.

        Args:
            campaign_id: Campaign primary key.
            days_ahead:  How many days to forecast (7 or 30).

        Returns:
            Dict with predicted values for spend, clicks, conversions, roi.
        """
        history = self.analytics_repo.get_last_n_days(campaign_id, days=30)
        if not history:
            logger.warning("No history for campaign %s — cannot forecast.", campaign_id)
            return {}

        # Reverse so oldest is first (get_last_n_days returns newest first)
        history = list(reversed(history))

        spends      = [r["spend"]       for r in history]
        clicks      = [r["clicks"]      for r in history]
        conversions = [r["conversions"] for r in history]
        rois        = [r["roi"]         for r in history]

        pred_spend = _predict_next(spends, days_ahead)
        pred_clicks = _predict_next(clicks, days_ahead)
        pred_conv  = _predict_next(conversions, days_ahead)
        pred_roi   = _predict_next(rois, days_ahead)

        slope, _ = _linear_regression(spends)
        confidence = _calculate_confidence(spends, slope)

        return {
            "campaign_id":    campaign_id,
            "days_ahead":     days_ahead,
            "confidence":     confidence,
            "predicted_spend":       round(sum(pred_spend), 2),
            "predicted_clicks":      int(sum(pred_clicks)),
            "predicted_conversions": int(sum(pred_conv)),
            "predicted_roi":         round(sum(pred_roi) / len(pred_roi), 4) if pred_roi else 0,
            "daily_spend_forecast":  pred_spend,
            "daily_clicks_forecast": [int(v) for v in pred_clicks],
            "trend_direction":       "up" if slope > 0 else "down" if slope < 0 else "flat",
        }

    def forecast_all_campaigns(self, days_ahead: int = 7) -> list[dict]:
        """
        Generate forecasts for all active campaigns.

        Returns:
            List of forecast dicts.
        """
        campaigns = self.camp_repo.get_active()
        results   = []
        for camp in campaigns:
            forecast = self.forecast_campaign(camp["id"], days_ahead)
            if forecast:
                forecast["campaign_name"] = camp["name"]
                forecast["platform"]      = camp["platform"]
                results.append(forecast)
                logger.info(
                    "Forecast for %s: spend=₹%.2f, trend=%s, confidence=%.2f",
                    camp["name"],
                    forecast.get("predicted_spend", 0),
                    forecast.get("trend_direction", "unknown"),
                    forecast.get("confidence", 0),
                )
        return results

    def forecast_platform_spend(self, platform: str,
                                days_ahead: int = 7) -> dict:
        """
        Forecast total spend for an entire platform.

        Args:
            platform:   'google' | 'meta' | 'bing'
            days_ahead: Forecast horizon.

        Returns:
            Dict with predicted total spend and trend.
        """
        from database.repositories.analytics_repository import AnalyticsRepository
        analytics_repo = AnalyticsRepository()
        daily = analytics_repo.get_daily_totals(days=30)

        if not daily:
            return {}

        spends = [r["spend"] for r in daily]
        predictions = _predict_next(spends, days_ahead)
        slope, _    = _linear_regression(spends)

        return {
            "platform":       platform,
            "days_ahead":     days_ahead,
            "predicted_spend": round(sum(predictions), 2),
            "daily_forecast":  predictions,
            "trend_direction": "up" if slope > 0 else "down" if slope < 0 else "flat",
        }
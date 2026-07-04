from flask import Blueprint, render_template, session, redirect, url_for
from services.analytics_service import AnalyticsService
from services.notification_service import NotificationService
from ai_engine.forecasting_engine import ForecastingEngine
from ai_engine.roi_predictor import ROIPredictor

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/analytics")
def index():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    analytics  = AnalyticsService()
    comparison = analytics.get_platform_comparison(30)
    trend      = analytics.get_daily_trend(30)
    top        = analytics.get_top_campaigns(30)
    worst      = analytics.get_worst_campaigns(7)
    forecasts  = ForecastingEngine().forecast_all_campaigns(7)
    roi_preds  = ROIPredictor().predict_all(7)
    unread     = NotificationService().get_unread_count(session["user_id"])
    return render_template("analytics.html",
        comparison=comparison, trend=trend,
        top=top, worst=worst,
        forecasts=forecasts, roi_preds=roi_preds, unread=unread)
from flask import Blueprint, render_template, session, redirect, url_for
from services.analytics_service import AnalyticsService
from services.campaign_service import CampaignService
from services.notification_service import NotificationService
from services.audit_service import AuditService
from ai_engine.performance_analyzer import PerformanceAnalyzer
from ai_engine.recommender import Recommender
from ai_engine.anomaly_detector import AnomalyDetector

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    analytics = AnalyticsService()
    PerformanceAnalyzer().score_all_campaigns()

    kpis        = analytics.get_dashboard_kpis(30)
    trend       = analytics.get_daily_trend(30)
    top_camps   = analytics.get_top_campaigns(30)
    worst_camps = analytics.get_worst_campaigns(7)
    comparison  = analytics.get_platform_comparison(30)
    counts      = CampaignService().get_dashboard_counts()
    unread      = NotificationService().get_unread_count(session["user_id"])
    audit_logs  = AuditService().get_recent(10)
    recs        = Recommender().recommend_all()
    anomalies   = AnomalyDetector().detect_all()

    return render_template("dashboard.html",
        kpis=kpis, trend=trend, top_camps=top_camps,
        worst_camps=worst_camps, comparison=comparison,
        counts=counts, unread=unread,
        audit_logs=audit_logs,
        recommendations=recs, anomalies=anomalies)
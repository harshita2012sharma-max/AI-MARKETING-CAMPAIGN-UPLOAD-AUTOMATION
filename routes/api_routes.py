from flask import Blueprint, jsonify, session
from services.analytics_service import AnalyticsService
from services.campaign_service import CampaignService
from services.notification_service import NotificationService

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/kpis")
def kpis():
    if "user_id" not in session: return jsonify({"error": "Unauthorized"}), 401
    return jsonify(AnalyticsService().get_dashboard_kpis(30))

@api_bp.route("/trend")
def trend():
    if "user_id" not in session: return jsonify({"error": "Unauthorized"}), 401
    return jsonify(AnalyticsService().get_daily_trend(30))

@api_bp.route("/platforms")
def platforms():
    if "user_id" not in session: return jsonify({"error": "Unauthorized"}), 401
    return jsonify(AnalyticsService().get_platform_comparison(30))

@api_bp.route("/campaigns")
def campaigns():
    if "user_id" not in session: return jsonify({"error": "Unauthorized"}), 401
    return jsonify(CampaignService().get_all())

@api_bp.route("/notifications/unread")
def unread_count():
    if "user_id" not in session: return jsonify({"error": "Unauthorized"}), 401
    count = NotificationService().get_unread_count(session["user_id"])
    return jsonify({"count": count})
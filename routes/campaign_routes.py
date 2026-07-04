from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from services.campaign_service import CampaignService
from services.analytics_service import AnalyticsService
from services.sync_service import SyncService
from services.notification_service import NotificationService

campaign_bp  = Blueprint("campaigns", __name__)
camp_service = CampaignService()

def _require_login():
    return "user_id" not in session

@campaign_bp.route("/campaigns")
def index():
    if _require_login(): return redirect(url_for("auth.login"))
    platform = request.args.get("platform")
    status   = request.args.get("status")
    query    = request.args.get("q", "")
    camps    = camp_service.search(query) if query else camp_service.get_all(platform=platform, status=status)
    unread   = NotificationService().get_unread_count(session["user_id"])
    return render_template("campaigns.html",
        campaigns=camps, platform=platform,
        status=status, query=query, unread=unread)

@campaign_bp.route("/campaigns/<int:campaign_id>")
def detail(campaign_id):
    if _require_login(): return redirect(url_for("auth.login"))
    camp        = camp_service.get_by_id(campaign_id)
    if not camp:
        flash("Campaign not found.", "error")
        return redirect(url_for("campaigns.index"))
    detail      = AnalyticsService().get_campaign_detail(campaign_id)
    sync_status = SyncService().get_campaign_sync_status(campaign_id)
    unread      = NotificationService().get_unread_count(session["user_id"])
    return render_template("campaign_detail.html",
        campaign=camp, detail=detail,
        sync_status=sync_status, unread=unread)

@campaign_bp.route("/campaigns/create", methods=["GET", "POST"])
def create():
    if _require_login(): return redirect(url_for("auth.login"))
    if request.method == "POST":
        data = {
            "name":            request.form["name"],
            "platform":        request.form["platform"],
            "objective":       request.form.get("objective", "awareness"),
            "daily_budget":    float(request.form.get("daily_budget", 0)),
            "total_budget":    float(request.form.get("total_budget", 0)),
            "start_date":      request.form["start_date"],
            "end_date":        request.form.get("end_date", ""),
            "target_audience": request.form.get("target_audience", ""),
            "keywords":        request.form.get("keywords", "[]"),
        }
        result = camp_service.create(data, session["user_id"])
        flash("Campaign created and synced to all 3 platforms!", "success")
        return redirect(url_for("campaigns.detail", campaign_id=result["campaign_id"]))
    unread = NotificationService().get_unread_count(session["user_id"])
    return render_template("campaign_create.html", unread=unread)

@campaign_bp.route("/campaigns/<int:campaign_id>/pause", methods=["POST"])
def pause(campaign_id):
    if _require_login(): return redirect(url_for("auth.login"))
    camp_service.pause(campaign_id, session["user_id"])
    flash("Campaign paused across all platforms.", "info")
    return redirect(url_for("campaigns.index"))

@campaign_bp.route("/campaigns/<int:campaign_id>/resume", methods=["POST"])
def resume(campaign_id):
    if _require_login(): return redirect(url_for("auth.login"))
    camp_service.resume(campaign_id, session["user_id"])
    flash("Campaign resumed across all platforms.", "success")
    return redirect(url_for("campaigns.index"))

@campaign_bp.route("/campaigns/<int:campaign_id>/delete", methods=["POST"])
def delete(campaign_id):
    if _require_login(): return redirect(url_for("auth.login"))
    camp_service.delete(campaign_id, session["user_id"])
    flash("Campaign removed.", "info")
    return redirect(url_for("campaigns.index"))
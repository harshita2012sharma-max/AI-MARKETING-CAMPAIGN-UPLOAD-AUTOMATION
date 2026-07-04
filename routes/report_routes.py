from flask import Blueprint, render_template, session, redirect, url_for, flash
from services.report_service import ReportService
from database.repositories.report_repository import ReportRepository
from services.notification_service import NotificationService

report_bp = Blueprint("reports", __name__)

@report_bp.route("/reports")
def index():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    all_reports = ReportRepository().get_all()
    unread      = NotificationService().get_unread_count(session["user_id"])
    return render_template("reports.html", reports=all_reports, unread=unread)

@report_bp.route("/reports/generate-pdf", methods=["POST"])
def generate_pdf():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    ReportService().generate_weekly_pdf(user_id=session["user_id"])
    flash("PDF report generated!", "success")
    return redirect(url_for("reports.index"))

@report_bp.route("/reports/export-csv", methods=["POST"])
def export_csv():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    ReportService().export_campaigns_csv(user_id=session["user_id"])
    flash("CSV export complete!", "success")
    return redirect(url_for("reports.index"))
from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from services.notification_service import NotificationService

notification_bp = Blueprint("notifications", __name__)

@notification_bp.route("/notifications")
def index():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    svc    = NotificationService()
    notes  = svc.get_for_user(session["user_id"])
    unread = svc.get_unread_count(session["user_id"])
    return render_template("notifications.html", notifications=notes, unread=unread)

@notification_bp.route("/notifications/mark-all-read", methods=["POST"])
def mark_all_read():
    if "user_id" not in session: return jsonify({"error": "Unauthorized"}), 401
    NotificationService().mark_all_read(session["user_id"])
    return jsonify({"ok": True})
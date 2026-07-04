from flask import Blueprint, render_template, session, redirect, url_for
settings_bp = Blueprint("settings_page", __name__)

@settings_bp.route("/settings")
def index():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    return render_template("settings.html")
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from services.auth_service import AuthService

auth_bp      = Blueprint("auth", __name__)
auth_service = AuthService()

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = auth_service.login(username, password, ip=request.remote_addr)
        if user:
            session["user_id"]  = user["id"]
            session["role"]     = user["role"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard.index"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from ai_engine.chat_agent import ChatAgent
from ai_engine.recommender import Recommender
from ai_engine.anomaly_detector import AnomalyDetector
from ai_engine.executive_summary import ExecutiveSummary
from services.notification_service import NotificationService

ai_bp   = Blueprint("ai", __name__)
_agents: dict = {}

@ai_bp.route("/ai")
def index():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    recs      = Recommender().recommend_all()
    anomalies = AnomalyDetector().detect_all()
    summary   = ExecutiveSummary().generate(7)
    unread    = NotificationService().get_unread_count(session["user_id"])
    return render_template("ai_panel.html",
        recommendations=recs, anomalies=anomalies,
        summary=summary, unread=unread)

@ai_bp.route("/ai/chat", methods=["POST"])
def chat():
    if "user_id" not in session: return jsonify({"error": "Unauthorized"}), 401
    user_id = session["user_id"]
    message = request.json.get("message", "").strip()
    if not message: return jsonify({"reply": "Please type a message."})
    if user_id not in _agents:
        _agents[user_id] = ChatAgent()
    reply = _agents[user_id].chat(message)
    return jsonify({"reply": reply})
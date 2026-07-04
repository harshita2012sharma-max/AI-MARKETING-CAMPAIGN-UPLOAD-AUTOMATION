"""
app.py — Flask application factory
"""
import logging
from datetime import datetime
from flask import Flask, session, g
from config.settings import settings
from config.logging_config import setup_logging
from database.migrations import run_migrations
from database.seed import run_seed

setup_logging()
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = settings.SECRET_KEY

    run_migrations()
    run_seed()

    from routes.auth_routes         import auth_bp
    from routes.dashboard_routes    import dashboard_bp
    from routes.campaign_routes     import campaign_bp
    from routes.analytics_routes    import analytics_bp
    from routes.ai_routes           import ai_bp
    from routes.api_routes          import api_bp
    from routes.notification_routes import notification_bp
    from routes.report_routes       import report_bp
    from routes.settings_routes     import settings_bp

    for bp in [auth_bp, dashboard_bp, campaign_bp, analytics_bp,
               ai_bp, api_bp, notification_bp, report_bp, settings_bp]:
        app.register_blueprint(bp)

    @app.before_request
    def load_user():
        from services.auth_service import AuthService
        user_id = session.get("user_id")
        g.user  = AuthService().get_user_by_id(user_id) if user_id else None

    @app.context_processor
    def inject_globals():
        return {"current_user": g.get("user"), "now": datetime.now()}

    from services.scheduler_service import start_scheduler
    start_scheduler()

    logger.info("AdPulse started.")
    return app
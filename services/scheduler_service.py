"""
services/scheduler_service.py
===============================
Background job scheduler using APScheduler.
Runs automatically every N minutes without any manual trigger.

Jobs:
  - sync_platforms     : every 30 minutes
  - run_ai_analysis    : every 6 hours
  - run_rule_engine    : every 1 hour
  - generate_weekly_report : every Monday at 9 AM
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from config.settings import settings

logger = logging.getLogger("services.scheduler_service")

# Module-level scheduler instance
_scheduler: BackgroundScheduler = None


def _job_sync_platforms() -> None:
    """Pull latest data from all 3 platform adapters."""
    try:
        from services.sync_service import SyncService
        SyncService().sync_all()
        logger.info("Scheduler: Platform sync complete.")
    except Exception as exc:
        logger.error("Scheduler: Platform sync failed: %s", exc)


def _job_ai_analysis() -> None:
    """Score all campaigns and generate recommendations."""
    try:
        from ai_engine.performance_analyzer import PerformanceAnalyzer
        from ai_engine.anomaly_detector import AnomalyDetector
        PerformanceAnalyzer().score_all_campaigns()
        AnomalyDetector().detect_all()
        logger.info("Scheduler: AI analysis complete.")
    except Exception as exc:
        logger.error("Scheduler: AI analysis failed: %s", exc)


def _job_rule_engine() -> None:
    """Run automation rules against all active campaigns."""
    try:
        from services.rule_engine_service import RuleEngineService
        triggered = RuleEngineService().run_all_rules(admin_user_id=1)
        logger.info("Scheduler: Rule engine ran. %d rules triggered.", len(triggered))
    except Exception as exc:
        logger.error("Scheduler: Rule engine failed: %s", exc)


def _job_weekly_report() -> None:
    """Generate and save weekly PDF report."""
    try:
        from services.report_service import ReportService
        path = ReportService().generate_weekly_pdf(user_id=1)
        logger.info("Scheduler: Weekly report saved to %s", path)
    except Exception as exc:
        logger.error("Scheduler: Weekly report failed: %s", exc)


def start_scheduler() -> None:
    """
    Start the background scheduler.
    Called once from app.py on startup.
    """
    global _scheduler

    if _scheduler and _scheduler.running:
        logger.warning("Scheduler already running. Skipping start.")
        return

    _scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

    # Sync platforms every 30 minutes
    _scheduler.add_job(
        _job_sync_platforms,
        trigger=IntervalTrigger(minutes=settings.SYNC_INTERVAL_MINUTES),
        id="sync_platforms",
        replace_existing=True,
        misfire_grace_time=60
    )

    # AI analysis every 6 hours
    _scheduler.add_job(
        _job_ai_analysis,
        trigger=IntervalTrigger(hours=6),
        id="ai_analysis",
        replace_existing=True,
        misfire_grace_time=300
    )

    # Rule engine every 1 hour
    _scheduler.add_job(
        _job_rule_engine,
        trigger=IntervalTrigger(hours=1),
        id="rule_engine",
        replace_existing=True,
        misfire_grace_time=120
    )

    # Weekly report every Monday at 9 AM
    _scheduler.add_job(
        _job_weekly_report,
        trigger=CronTrigger(
            day_of_week="mon",
            hour=settings.REPORT_HOUR,
            minute=0
        ),
        id="weekly_report",
        replace_existing=True,
        misfire_grace_time=3600
    )

    _scheduler.start()
    logger.info(
        "Scheduler started. Jobs: sync every %dm, AI every 6h, rules every 1h, report every Monday.",
        settings.SYNC_INTERVAL_MINUTES
    )


def stop_scheduler() -> None:
    """Gracefully stop the scheduler (called on app shutdown)."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
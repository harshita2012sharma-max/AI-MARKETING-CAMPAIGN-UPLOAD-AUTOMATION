"""
config/logging_config.py
=========================
Sets up logging for the entire app.
Three log files: app.log, ai.log, scheduler.log
"""

import logging
import logging.handlers
from pathlib import Path
from config.settings import settings


def setup_logging() -> None:
    """Call this once from app.py before anything else starts."""
    log_dir = settings.LOGS_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    level = logging.DEBUG if settings.DEBUG else logging.INFO

    def _file_handler(filename: str) -> logging.Handler:
        handler = logging.handlers.RotatingFileHandler(
            log_dir / filename,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        handler.setFormatter(fmt)
        handler.setLevel(level)
        return handler

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(_file_handler("app.log"))

    logging.getLogger("ai_engine").addHandler(_file_handler("ai.log"))
    logging.getLogger("services.scheduler_service").addHandler(_file_handler("scheduler.log"))

    if settings.DEBUG:
        console = logging.StreamHandler()
        console.setFormatter(fmt)
        console.setLevel(logging.DEBUG)
        root.addHandler(console)

    logging.getLogger("werkzeug").setLevel(logging.WARNING)
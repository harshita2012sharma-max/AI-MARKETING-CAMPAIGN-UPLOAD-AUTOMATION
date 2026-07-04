"""
database/migrations.py
=======================
Runs schema.sql to create all tables on first startup.
Safe to run multiple times — uses IF NOT EXISTS everywhere.
"""

import logging
from pathlib import Path
from database.connection import execute_script

logger = logging.getLogger(__name__)
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def run_migrations() -> None:
    """Read schema.sql and execute it. Called once from app.py on startup."""
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"schema.sql not found at {SCHEMA_PATH}")

    logger.info("Running database migrations...")
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    execute_script(sql)
    logger.info("Database migrations complete.")
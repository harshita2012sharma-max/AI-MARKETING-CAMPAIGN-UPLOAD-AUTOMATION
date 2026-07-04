"""
database/connection.py
=======================
Supports MySQL.
Set DB_TYPE=mysql in .env to switch.
Everything else in the app stays exactly the same.
"""

import threading
import logging
from config.settings import settings

logger = logging.getLogger(__name__)
_thread_local = threading.local()


# ─────────────────────────────────────────────────────────────────────────────
# MYSQL CONNECTION
# ─────────────────────────────────────────────────────────────────────────────
def _get_mysql_connection():
    """Return thread-local MySQL connection."""
    import mysql.connector
    from mysql.connector import Error

    if not hasattr(_thread_local, "connection") or _thread_local.connection is None:
        try:
            conn = mysql.connector.connect(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                database=settings.MYSQL_DATABASE,
                autocommit=False,
                connection_timeout=30,
                use_pure=True,
            )
            _thread_local.connection = conn
            logger.debug("MySQL connection created for thread %s",
                         threading.current_thread().name)
        except Error as exc:
            logger.error("MySQL connection failed: %s", exc)
            raise

    # Reconnect if connection dropped
    if not _thread_local.connection.is_connected():
        _thread_local.connection.reconnect(attempts=3, delay=2)

    return _thread_local.connection


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API 
# ─────────────────────────────────────────────────────────────────────────────
def get_connection():
    """
    Return database connection based on DB_TYPE in .env.
    MySQL  → returns mysql.connector.connection
    """
    return _get_mysql_connection()
  


def close_connection() -> None:
    """Close connection for current thread."""
    if hasattr(_thread_local, "connection") and _thread_local.connection:
        try:
            _thread_local.connection.close()
        except Exception:
            pass
        _thread_local.connection = None


def execute_script(sql: str) -> None:
    """Execute MySQL script."""
    _execute_mysql_script(sql)




def _execute_mysql_script(sql: str) -> None:
    """Execute MySQL script — splits on semicolons."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        statements = [s.strip() for s in sql.split(";") if s.strip()]

        for stmt in statements:
            if stmt:
                try:
                    cursor.execute(stmt)
                except Exception as e:
                    logger.error("Error executing SQL:\n%s\n%s", stmt, e)
                    raise

        conn.commit()
        logger.info("MySQL script executed.")

    except Exception as exc:
        conn.rollback()
        logger.error("MySQL script failed: %s", exc)
        raise

    finally:
        cursor.close()
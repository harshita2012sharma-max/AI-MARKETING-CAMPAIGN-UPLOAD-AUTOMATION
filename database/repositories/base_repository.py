"""
database/repositories/base_repository.py
==========================================
Works with MySQL.
Uses dictionary=True cursor so rows come back as dicts.
"""

import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from database.connection import get_connection

logger = logging.getLogger(__name__)


class BaseRepository:

    def _conn(self):
        return get_connection()

    def _cursor(self, dictionary: bool = True):
        """Return a MySQL cursor."""
        conn = self._conn()
        return conn.cursor(dictionary=True)

    def _row_to_dict(self, row) -> dict:
        """
        Convert a cursor row to a plain dict, normalizing MySQL's
        native Python types back to what the app (and templates)
        expect after coming from SQLite:
          - decimal.Decimal -> float   (so arithmetic doesn't break)
          - datetime/date   -> str     (so string slicing like
                                        n.created_at[:16] still works)
        MySQL returns DATETIME columns as datetime.datetime objects
        and DATE columns as datetime.date objects, whereas SQLite
        returned them as plain strings — this normalizes both back
        to strings once, here, instead of patching every template.
        """
        result = {}
        for k, v in dict(row).items():
            if isinstance(v, Decimal):
                result[k] = float(v)
            elif isinstance(v, datetime):
                result[k] = v.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(v, date):
                result[k] = v.strftime("%Y-%m-%d")
            else:
                result[k] = v
        return result

    def _fix_placeholders(self, sql: str) -> str:
        """
        MySQL uses %s for parameters.
        """
        return sql.replace("?", "%s")

    def _fix_sql_syntax(self, sql: str) -> str:
        """Fix SQL to use MySQL-specific functions."""
        sql = sql.replace("datetime('now')", "NOW()")
        sql = sql.replace("date('now')", "CURDATE()")

        # date('now', '-30 days') -> DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        import re
        sql = re.sub(
            r"date\('now',\s*'([+-])(\d+)\s+days?'\)",
            lambda m: f"DATE_SUB(CURDATE(), INTERVAL {m.group(2)} DAY)"
                      if m.group(1) == '-'
                      else f"DATE_ADD(CURDATE(), INTERVAL {m.group(2)} DAY)",
            sql
        )
        return sql

    def execute(self, sql: str, params: tuple = ()):
        """Run INSERT, UPDATE, or DELETE."""
        conn   = self._conn()
        sql    = self._fix_placeholders(self._fix_sql_syntax(sql))
        cursor = self._cursor()

        try:
            # Handle ON CONFLICT for MySQL (use ON DUPLICATE KEY UPDATE instead)
            if "ON CONFLICT" in sql:
                sql = self._convert_upsert(sql)

            cursor.execute(sql, params)
            conn.commit()

            # Create a simple result object
            class Result:
                def __init__(self, cur):
                    self.lastrowid = cur.lastrowid
                    self.rowcount  = cur.rowcount

            return Result(cursor)

        except Exception as exc:
            logger.error("DB execute error: %s | SQL: %s", exc, sql[:100])
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            cursor.close()

    def fetchone(self, sql: str, params: tuple = ()) -> Optional[dict]:
        """Run SELECT and return first row as dict."""
        sql    = self._fix_placeholders(self._fix_sql_syntax(sql))
        cursor = self._cursor(dictionary=True)

        try:
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None
        except Exception as exc:
            logger.error("fetchone error: %s | SQL: %s", exc, sql[:100])
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    def fetchall(self, sql: str, params: tuple = ()) -> list[dict]:
        """Run SELECT and return all rows as list of dicts."""
        sql    = self._fix_placeholders(self._fix_sql_syntax(sql))
        cursor = self._cursor(dictionary=True)

        try:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows] if rows else []
        except Exception as exc:
            logger.error("fetchall error: %s | SQL: %s", exc, sql[:100])
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    def count(self, table: str, where: str = "", params: tuple = ()) -> int:
        sql = f"SELECT COUNT(*) as cnt FROM {table}"
        if where:
            sql += f" WHERE {where}"
        row = self.fetchone(sql, params)
        return row["cnt"] if row else 0

    def _convert_upsert(self, sql: str) -> str:
        """
        Convert SQLite ON CONFLICT ... DO UPDATE SET
        to MySQL ON DUPLICATE KEY UPDATE syntax.
        This handles the campaign_platforms upsert.
        """
        if "ON CONFLICT(campaign_id, platform)" in sql:
            # Extract the UPDATE part
            if "DO UPDATE SET" in sql:
                update_part = sql.split("DO UPDATE SET")[1].strip()
                base_sql = sql.split("ON CONFLICT")[0].strip()
                # Build MySQL version
                lines = [l.strip() for l in update_part.split(",") if l.strip()]
                mysql_update = ", ".join(lines)
                return f"{base_sql} ON DUPLICATE KEY UPDATE {mysql_update}"
        return sql
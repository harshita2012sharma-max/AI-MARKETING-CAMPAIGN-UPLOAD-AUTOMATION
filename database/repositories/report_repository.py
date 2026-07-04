"""
database/repositories/report_repository.py
"""
import logging
from typing import Optional
from database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ReportRepository(BaseRepository):

    def create(self, title: str, report_type: str, fmt: str,
               file_path: str, generated_by: Optional[int] = None) -> int:
        cur = self.execute(
            "INSERT INTO reports (title,report_type,format,file_path,generated_by) VALUES (?,?,?,?,?)",
            (title, report_type, fmt, file_path, generated_by)
        )
        return cur.lastrowid

    def get_all(self, limit: int = 50) -> list[dict]:
        return self.fetchall(
            """SELECT r.*,u.username AS generated_by_name FROM reports r
               LEFT JOIN users u ON u.id=r.generated_by
               ORDER BY r.generated_at DESC LIMIT ?""",
            (limit,)
        )

    def get_by_id(self, report_id: int) -> Optional[dict]:
        return self.fetchone("SELECT * FROM reports WHERE id=?", (report_id,))
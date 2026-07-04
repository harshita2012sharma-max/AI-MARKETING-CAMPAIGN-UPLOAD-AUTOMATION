"""
database/repositories/audit_repository.py
"""
import logging
from typing import Optional
from database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class AuditRepository(BaseRepository):

    def log(self, action: str, description: str,
            user_id: Optional[int] = None, entity_type: Optional[str] = None,
            entity_id: Optional[int] = None, ip_address: Optional[str] = None) -> None:
        self.execute(
            """INSERT INTO audit_logs
               (user_id,action,entity_type,entity_id,description,ip_address)
               VALUES (?,?,?,?,?,?)""",
            (user_id, action, entity_type, entity_id, description, ip_address)
        )

    def get_recent(self, limit: int = 50) -> list[dict]:
        return self.fetchall(
            """SELECT al.*,u.username FROM audit_logs al
               LEFT JOIN users u ON u.id=al.user_id
               ORDER BY al.created_at DESC LIMIT ?""",
            (limit,)
        )

    def get_by_entity(self, entity_type: str, entity_id: int) -> list[dict]:
        return self.fetchall(
            "SELECT * FROM audit_logs WHERE entity_type=? AND entity_id=? ORDER BY created_at DESC",
            (entity_type, entity_id)
        )
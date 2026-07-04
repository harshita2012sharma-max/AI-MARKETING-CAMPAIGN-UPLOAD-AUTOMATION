"""
services/audit_service.py
Records every action with timestamp.
"""
import logging
from typing import Optional
from database.repositories.audit_repository import AuditRepository

logger = logging.getLogger(__name__)


class AuditService:

    def __init__(self):
        self.repo = AuditRepository()

    def log(self, action: str, description: str,
            user_id: Optional[int] = None,
            entity_type: Optional[str] = None,
            entity_id: Optional[int] = None,
            ip_address: Optional[str] = None) -> None:
        self.repo.log(
            action, description,
            user_id, entity_type, entity_id, ip_address
        )

    def get_recent(self, limit: int = 50) -> list[dict]:
        return self.repo.get_recent(limit)
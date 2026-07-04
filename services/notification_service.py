"""
services/notification_service.py
Creates and manages user notifications (alert bell).
"""
import logging
from database.repositories.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)


class NotificationService:

    def __init__(self):
        self.repo = NotificationRepository()

    def create(self, user_id: int, title: str,
               message: str, ntype: str = "info",
               related_id: int = None) -> int:
        return self.repo.create(user_id, title, message, ntype, related_id)

    def get_for_user(self, user_id: int) -> list[dict]:
        return self.repo.get_for_user(user_id)

    def get_unread_count(self, user_id: int) -> int:
        return self.repo.get_unread_count(user_id)

    def mark_read(self, notification_id: int) -> None:
        self.repo.mark_read(notification_id)

    def mark_all_read(self, user_id: int) -> None:
        self.repo.mark_all_read(user_id)
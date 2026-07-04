"""
database/repositories/notification_repository.py
"""
import logging
from database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class NotificationRepository(BaseRepository):

    def create(self, user_id: int, title: str, message: str,
               ntype: str = "info", related_id: int = None) -> int:
        cur = self.execute(
            "INSERT INTO notifications (user_id,title,message,type,related_id) VALUES (?,?,?,?,?)",
            (user_id, title, message, ntype, related_id)
        )
        return cur.lastrowid

    def get_for_user(self, user_id: int, limit: int = 20) -> list[dict]:
        return self.fetchall(
            "SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )

    def get_unread_count(self, user_id: int) -> int:
        return self.count("notifications", "user_id=? AND is_read=0", (user_id,))

    def mark_read(self, notification_id: int) -> None:
        self.execute("UPDATE notifications SET is_read=1 WHERE id=?", (notification_id,))

    def mark_all_read(self, user_id: int) -> None:
        self.execute("UPDATE notifications SET is_read=1 WHERE user_id=?", (user_id,))
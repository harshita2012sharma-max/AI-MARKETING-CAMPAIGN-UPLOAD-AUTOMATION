"""
database/repositories/user_repository.py
"""
import logging
from typing import Optional
from database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):

    def create(self, username: str, email: str, password_hash: str, role: str = "viewer") -> int:
        cur = self.execute(
            "INSERT INTO users (username,email,password_hash,role) VALUES (?,?,?,?)",
            (username, email, password_hash, role)
        )
        return cur.lastrowid

    def get_by_id(self, user_id: int) -> Optional[dict]:
        return self.fetchone("SELECT * FROM users WHERE id=?", (user_id,))

    def get_by_username(self, username: str) -> Optional[dict]:
        return self.fetchone("SELECT * FROM users WHERE username=?", (username,))

    def get_by_email(self, email: str) -> Optional[dict]:
        return self.fetchone("SELECT * FROM users WHERE email=?", (email,))

    def get_all(self) -> list[dict]:
        return self.fetchall(
            "SELECT id,username,email,role,is_active,created_at,last_login FROM users ORDER BY username"
        )

    def update_last_login(self, user_id: int) -> None:
        self.execute("UPDATE users SET last_login=datetime('now') WHERE id=?", (user_id,))

    def update_password(self, user_id: int, password_hash: str) -> bool:
        cur = self.execute("UPDATE users SET password_hash=? WHERE id=?", (password_hash, user_id))
        return cur.rowcount > 0

    def set_active(self, user_id: int, is_active: bool) -> bool:
        cur = self.execute("UPDATE users SET is_active=? WHERE id=?", (1 if is_active else 0, user_id))
        return cur.rowcount > 0
"""
services/auth_service.py
Login, logout, password hashing, role checks.
"""
import hashlib
import logging
import bcrypt
from typing import Optional
from database.repositories.user_repository import UserRepository
from database.repositories.audit_repository import AuditRepository

logger = logging.getLogger(__name__)


class AuthService:

    def __init__(self):
        self.user_repo  = UserRepository()
        self.audit_repo = AuditRepository()

    def login(self, username: str, password: str,
              ip: Optional[str] = None) -> Optional[dict]:
        user = self.user_repo.get_by_username(username)
        if not user or not user["is_active"]:
            return None

        pw_bytes = password.encode("utf-8")
        stored   = user["password_hash"].encode("utf-8")

        # Try bcrypt first, fall back to SHA-256 (used by seed.py)
        try:
            valid = bcrypt.checkpw(pw_bytes, stored)
        except Exception:
            valid = hashlib.sha256(pw_bytes).hexdigest() == user["password_hash"]

        if not valid:
            self.audit_repo.log(
                "user.login_failed",
                f"Failed login for {username}",
                ip_address=ip
            )
            return None

        self.user_repo.update_last_login(user["id"])
        self.audit_repo.log(
            "user.login",
            f"{username} logged in",
            user_id=user["id"],
            ip_address=ip
        )
        return user

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        ).decode()

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        return self.user_repo.get_by_id(user_id)

    def is_admin(self, user: dict) -> bool:
        return user.get("role") == "admin"

    def is_manager_or_above(self, user: dict) -> bool:
        return user.get("role") in ("admin", "manager")
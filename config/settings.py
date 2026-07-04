"""
config/settings.py
Central configuration for AdPulse.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

BASE_DIR = Path(__file__).parent.parent


class Settings:

    # Flask
    SECRET_KEY: str      = os.getenv("SECRET_KEY", "adpulse-dev-secret-change-in-production")
    DEBUG: bool          = os.getenv("DEBUG", "false").lower() == "true"
    PORT: int            = int(os.getenv("PORT", "5000"))
    HOST: str            = os.getenv("HOST", "127.0.0.1")

    # Database type — sqlite or mysql
    DB_TYPE: str         = os.getenv("DB_TYPE", "sqlite")

    # SQLite
    DATABASE_PATH: str   = os.getenv("DATABASE_PATH", str(BASE_DIR / "adpulse.db"))

    # MySQL
    MYSQL_HOST: str      = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int      = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str      = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str  = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str  = os.getenv("MYSQL_DATABASE", "adpulse")

    # AI / Groq
    GROQ_API_KEY: str    = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str      = os.getenv("GROQ_MODEL", "llama3-8b-8192")
    GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "1024"))

    # Paths
    REPORTS_DIR: Path    = BASE_DIR / "reports"
    LOGS_DIR: Path       = BASE_DIR / "logs"

    # Scheduler
    SYNC_INTERVAL_MINUTES: int = int(os.getenv("SYNC_INTERVAL_MINUTES", "30"))
    REPORT_HOUR: int           = int(os.getenv("REPORT_HOUR", "9"))

    # Session
    SESSION_LIFETIME_HOURS: int = int(os.getenv("SESSION_LIFETIME_HOURS", "8"))

    def __init__(self) -> None:
        self.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
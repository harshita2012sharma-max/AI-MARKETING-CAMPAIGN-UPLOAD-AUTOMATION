"""
database/repositories/platform_repository.py
Manages campaign_platforms table — one row per platform per campaign.
"""
import logging
from database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class PlatformRepository(BaseRepository):

    def save_sync_result(self, campaign_id: int, platform: str,
                         external_id: str, status: str = "created",
                         error_message: str = None) -> None:
        self.execute(
            """INSERT INTO campaign_platforms
               (campaign_id, platform, external_id, status, error_message)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(campaign_id, platform)
               DO UPDATE SET
                   external_id   = excluded.external_id,
                   status        = excluded.status,
                   error_message = excluded.error_message,
                   synced_at     = datetime('now')""",
            (campaign_id, platform, external_id, status, error_message)
        )

    def get_for_campaign(self, campaign_id: int) -> list[dict]:
        return self.fetchall(
            "SELECT * FROM campaign_platforms WHERE campaign_id=? ORDER BY platform",
            (campaign_id,)
        )

    def get_all_synced(self) -> list[dict]:
        return self.fetchall(
            """SELECT cp.*, c.name as campaign_name
               FROM campaign_platforms cp
               JOIN campaigns c ON c.id=cp.campaign_id
               ORDER BY cp.synced_at DESC"""
        )

    def update_status(self, campaign_id: int, platform: str, status: str) -> None:
        self.execute(
            """UPDATE campaign_platforms
               SET status=?, synced_at=datetime('now')
               WHERE campaign_id=? AND platform=?""",
            (status, campaign_id, platform)
        )

    def get_sync_summary(self) -> dict:
        rows = self.fetchall(
            """SELECT platform, COUNT(*) as total,
               SUM(CASE WHEN status IN ('created','active') THEN 1 ELSE 0 END) as active
               FROM campaign_platforms GROUP BY platform"""
        )
        return {r["platform"]: {"total": r["total"], "active": r["active"]} for r in rows}
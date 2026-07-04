"""
services/campaign_service.py
==============================
Campaign business logic.
KEY CHANGE: create() now pushes to all 3 platforms after saving to DB.
"""
import logging
import uuid
from typing import Optional
from database.repositories.campaign_repository import CampaignRepository
from database.repositories.audit_repository import AuditRepository

logger = logging.getLogger(__name__)


class CampaignService:

    def __init__(self):
        self.camp_repo  = CampaignRepository()
        self.audit_repo = AuditRepository()

    def get_all(self, platform: Optional[str] = None,
                status: Optional[str] = None,
                page: int = 1) -> list[dict]:
        return self.camp_repo.get_all(
            platform=platform, status=status, page=page
        )

    def get_by_id(self, campaign_id: int) -> Optional[dict]:
        return self.camp_repo.get_by_id(campaign_id)

    def create(self, data: dict, user_id: int) -> dict:
        """
        Create a campaign AND push it to all 3 platforms.

        Returns:
            Dict with campaign_id and platform sync results.
        """
        # Save to our DB first
        data["external_id"]  = f"AP-{uuid.uuid4().hex[:8].upper()}"
        data["created_by"]   = user_id
        data["spent_total"]  = 0.0
        data["health_score"] = 0.0
        camp_id = self.camp_repo.create(data)

        # NOW push to all 3 platforms
        from services.sync_service import SyncService
        sync_results = SyncService().push_campaign_to_all_platforms(
            campaign_id=camp_id,
            campaign_data=data
        )

        self.audit_repo.log(
            "campaign.create",
            f"Created campaign '{data['name']}' and pushed to 3 platforms",
            user_id=user_id,
            entity_type="campaign",
            entity_id=camp_id
        )

        logger.info(
            "Campaign '%s' created (id=%s) and synced to all platforms",
            data["name"], camp_id
        )

        return {
            "campaign_id":    camp_id,
            "campaign_name":  data["name"],
            "sync_results":   sync_results
        }

    def update(self, campaign_id: int, data: dict, user_id: int) -> bool:
        result = self.camp_repo.update(campaign_id, data)
        if result:
            self.audit_repo.log(
                "campaign.update",
                f"Updated campaign {campaign_id}",
                user_id=user_id,
                entity_type="campaign",
                entity_id=campaign_id
            )
        return result

    def pause(self, campaign_id: int, user_id: int) -> bool:
        """Pause campaign in DB and update all platform statuses."""
        result = self.camp_repo.update_status(campaign_id, "paused")
        if result:
            # Update status in campaign_platforms table too
            from database.repositories.platform_repository import PlatformRepository
            platform_repo = PlatformRepository()
            for platform in ["google", "meta", "bing"]:
                platform_repo.update_status(campaign_id, platform, "paused")

            self.audit_repo.log(
                "campaign.pause",
                f"Paused campaign {campaign_id} across all platforms",
                user_id=user_id,
                entity_type="campaign",
                entity_id=campaign_id
            )
        return result

    def resume(self, campaign_id: int, user_id: int) -> bool:
        """Resume campaign in DB and update all platform statuses."""
        result = self.camp_repo.update_status(campaign_id, "active")
        if result:
            from database.repositories.platform_repository import PlatformRepository
            platform_repo = PlatformRepository()
            for platform in ["google", "meta", "bing"]:
                platform_repo.update_status(campaign_id, platform, "active")

            self.audit_repo.log(
                "campaign.resume",
                f"Resumed campaign {campaign_id} across all platforms",
                user_id=user_id,
                entity_type="campaign",
                entity_id=campaign_id
            )
        return result

    def delete(self, campaign_id: int, user_id: int) -> bool:
        result = self.camp_repo.delete(campaign_id)
        if result:
            self.audit_repo.log(
                "campaign.delete",
                f"Deleted campaign {campaign_id}",
                user_id=user_id,
                entity_type="campaign",
                entity_id=campaign_id
            )
        return result

    def search(self, query: str) -> list[dict]:
        return self.camp_repo.search(query)

    def get_dashboard_counts(self) -> dict:
        return {
            "by_platform": self.camp_repo.count_by_platform(),
            "by_status":   self.camp_repo.count_by_status(),
        }
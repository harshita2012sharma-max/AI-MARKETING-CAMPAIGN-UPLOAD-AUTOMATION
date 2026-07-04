"""
services/sync_service.py
==========================
THE CORE FEATURE — Multi-platform campaign synchronization.

When a user creates ONE campaign in AdPulse:
1. We push it to Google Ads simulator  → get back G-XXXXXX
2. We push it to Meta Ads simulator    → get back M-XXXXXX
3. We push it to Bing Ads simulator    → get back B-XXXXXX
4. We save all 3 results to campaign_platforms table
5. Dashboard shows sync status table with all 3 external IDs

This is exactly what the Upwork client asked for:
"Centralize campaign management across Google Ads, Microsoft Bing Ads, and Meta Ads"
"""

import logging
import time
from adapters.adapter_factory import AdapterFactory
from database.repositories.campaign_repository import CampaignRepository
from database.repositories.analytics_repository import AnalyticsRepository
from database.repositories.platform_repository import PlatformRepository
from database.repositories.audit_repository import AuditRepository
from database.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

PLATFORMS = ["google", "meta", "bing"]


class SyncService:

    def __init__(self):
        self.camp_repo      = CampaignRepository()
        self.analytics_repo = AnalyticsRepository()
        self.platform_repo  = PlatformRepository()
        self.audit_repo     = AuditRepository()
        self.user_repo      = UserRepository()

    def push_campaign_to_all_platforms(self,
                                        campaign_id: int,
                                        campaign_data: dict) -> dict:
        """
        THE MAIN FUNCTION — Push one campaign to all 3 platforms.

        This is called right after a campaign is created in AdPulse.
        Each platform simulator receives the campaign data and returns
        its own external ID.

        Args:
            campaign_id:   Our internal DB campaign ID.
            campaign_data: Campaign details (name, budget, dates etc).

        Returns:
            Dict showing sync result per platform:
            {
                "google": {"external_id": "G-8A31F2", "status": "created"},
                "meta":   {"external_id": "M-19CD44", "status": "created"},
                "bing":   {"external_id": "B-77EF10", "status": "created"},
            }
        """
        results = {}

        logger.info(
            "Pushing campaign '%s' to all platforms...",
            campaign_data.get("name", campaign_id)
        )

        for platform in PLATFORMS:
            try:
                # Get the adapter for this platform
                adapter = AdapterFactory.get(platform)

                # Send campaign to the platform simulator
                # In production this calls real Google/Meta/Bing API
                response = adapter.create_campaign(dict(campaign_data))

                # Platform returns its own external ID
                external_id = response.get("external_id", f"UNKNOWN-{platform[:1].upper()}")
                status      = response.get("status", "created")

                # Save to campaign_platforms table
                self.platform_repo.save_sync_result(
                    campaign_id=campaign_id,
                    platform=platform,
                    external_id=external_id,
                    status=status
                )

                results[platform] = {
                    "external_id": external_id,
                    "status":      status,
                    "success":     True,
                    "platform_label": platform.title()
                }

                logger.info(
                    "✅ %s: Campaign created with external ID %s",
                    platform.title(), external_id
                )

                # Small delay between platform calls (realistic behaviour)
                time.sleep(0.1)

            except Exception as exc:
                # One platform failing should NOT stop the others
                error_msg = str(exc)
                logger.error("❌ %s sync failed: %s", platform, error_msg)

                self.platform_repo.save_sync_result(
                    campaign_id=campaign_id,
                    platform=platform,
                    external_id="FAILED",
                    status="failed",
                    error_message=error_msg
                )

                results[platform] = {
                    "external_id": "FAILED",
                    "status":      "failed",
                    "success":     False,
                    "error":       error_msg
                }

        # Log to audit trail
        successful = sum(1 for r in results.values() if r["success"])
        self.audit_repo.log(
            action="campaign.sync",
            description=(
                f"Campaign {campaign_id} pushed to {successful}/3 platforms. "
                f"IDs: " + ", ".join(
                    f"{p}={r['external_id']}"
                    for p, r in results.items()
                )
            ),
            entity_type="campaign",
            entity_id=campaign_id
        )

        return results

    def get_campaign_sync_status(self, campaign_id: int) -> list[dict]:
        """
        Get current sync status for a campaign across all platforms.
        Used to show the sync table on campaign detail page.

        Returns:
            List of platform sync records with status and external IDs.
        """
        return self.platform_repo.get_for_campaign(campaign_id)

    def sync_metrics_from_all_platforms(self) -> dict:
        """
        Pull latest metrics from all platforms for all campaigns.
        Called by the scheduler every 30 minutes.

        Returns:
            Summary: {platform: metrics_synced_count}
        """
        summary = {}

        for platform in PLATFORMS:
            try:
                count = self._sync_platform_metrics(platform)
                summary[platform] = count
                time.sleep(0.3)
            except Exception as exc:
                logger.error("Metrics sync failed for %s: %s", platform, exc)
                summary[platform] = 0

        logger.info("Metrics sync complete: %s", summary)
        return summary

    def _sync_platform_metrics(self, platform: str) -> int:
        """Pull metrics from one platform and save to daily_metrics table."""
        adapter   = AdapterFactory.get(platform)
        campaigns = self.camp_repo.get_by_platform(platform)
        synced    = 0

        for camp in campaigns:
            try:
                metrics = adapter.get_metrics(
                    campaign_id=camp["external_id"],
                    days=1
                )
                for metric in metrics:
                    metric["campaign_id"] = camp["id"]
                    self.analytics_repo.insert_metric(metric)
                synced += 1
            except Exception as exc:
                logger.warning(
                    "Metrics failed for campaign %s on %s: %s",
                    camp["id"], platform, exc
                )

        return synced
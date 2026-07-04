"""
adapters/google_ads_adapter.py
================================
Simulates Google Ads API with realistic behaviour.

Improvement: Now maintains internal storage so create/update/delete
operations actually persist within the session. This makes the simulator
behave exactly like a real Google Ads API would.

Storage is in-memory (Python dict). Resets when app restarts,
which is correct for a simulator.
"""
import random
import uuid
import logging
from datetime import date, timedelta
from adapters.base_adapter import BaseAdapter

logger = logging.getLogger(__name__)
random.seed(99)


class GoogleAdsMockAdapter(BaseAdapter):

    def __init__(self):
        # Internal storage — simulates Google's campaign database
        # Seeded with realistic starter campaigns
        self._campaigns: dict[str, dict] = {
            "G-001": {
                "external_id":     "G-001",
                "name":            "Diwali Sale — Google Search",
                "platform":        "google",
                "status":          "active",
                "objective":       "conversions",
                "daily_budget":    1500.0,
                "total_budget":    45000.0,
                "start_date":      (date.today() - timedelta(days=89)).isoformat(),
                "target_audience": "25-45, India, Shopping interest",
            },
            "G-002": {
                "external_id":     "G-002",
                "name":            "Brand Awareness — Google Display",
                "platform":        "google",
                "status":          "active",
                "objective":       "awareness",
                "daily_budget":    800.0,
                "total_budget":    24000.0,
                "start_date":      (date.today() - timedelta(days=89)).isoformat(),
                "target_audience": "18-35, India, Tech interest",
            },
            "G-003": {
                "external_id":     "G-003",
                "name":            "Product Launch — Google Search",
                "platform":        "google",
                "status":          "paused",
                "objective":       "conversions",
                "daily_budget":    2000.0,
                "total_budget":    60000.0,
                "start_date":      (date.today() - timedelta(days=60)).isoformat(),
                "target_audience": "30-50, India, Business decision makers",
            },
        }

    def get_campaigns(self) -> list[dict]:
        """
        Return all campaigns from internal storage.
        Now includes any campaigns created via create_campaign().
        """
        return list(self._campaigns.values())

    def create_campaign(self, data: dict) -> dict:
        """
        Create a new campaign and store it internally.
        Returns the campaign with a new Google-style external ID.
        """
        external_id = f"G-{uuid.uuid4().hex[:6].upper()}"
        campaign = {
            "external_id":     external_id,
            "name":            data.get("name", "Untitled Campaign"),
            "platform":        "google",
            "status":          "created",
            "objective":       data.get("objective", "awareness"),
            "daily_budget":    data.get("daily_budget", 0.0),
            "total_budget":    data.get("total_budget", 0.0),
            "start_date":      data.get("start_date", date.today().isoformat()),
            "target_audience": data.get("target_audience", ""),
        }
        # Store it — now get_campaigns() will include this
        self._campaigns[external_id] = campaign
        logger.info("GoogleAds: Created campaign %s — '%s'",
                    external_id, campaign["name"])
        return campaign

    def update_campaign(self, campaign_id: str, data: dict) -> dict:
        """
        Update campaign fields in internal storage.
        Returns updated campaign dict.
        """
        if campaign_id not in self._campaigns:
            logger.warning("GoogleAds: Campaign %s not found for update.", campaign_id)
            return {"external_id": campaign_id, **data}

        # Update only the fields provided
        self._campaigns[campaign_id].update({
            k: v for k, v in data.items()
            if k != "external_id"  # never overwrite the ID
        })
        logger.info("GoogleAds: Updated campaign %s", campaign_id)
        return self._campaigns[campaign_id]

    def delete_campaign(self, campaign_id: str) -> bool:
        """Remove campaign from internal storage."""
        if campaign_id in self._campaigns:
            del self._campaigns[campaign_id]
            logger.info("GoogleAds: Deleted campaign %s", campaign_id)
            return True
        logger.warning("GoogleAds: Campaign %s not found for delete.", campaign_id)
        return False

    def pause_campaign(self, campaign_id: str) -> bool:
        """Pause a campaign in internal storage."""
        if campaign_id in self._campaigns:
            self._campaigns[campaign_id]["status"] = "paused"
            logger.info("GoogleAds: Paused campaign %s", campaign_id)
            return True
        return False

    def resume_campaign(self, campaign_id: str) -> bool:
        """Resume a paused campaign in internal storage."""
        if campaign_id in self._campaigns:
            self._campaigns[campaign_id]["status"] = "active"
            logger.info("GoogleAds: Resumed campaign %s", campaign_id)
            return True
        return False

    def get_metrics(self, campaign_id: str, days: int = 30) -> list[dict]:
        """Generate realistic daily metrics for any campaign ID."""
        metrics = []
        base = {
            "impressions": 3200, "clicks": 102,
            "conversions": 9, "spend": 1280.0, "revenue": 3200.0
        }
        for i in range(days):
            day  = date.today() - timedelta(days=days - i)
            wm   = 0.70 if day.weekday() >= 5 else 1.0
            imp  = max(1, int(base["impressions"] * wm * random.uniform(0.85, 1.15)))
            clk  = max(0, min(imp, int(base["clicks"] * wm * random.uniform(0.85, 1.15))))
            conv = max(0, min(clk, int(base["conversions"] * wm * random.uniform(0.7, 1.3))))
            spnd = round(base["spend"] * wm * random.uniform(0.85, 1.15), 2)
            rev  = round(base["revenue"] * wm * random.uniform(0.8, 1.2), 2)
            metrics.append({
                "date":        day.isoformat(),
                "impressions": imp, "clicks": clk,
                "conversions": conv, "spend": spnd, "revenue": rev,
                "ctr":  round(clk / imp * 100, 4) if imp  else 0.0,
                "cpc":  round(spnd / clk, 4)      if clk  else 0.0,
                "cpa":  round(spnd / conv, 4)     if conv else 0.0,
                "roi":  round(rev / spnd, 4)      if spnd else 0.0,
            })
        return metrics
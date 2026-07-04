"""
adapters/meta_ads_adapter.py
==============================
Simulates Meta (Facebook + Instagram) Ads API with internal storage.
create/update/delete operations actually persist within the session.
"""
import random
import uuid
import logging
from datetime import date, timedelta
from adapters.base_adapter import BaseAdapter

logger = logging.getLogger(__name__)
random.seed(77)


class MetaAdsMockAdapter(BaseAdapter):

    def __init__(self):
        self._campaigns: dict[str, dict] = {
            "M-001": {
                "external_id":     "M-001",
                "name":            "Instagram Reels — Summer Collection",
                "platform":        "meta",
                "status":          "active",
                "objective":       "awareness",
                "daily_budget":    1200.0,
                "total_budget":    36000.0,
                "start_date":      (date.today() - timedelta(days=89)).isoformat(),
                "target_audience": "18-30, India, Fashion interest",
            },
            "M-002": {
                "external_id":     "M-002",
                "name":            "Facebook Lead Gen — B2B",
                "platform":        "meta",
                "status":          "active",
                "objective":       "lead_generation",
                "daily_budget":    900.0,
                "total_budget":    27000.0,
                "start_date":      (date.today() - timedelta(days=75)).isoformat(),
                "target_audience": "28-55, India, Business owners",
            },
            "M-003": {
                "external_id":     "M-003",
                "name":            "Retargeting — Cart Abandonment",
                "platform":        "meta",
                "status":          "active",
                "objective":       "conversions",
                "daily_budget":    600.0,
                "total_budget":    18000.0,
                "start_date":      (date.today() - timedelta(days=45)).isoformat(),
                "target_audience": "All ages, Website visitors",
            },
        }

    def get_campaigns(self) -> list[dict]:
        return list(self._campaigns.values())

    def create_campaign(self, data: dict) -> dict:
        external_id = f"M-{uuid.uuid4().hex[:6].upper()}"
        campaign = {
            "external_id":     external_id,
            "name":            data.get("name", "Untitled Campaign"),
            "platform":        "meta",
            "status":          "created",
            "objective":       data.get("objective", "awareness"),
            "daily_budget":    data.get("daily_budget", 0.0),
            "total_budget":    data.get("total_budget", 0.0),
            "start_date":      data.get("start_date", date.today().isoformat()),
            "target_audience": data.get("target_audience", ""),
        }
        self._campaigns[external_id] = campaign
        logger.info("MetaAds: Created campaign %s — '%s'",
                    external_id, campaign["name"])
        return campaign

    def update_campaign(self, campaign_id: str, data: dict) -> dict:
        if campaign_id not in self._campaigns:
            logger.warning("MetaAds: Campaign %s not found.", campaign_id)
            return {"external_id": campaign_id, **data}
        self._campaigns[campaign_id].update({
            k: v for k, v in data.items() if k != "external_id"
        })
        logger.info("MetaAds: Updated campaign %s", campaign_id)
        return self._campaigns[campaign_id]

    def delete_campaign(self, campaign_id: str) -> bool:
        if campaign_id in self._campaigns:
            del self._campaigns[campaign_id]
            logger.info("MetaAds: Deleted campaign %s", campaign_id)
            return True
        return False

    def pause_campaign(self, campaign_id: str) -> bool:
        if campaign_id in self._campaigns:
            self._campaigns[campaign_id]["status"] = "paused"
            return True
        return False

    def resume_campaign(self, campaign_id: str) -> bool:
        if campaign_id in self._campaigns:
            self._campaigns[campaign_id]["status"] = "active"
            return True
        return False

    def get_metrics(self, campaign_id: str, days: int = 30) -> list[dict]:
        metrics = []
        base = {
            "impressions": 12000, "clicks": 480,
            "conversions": 24, "spend": 1150.0, "revenue": 4800.0
        }
        for i in range(days):
            day  = date.today() - timedelta(days=days - i)
            wm   = 0.80 if day.weekday() >= 5 else 1.0
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
"""
adapters/bing_ads_adapter.py
==============================
Simulates Microsoft Bing Ads API with internal storage.
create/update/delete operations actually persist within the session.
"""
import random
import uuid
import logging
from datetime import date, timedelta
from adapters.base_adapter import BaseAdapter

logger = logging.getLogger(__name__)
random.seed(55)


class BingAdsMockAdapter(BaseAdapter):

    def __init__(self):
        self._campaigns: dict[str, dict] = {
            "B-001": {
                "external_id":     "B-001",
                "name":            "Bing Search — Software Keywords",
                "platform":        "bing",
                "status":          "active",
                "objective":       "conversions",
                "daily_budget":    700.0,
                "total_budget":    21000.0,
                "start_date":      (date.today() - timedelta(days=89)).isoformat(),
                "target_audience": "25-55, US+India, Tech buyers",
            },
            "B-002": {
                "external_id":     "B-002",
                "name":            "Bing Display — Brand Campaign",
                "platform":        "bing",
                "status":          "active",
                "objective":       "awareness",
                "daily_budget":    400.0,
                "total_budget":    12000.0,
                "start_date":      (date.today() - timedelta(days=89)).isoformat(),
                "target_audience": "30-60, US, Enterprise buyers",
            },
        }

    def get_campaigns(self) -> list[dict]:
        return list(self._campaigns.values())

    def create_campaign(self, data: dict) -> dict:
        external_id = f"B-{uuid.uuid4().hex[:6].upper()}"
        campaign = {
            "external_id":     external_id,
            "name":            data.get("name", "Untitled Campaign"),
            "platform":        "bing",
            "status":          "created",
            "objective":       data.get("objective", "awareness"),
            "daily_budget":    data.get("daily_budget", 0.0),
            "total_budget":    data.get("total_budget", 0.0),
            "start_date":      data.get("start_date", date.today().isoformat()),
            "target_audience": data.get("target_audience", ""),
        }
        self._campaigns[external_id] = campaign
        logger.info("BingAds: Created campaign %s — '%s'",
                    external_id, campaign["name"])
        return campaign

    def update_campaign(self, campaign_id: str, data: dict) -> dict:
        if campaign_id not in self._campaigns:
            logger.warning("BingAds: Campaign %s not found.", campaign_id)
            return {"external_id": campaign_id, **data}
        self._campaigns[campaign_id].update({
            k: v for k, v in data.items() if k != "external_id"
        })
        logger.info("BingAds: Updated campaign %s", campaign_id)
        return self._campaigns[campaign_id]

    def delete_campaign(self, campaign_id: str) -> bool:
        if campaign_id in self._campaigns:
            del self._campaigns[campaign_id]
            logger.info("BingAds: Deleted campaign %s", campaign_id)
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
            "impressions": 1800, "clicks": 72,
            "conversions": 6, "spend": 648.0, "revenue": 1800.0
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
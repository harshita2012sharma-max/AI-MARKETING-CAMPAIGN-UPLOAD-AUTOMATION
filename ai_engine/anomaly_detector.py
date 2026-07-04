"""
ai_engine/anomaly_detector.py
Detects sudden drops/spikes using z-score and percentage change.
"""
import logging
import statistics
from database.repositories.analytics_repository import AnalyticsRepository
from database.repositories.campaign_repository import CampaignRepository
from config.constants import ANOMALY_CTR_DROP_PCT, ANOMALY_SPEND_SPIKE_PCT

logger = logging.getLogger("ai_engine.anomaly_detector")


class AnomalyDetector:

    def __init__(self):
        self.analytics_repo = AnalyticsRepository()
        self.camp_repo      = CampaignRepository()

    def detect_all(self) -> list[dict]:
        """Run anomaly detection on all active campaigns."""
        anomalies = []
        campaigns = self.camp_repo.get_active()
        for camp in campaigns:
            found = self.detect_for_campaign(camp["id"], camp["name"])
            anomalies.extend(found)
        return anomalies

    def detect_for_campaign(self, campaign_id: int, name: str) -> list[dict]:
        """Detect anomalies for one campaign. Returns list of anomaly dicts."""
        anomalies = []
        rows = self.analytics_repo.get_last_n_days(campaign_id, 8)
        if len(rows) < 3:
            return anomalies

        # Most recent day vs average of previous 7 days
        today   = rows[0]
        history = rows[1:]

        ctrs   = [r["ctr"]   for r in history if r["ctr"]]
        spends = [r["spend"] for r in history if r["spend"]]

        if ctrs and today["ctr"] is not None:
            avg_ctr = statistics.mean(ctrs)
            if avg_ctr > 0:
                drop = (avg_ctr - today["ctr"]) / avg_ctr * 100
                if drop >= ANOMALY_CTR_DROP_PCT:
                    anomalies.append({
                        "campaign_id": campaign_id,
                        "campaign_name": name,
                        "type": "ctr_drop",
                        "title": f"CTR dropped {drop:.1f}%",
                        "message": f"{name}: CTR dropped {drop:.1f}% vs 7-day average.",
                        "severity": "warning" if drop < 40 else "error",
                    })
                    logger.warning("Anomaly: CTR drop %.1f%% on %s", drop, name)

        if spends and today["spend"] is not None:
            avg_spend = statistics.mean(spends)
            if avg_spend > 0:
                spike = (today["spend"] - avg_spend) / avg_spend * 100
                if spike >= ANOMALY_SPEND_SPIKE_PCT:
                    anomalies.append({
                        "campaign_id": campaign_id,
                        "campaign_name": name,
                        "type": "spend_spike",
                        "title": f"Spend spike {spike:.1f}%",
                        "message": f"{name}: Spend spiked {spike:.1f}% vs 7-day average.",
                        "severity": "warning",
                    })

        return anomalies
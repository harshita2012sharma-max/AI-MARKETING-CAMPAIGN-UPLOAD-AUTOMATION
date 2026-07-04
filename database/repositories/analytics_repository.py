"""
database/repositories/analytics_repository.py
==============================================
All SQL for the daily_metrics table.
"""
import logging
from database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class AnalyticsRepository(BaseRepository):

    def insert_metric(self, data: dict) -> None:
        self.execute(
            """INSERT INTO daily_metrics
               (campaign_id,date,impressions,clicks,conversions,
                spend,revenue,ctr,cpc,cpa,roi)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)
               ON DUPLICATE KEY UPDATE
                   impressions = VALUES(impressions),
                   clicks      = VALUES(clicks),
                   conversions = VALUES(conversions),
                   spend       = VALUES(spend),
                   revenue     = VALUES(revenue),
                   ctr         = VALUES(ctr),
                   cpc         = VALUES(cpc),
                   cpa         = VALUES(cpa),
                   roi         = VALUES(roi)""",
            (data["campaign_id"], data["date"],
             data.get("impressions",0), data.get("clicks",0),
             data.get("conversions",0), data.get("spend",0.0),
             data.get("revenue",0.0), data.get("ctr",0.0),
             data.get("cpc",0.0), data.get("cpa",0.0), data.get("roi",0.0))
        )

    def get_last_n_days(self, campaign_id: int, days: int = 30) -> list[dict]:
        return self.fetchall(
            "SELECT * FROM daily_metrics WHERE campaign_id=? ORDER BY date DESC LIMIT ?",
            (campaign_id, days)
        )

    def get_all_platform_summary(self, days: int = 30) -> list[dict]:
        return self.fetchall(
            """SELECT c.platform,
                 SUM(dm.impressions) AS total_impressions,
                 SUM(dm.clicks)      AS total_clicks,
                 SUM(dm.conversions) AS total_conversions,
                 ROUND(SUM(dm.spend),2)   AS total_spend,
                 ROUND(SUM(dm.revenue),2) AS total_revenue,
                 ROUND(AVG(dm.ctr),4)     AS avg_ctr,
                 ROUND(AVG(dm.cpc),4)     AS avg_cpc,
                 ROUND(AVG(dm.roi),4)     AS avg_roi
               FROM daily_metrics dm
               JOIN campaigns c ON c.id=dm.campaign_id
               WHERE dm.date >= DATE_SUB(CURDATE(), INTERVAL ? DAY)
               GROUP BY c.platform""",
            (days,)
        )

    def get_daily_totals(self, days: int = 30) -> list[dict]:
        return self.fetchall(
            """SELECT dm.date,
                 SUM(dm.impressions)     AS impressions,
                 SUM(dm.clicks)          AS clicks,
                 SUM(dm.conversions)     AS conversions,
                 ROUND(SUM(dm.spend),2)  AS spend,
                 ROUND(SUM(dm.revenue),2) AS revenue
               FROM daily_metrics dm
               WHERE dm.date >= DATE_SUB(CURDATE(), INTERVAL ? DAY)
               GROUP BY dm.date ORDER BY dm.date ASC""",
            (days,)
        )

    def get_campaign_summary(self, campaign_id: int) -> dict:
        return self.fetchone(
            """SELECT COUNT(*) AS total_days,
                 SUM(impressions) AS total_impressions,
                 SUM(clicks)      AS total_clicks,
                 SUM(conversions) AS total_conversions,
                 ROUND(SUM(spend),2)   AS total_spend,
                 ROUND(SUM(revenue),2) AS total_revenue,
                 ROUND(AVG(ctr),4) AS avg_ctr,
                 ROUND(AVG(cpc),4) AS avg_cpc,
                 ROUND(AVG(cpa),4) AS avg_cpa,
                 ROUND(AVG(roi),4) AS avg_roi
               FROM daily_metrics WHERE campaign_id=?""",
            (campaign_id,)
        ) or {}

    def get_top_campaigns_by_roi(self, days: int = 30, limit: int = 5) -> list[dict]:
        return self.fetchall(
            """SELECT c.id,c.name,c.platform,c.status,
                 ROUND(AVG(dm.roi),4)    AS avg_roi,
                 ROUND(SUM(dm.spend),2)  AS total_spend,
                 ROUND(SUM(dm.revenue),2) AS total_revenue,
                 SUM(dm.conversions)     AS total_conversions
               FROM daily_metrics dm
               JOIN campaigns c ON c.id=dm.campaign_id
               WHERE dm.date >= DATE_SUB(CURDATE(), INTERVAL ? DAY)
               GROUP BY dm.campaign_id
               ORDER BY avg_roi DESC LIMIT ?""",
            (days, limit)
        )

    def get_worst_campaigns(self, days: int = 7, limit: int = 5) -> list[dict]:
        return self.fetchall(
            """SELECT c.id,c.name,c.platform,c.status,
                 ROUND(AVG(dm.roi),4) AS avg_roi,
                 ROUND(AVG(dm.cpc),4) AS avg_cpc,
                 ROUND(AVG(dm.ctr),4) AS avg_ctr,
                 SUM(dm.conversions)  AS total_conversions
               FROM daily_metrics dm
               JOIN campaigns c ON c.id=dm.campaign_id
               WHERE dm.date >= DATE_SUB(CURDATE(), INTERVAL ? DAY) AND c.status='active'
               GROUP BY dm.campaign_id
               ORDER BY avg_roi ASC, avg_cpc DESC LIMIT ?""",
            (days, limit)
        )
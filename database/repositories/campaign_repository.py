"""
database/repositories/campaign_repository.py
============================================
All SQL for the campaigns table.
"""
import logging
from typing import Optional
from database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class CampaignRepository(BaseRepository):

    def create(self, data: dict) -> int:
        cur = self.execute(
            """INSERT INTO campaigns
               (external_id,name,platform,status,objective,
                daily_budget,total_budget,spent_total,
                start_date,end_date,target_audience,keywords,
                health_score,created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (data["external_id"], data["name"], data["platform"],
             data.get("status","draft"), data.get("objective","awareness"),
             data.get("daily_budget",0.0), data.get("total_budget",0.0),
             data.get("spent_total",0.0), data["start_date"],
             data.get("end_date"), data.get("target_audience",""),
             data.get("keywords","[]"), data.get("health_score",0.0),
             data["created_by"])
        )
        return cur.lastrowid

    def get_by_id(self, campaign_id: int) -> Optional[dict]:
        return self.fetchone("SELECT * FROM campaigns WHERE id=?", (campaign_id,))

    def get_by_external_id(self, external_id: str) -> Optional[dict]:
        return self.fetchone("SELECT * FROM campaigns WHERE external_id=?", (external_id,))

    def get_all(self, platform=None, status=None, page=1, per_page=50) -> list[dict]:
        conditions, params = [], []
        if platform:
            conditions.append("platform=?"); params.append(platform)
        if status:
            conditions.append("status=?"); params.append(status)
        where  = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        offset = (page - 1) * per_page
        params += [per_page, offset]
        return self.fetchall(
            f"SELECT * FROM campaigns {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            tuple(params)
        )

    def get_active(self) -> list[dict]:
        return self.fetchall("SELECT * FROM campaigns WHERE status='active'")

    def update(self, campaign_id: int, data: dict) -> bool:
        allowed = {"name","status","objective","daily_budget","total_budget",
                   "end_date","target_audience","keywords","health_score"}
        updates = {k: v for k, v in data.items() if k in allowed}
        if not updates:
            return False
        set_clause = ", ".join(f"{k}=?" for k in updates)
        cur = self.execute(
            f"UPDATE campaigns SET {set_clause} WHERE id=?",
            tuple(list(updates.values()) + [campaign_id])
        )
        return cur.rowcount > 0

    def update_status(self, campaign_id: int, status: str) -> bool:
        cur = self.execute("UPDATE campaigns SET status=? WHERE id=?", (status, campaign_id))
        return cur.rowcount > 0

    def update_health_score(self, campaign_id: int, score: float) -> None:
        self.execute("UPDATE campaigns SET health_score=? WHERE id=?", (round(score,2), campaign_id))

    def update_spent(self, campaign_id: int, spent_total: float) -> None:
        self.execute("UPDATE campaigns SET spent_total=? WHERE id=?", (round(spent_total,2), campaign_id))

    def delete(self, campaign_id: int) -> bool:
        cur = self.execute("UPDATE campaigns SET status='ended' WHERE id=?", (campaign_id,))
        return cur.rowcount > 0

    def search(self, query: str) -> list[dict]:
        like = f"%{query}%"
        return self.fetchall(
            "SELECT * FROM campaigns WHERE name LIKE ? OR target_audience LIKE ?", (like, like)
        )

    def count_by_platform(self) -> dict:
        rows = self.fetchall("SELECT platform, COUNT(*) as cnt FROM campaigns GROUP BY platform")
        return {r["platform"]: r["cnt"] for r in rows}

    def count_by_status(self) -> dict:
        rows = self.fetchall("SELECT status, COUNT(*) as cnt FROM campaigns GROUP BY status")
        return {r["status"]: r["cnt"] for r in rows}
"""
database/seed.py
================
Generates 90 days of realistic campaign data for all three platforms.
Run once on startup. Safe to call multiple times — skips if data exists.
"""

import hashlib
import json
import logging
import random
from datetime import date, timedelta
from database.connection import get_connection

logger = logging.getLogger(__name__)
random.seed(42)

CAMPAIGN_DEFINITIONS: list[dict] = [
    {
        "external_id": "G-001", "name": "Diwali Sale — Google Search",
        "platform": "google", "status": "active", "objective": "conversions",
        "daily_budget": 1500.0, "total_budget": 45000.0,
        "start_date": (date.today() - timedelta(days=89)).isoformat(),
        "target_audience": "25-45, India, Shopping interest",
        "keywords": json.dumps(["diwali sale", "online deals", "festive offers"]),
        "_base": {"impressions": 3200, "clicks": 102, "conversions": 9, "spend": 1280.0, "revenue": 3200.0},
    },
    {
        "external_id": "G-002", "name": "Brand Awareness — Google Display",
        "platform": "google", "status": "active", "objective": "awareness",
        "daily_budget": 800.0, "total_budget": 24000.0,
        "start_date": (date.today() - timedelta(days=89)).isoformat(),
        "target_audience": "18-35, India, Tech interest",
        "keywords": json.dumps(["brand", "software", "saas"]),
        "_base": {"impressions": 8500, "clicks": 68, "conversions": 2, "spend": 760.0, "revenue": 900.0},
    },
    {
        "external_id": "G-003", "name": "Product Launch — Google Search",
        "platform": "google", "status": "paused", "objective": "conversions",
        "daily_budget": 2000.0, "total_budget": 60000.0,
        "start_date": (date.today() - timedelta(days=60)).isoformat(),
        "target_audience": "30-50, India, Business decision makers",
        "keywords": json.dumps(["marketing software", "campaign tool", "ad automation"]),
        "_base": {"impressions": 1200, "clicks": 14, "conversions": 0, "spend": 980.0, "revenue": 0.0},
    },
    {
        "external_id": "M-001", "name": "Instagram Reels — Summer Collection",
        "platform": "meta", "status": "active", "objective": "awareness",
        "daily_budget": 1200.0, "total_budget": 36000.0,
        "start_date": (date.today() - timedelta(days=89)).isoformat(),
        "target_audience": "18-30, India, Fashion interest",
        "keywords": json.dumps(["summer fashion", "new collection", "instagram style"]),
        "_base": {"impressions": 12000, "clicks": 480, "conversions": 24, "spend": 1150.0, "revenue": 4800.0},
    },
    {
        "external_id": "M-002", "name": "Facebook Lead Gen — B2B",
        "platform": "meta", "status": "active", "objective": "lead_generation",
        "daily_budget": 900.0, "total_budget": 27000.0,
        "start_date": (date.today() - timedelta(days=75)).isoformat(),
        "target_audience": "28-55, India, Business owners",
        "keywords": json.dumps(["b2b leads", "business software", "enterprise"]),
        "_base": {"impressions": 4200, "clicks": 126, "conversions": 11, "spend": 860.0, "revenue": 2750.0},
    },
    {
        "external_id": "M-003", "name": "Retargeting — Cart Abandonment",
        "platform": "meta", "status": "active", "objective": "conversions",
        "daily_budget": 600.0, "total_budget": 18000.0,
        "start_date": (date.today() - timedelta(days=45)).isoformat(),
        "target_audience": "All ages, Website visitors",
        "keywords": json.dumps(["retarget", "cart abandonment", "purchase reminder"]),
        "_base": {"impressions": 2800, "clicks": 224, "conversions": 28, "spend": 580.0, "revenue": 5600.0},
    },
    {
        "external_id": "B-001", "name": "Bing Search — Software Keywords",
        "platform": "bing", "status": "active", "objective": "conversions",
        "daily_budget": 700.0, "total_budget": 21000.0,
        "start_date": (date.today() - timedelta(days=89)).isoformat(),
        "target_audience": "25-55, US+India, Tech buyers",
        "keywords": json.dumps(["marketing software", "automation tool", "ad platform"]),
        "_base": {"impressions": 1800, "clicks": 72, "conversions": 6, "spend": 648.0, "revenue": 1800.0},
    },
    {
        "external_id": "B-002", "name": "Bing Display — Brand Campaign",
        "platform": "bing", "status": "active", "objective": "awareness",
        "daily_budget": 400.0, "total_budget": 12000.0,
        "start_date": (date.today() - timedelta(days=89)).isoformat(),
        "target_audience": "30-60, US, Enterprise buyers",
        "keywords": json.dumps(["enterprise software", "cloud tools"]),
        "_base": {"impressions": 3600, "clicks": 54, "conversions": 2, "spend": 380.0, "revenue": 600.0},
    },
]


def _variance(base: float, pct: float = 0.15) -> float:
    return max(0.0, base + random.uniform(-base * pct, base * pct))

def _weekend_multiplier(day: date) -> float:
    return 0.70 if day.weekday() >= 5 else 1.0

def _compute_derived(impressions, clicks, conversions, spend, revenue) -> dict:
    return {
        "ctr": round(clicks / impressions * 100, 4) if impressions else 0.0,
        "cpc": round(spend / clicks, 4)             if clicks else 0.0,
        "cpa": round(spend / conversions, 4)        if conversions else 0.0,
        "roi": round(revenue / spend, 4)            if spend else 0.0,
    }

def _seed_users(conn) -> dict:
    users = [
        ("admin",   "admin@adpulse.io",   "admin",   "admin"),
        ("manager", "manager@adpulse.io", "manager", "manager"),
        ("viewer",  "viewer@adpulse.io",  "viewer",  "viewer"),
    ]

    user_ids = {}

    for username, email, password, role in users:
        pw_hash = hashlib.sha256(password.encode()).hexdigest()

        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                "INSERT IGNORE INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                (username, email, pw_hash, role)
            )

            conn.commit()

            cursor.execute(
                "SELECT id FROM users WHERE username=%s",
                (username,)
            )

            row = cursor.fetchone()

            if row:
                user_ids[username] = row["id"]

        except Exception as e:
            logger.warning("User seed skipped %s: %s", username, e)

        finally:
            cursor.close()

    return user_ids

def _seed_campaigns(conn, admin_id) -> list:
    seeded = []

    for camp in CAMPAIGN_DEFINITIONS:
        base = camp["_base"]
        start = camp["start_date"]
        days = (date.today() - date.fromisoformat(start)).days + 1

        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """INSERT IGNORE INTO campaigns
                   (external_id,name,platform,status,objective,
                    daily_budget,total_budget,spent_total,
                    start_date,target_audience,keywords,health_score,created_by)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    camp["external_id"],
                    camp["name"],
                    camp["platform"],
                    camp["status"],
                    camp["objective"],
                    camp["daily_budget"],
                    camp["total_budget"],
                    round(base["spend"] * days * 0.95, 2),
                    start,
                    camp.get("target_audience", ""),
                    camp.get("keywords", "[]"),
                    0.0,
                    admin_id,
                ),
            )

            conn.commit()

            cursor.execute(
                "SELECT id FROM campaigns WHERE external_id=%s",
                (camp["external_id"],),
            )

            row = cursor.fetchone()

            if row:
                seeded.append(
                    {
                        "id": row["id"],
                        "start_date": start,
                        "_base": base,
                    }
                )

        except Exception as e:
            logger.warning("Campaign seed skipped %s: %s", camp["name"], e)
            continue

        finally:
            cursor.close()

    return seeded

def _seed_metrics(conn, seeded_campaigns) -> None:
    today = date.today()

    cursor = conn.cursor(dictionary=True)

    for camp in seeded_campaigns:
        base = camp["_base"]
        current = date.fromisoformat(camp["start_date"])

        while current <= today:
            wm = _weekend_multiplier(current)

            imp = max(1, int(_variance(base["impressions"]) * wm))
            clk = max(0, min(imp, int(_variance(base["clicks"]) * wm)))
            conv = max(0, min(clk, int(_variance(base["conversions"]) * wm)))

            spnd = round(_variance(base["spend"]) * wm, 2)
            rev = round(_variance(base["revenue"]) * wm, 2)

            d = _compute_derived(imp, clk, conv, spnd, rev)

            try:
                cursor.execute(
                    """INSERT IGNORE INTO daily_metrics
                       (campaign_id,date,impressions,clicks,conversions,
                        spend,revenue,ctr,cpc,cpa,roi)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        camp["id"],
                        current.isoformat(),
                        imp,
                        clk,
                        conv,
                        spnd,
                        rev,
                        d["ctr"],
                        d["cpc"],
                        d["cpa"],
                        d["roi"],
                    ),
                )
            except Exception:
                pass

            current += timedelta(days=1)

    conn.commit()
    cursor.close()

def _seed_notifications(conn, admin_id) -> None:
    notes = [
        (admin_id, "Welcome to AdPulse!", "Your platform is ready. Campaigns have been synced.", "success"),
        (admin_id, "AI Analysis Complete", "8 campaigns analysed. 2 recommendations generated.", "info"),
        (admin_id, "Anomaly Detected", "Google Display CTR dropped 28% vs 7-day average.", "warning"),
    ]

    cursor = conn.cursor()

    for uid, title, msg, ntype in notes:
        try:
            cursor.execute(
                "INSERT IGNORE INTO notifications (user_id,title,message,type) VALUES (%s,%s,%s,%s)",
                (uid, title, msg, ntype)
            )
        except Exception:
            pass

    conn.commit()
    cursor.close()

def run_seed() -> None:
    """Main entry point. Called from app.py on startup."""

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS cnt FROM campaigns")

    existing = cursor.fetchone()

    cursor.close()

    if existing and existing["cnt"] > 0:
        logger.info("Seed skipped — %d campaigns already exist.", existing["cnt"])
        return

    logger.info("Starting database seed...")

    user_ids = _seed_users(conn)
    admin_id = user_ids.get("admin", 1)

    seeded = _seed_campaigns(conn, admin_id)

    _seed_metrics(conn, seeded)

    _seed_notifications(conn, admin_id)

    logger.info("Seed complete. %d campaigns created.", len(seeded))
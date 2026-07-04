from database.connection import get_connection

conn = get_connection()

conn.executescript("""
CREATE TABLE IF NOT EXISTS campaign_platforms (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id   INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    platform      TEXT    NOT NULL CHECK(platform IN ('google','meta','bing')),
    external_id   TEXT    NOT NULL,
    status        TEXT    NOT NULL DEFAULT 'created'
                          CHECK(status IN ('created','active','paused','failed','syncing')),
    synced_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    error_message TEXT,
    UNIQUE(campaign_id, platform)
);

CREATE INDEX IF NOT EXISTS idx_camp_platforms_campaign
    ON campaign_platforms(campaign_id);

CREATE INDEX IF NOT EXISTS idx_camp_platforms_platform
    ON campaign_platforms(platform);
""")

print("campaign_platforms table created OK")

# Verify
row = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='campaign_platforms'"
).fetchone()
print("Table exists:", row is not None)
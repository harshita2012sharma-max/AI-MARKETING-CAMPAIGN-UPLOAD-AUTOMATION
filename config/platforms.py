"""
config/platforms.py
====================
THIS IS THE ONLY FILE YOU CHANGE TO SWAP MOCK TO REAL APIS.

To connect real Google Ads:
1. Create adapters/google_ads_real.py
2. Change ADAPTERS["google"] to point to it
3. Restart app — done. Nothing else changes.
"""

ADAPTERS: dict[str, str] = {
    "google": "adapters.google_ads_adapter.GoogleAdsMockAdapter",
    "meta":   "adapters.meta_ads_adapter.MetaAdsMockAdapter",
    "bing":   "adapters.bing_ads_adapter.BingAdsMockAdapter",
}
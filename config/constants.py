"""
config/constants.py
====================
All magic numbers live here — never hardcoded in business logic.
Change a threshold here and it applies everywhere automatically.
"""

# Health Score Weights (must sum to 1.0)
HEALTH_WEIGHT_ROI: float = 0.40
HEALTH_WEIGHT_CTR: float = 0.30
HEALTH_WEIGHT_CPC: float = 0.30

# Anomaly Detection Thresholds
ANOMALY_CTR_DROP_PCT: float     = 25.0
ANOMALY_SPEND_SPIKE_PCT: float  = 30.0
ANOMALY_CONV_DROP_PCT: float    = 40.0
ANOMALY_ZSCORE_THRESHOLD: float = 2.0

# Campaign Health Score Ranges
HEALTH_EXCELLENT: int = 80
HEALTH_GOOD: int      = 60
HEALTH_WARNING: int   = 40

# Benchmark KPIs (Indian market averages)
BENCHMARK_CTR_GOOD: float = 2.0
BENCHMARK_CTR_POOR: float = 0.5
BENCHMARK_CPC_HIGH: float = 50.0
BENCHMARK_ROI_GOOD: float = 2.0
BENCHMARK_ROI_POOR: float = 1.0

# Forecasting
FORECAST_DAYS_SHORT: int = 7
FORECAST_DAYS_LONG: int  = 30

# Pagination
DEFAULT_PAGE_SIZE: int = 20

# Platform Labels
PLATFORMS: dict[str, str] = {
    "google": "Google Ads",
    "meta":   "Meta Ads",
    "bing":   "Bing Ads",
}

PLATFORM_COLORS: dict[str, str] = {
    "google": "#4285F4",
    "meta":   "#1877F2",
    "bing":   "#00809D",
}

# Campaign Status
STATUS_COLORS: dict[str, str] = {
    "active": "success",
    "paused": "warning",
    "ended":  "error",
    "draft":  "info",
}

# AI Decision Types
AI_DECISION_TYPES: list[str] = [
    "recommend",
    "anomaly",
    "forecast",
    "auto_action",
]
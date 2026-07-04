"""
test_backend.py
Run this to verify all backend systems work.
Command: python test_backend.py
"""

print("=" * 50)
print("ADPULSE BACKEND TEST")
print("=" * 50)

# Test 1: Adapters
print("\n1. Testing Adapters...")
try:
    from adapters.adapter_factory import AdapterFactory
    for p in ["google", "meta", "bing"]:
        a = AdapterFactory.get(p)
        c = a.get_campaigns()
        print(f"   {p}: {len(c)} campaigns OK")
    print("   ADAPTERS OK")
except Exception as e:
    print(f"   ADAPTERS FAILED: {e}")

# Test 2: Analytics
print("\n2. Testing Analytics...")
try:
    from services.analytics_service import AnalyticsService
    kpis = AnalyticsService().get_dashboard_kpis(30)
    print(f"   Total Spend:    {kpis['total_spend']}")
    print(f"   Total Clicks:   {kpis['total_clicks']}")
    print(f"   Total Revenue:  {kpis['total_revenue']}")
    print(f"   Avg ROI:        {kpis['avg_roi']}")
    print(f"   Avg CTR:        {kpis['avg_ctr']}")
    print("   ANALYTICS OK")
except Exception as e:
    print(f"   ANALYTICS FAILED: {e}")

# Test 3: AI Engine
print("\n3. Testing AI Engine...")
try:
    from ai_engine.performance_analyzer import PerformanceAnalyzer
    from ai_engine.anomaly_detector import AnomalyDetector
    from ai_engine.recommender import Recommender
    from ai_engine.forecasting_engine import ForecastingEngine
    from ai_engine.roi_predictor import ROIPredictor

    scores    = PerformanceAnalyzer().score_all_campaigns()
    recs      = Recommender().recommend_all()
    anomalies = AnomalyDetector().detect_all()
    forecasts = ForecastingEngine().forecast_all_campaigns(7)
    roi_preds = ROIPredictor().predict_all(7)

    print(f"   Campaigns scored:      {len(scores)}")
    print(f"   Recommendations:       {len(recs)}")
    print(f"   Anomalies detected:    {len(anomalies)}")
    print(f"   Forecasts generated:   {len(forecasts)}")
    print(f"   ROI predictions:       {len(roi_preds)}")
    print("   AI ENGINE OK")
except Exception as e:
    print(f"   AI ENGINE FAILED: {e}")

# Test 4: Services
print("\n4. Testing Services...")
try:
    from services.campaign_service import CampaignService
    from services.budget_service import BudgetService
    from services.notification_service import NotificationService
    from services.auth_service import AuthService

    camps  = CampaignService().get_all()
    budget = BudgetService().get_spend_summary()
    notifs = NotificationService().get_for_user(1)
    user   = AuthService().login("admin", "admin")

    print(f"   Campaigns in DB:       {len(camps)}")
    print(f"   Monthly spend:         {budget['monthly_spend']}")
    print(f"   Notifications:         {len(notifs)}")
    print(f"   Admin login:           {'OK' if user else 'FAILED'}")
    print("   SERVICES OK")
except Exception as e:
    print(f"   SERVICES FAILED: {e}")

# Test 5: Multi-platform sync
print("\n5. Testing Multi-Platform Sync...")
try:
    from services.sync_service import SyncService
    from services.campaign_service import CampaignService

    test_data = {
        "name":          "Test Sync Campaign",
        "platform":      "google",
        "objective":     "awareness",
        "daily_budget":  500.0,
        "total_budget":  15000.0,
        "start_date":    "2024-01-01",
        "target_audience": "Test audience",
        "keywords":      "[]",
    }

    result = CampaignService().create(test_data, user_id=1)
    sync   = result["sync_results"]

    print(f"   Campaign ID:     {result['campaign_id']}")
    for platform, info in sync.items():
        status = "OK" if info["success"] else "FAILED"
        print(f"   {platform:6}: {info['external_id']}  [{status}]")
    print("   SYNC OK")
except Exception as e:
    print(f"   SYNC FAILED: {e}")

print()
print("=" * 50)
print("ALL BACKEND TESTS COMPLETE")
print("=" * 50)
print()
print("Next step: python run.py")
print("Then open: http://localhost:5000")
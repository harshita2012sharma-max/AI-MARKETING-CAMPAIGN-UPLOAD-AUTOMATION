"""
services/rule_engine_service.py
=================================
Evaluates user-defined automation rules against live campaign data.

Example rules:
  IF cpc > 50 AND conversions < 5 THEN pause campaign
  IF roi > 3.0 THEN increase budget by 20%
  IF ctr < 0.5 THEN send notification

Rules are stored in the settings table as JSON.
This engine runs every scheduler cycle.
"""

import json
import logging
from database.repositories.analytics_repository import AnalyticsRepository
from database.repositories.campaign_repository import CampaignRepository
from database.repositories.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)

# Built-in default rules — always active
DEFAULT_RULES: list[dict] = [
    {
        "id":        "rule_001",
        "name":      "Auto-pause losing campaigns",
        "condition": {"metric": "roi", "operator": "<", "value": 0.5},
        "action":    "pause",
        "description": "Pause any campaign with ROI below 0.5x",
        "enabled":   True,
    },
    {
        "id":        "rule_002",
        "name":      "Alert on high CPC",
        "condition": {"metric": "avg_cpc", "operator": ">", "value": 80.0},
        "action":    "notify",
        "description": "Send alert when CPC exceeds Rs 80",
        "enabled":   True,
    },
    {
        "id":        "rule_003",
        "name":      "Alert on low CTR",
        "condition": {"metric": "avg_ctr", "operator": "<", "value": 0.3},
        "action":    "notify",
        "description": "Send alert when CTR drops below 0.3%",
        "enabled":   True,
    },
]


def _evaluate_condition(actual_value: float, operator: str, threshold: float) -> bool:
    """
    Check if a metric value satisfies a rule condition.

    Args:
        actual_value: Current metric value.
        operator:     One of: '<', '>', '<=', '>=', '=='.
        threshold:    The rule threshold value.

    Returns:
        True if condition is met, False otherwise.
    """
    ops = {
        "<":  actual_value < threshold,
        ">":  actual_value > threshold,
        "<=": actual_value <= threshold,
        ">=": actual_value >= threshold,
        "==": abs(actual_value - threshold) < 0.001,
    }
    return ops.get(operator, False)


class RuleEngineService:
    """Evaluates automation rules against active campaign data."""

    def __init__(self):
        self.analytics_repo    = AnalyticsRepository()
        self.camp_repo         = CampaignRepository()
        self.notification_repo = NotificationRepository()

    def run_all_rules(self, admin_user_id: int = 1) -> list[dict]:
        """
        Run all default rules against all active campaigns.

        Args:
            admin_user_id: User ID to send notifications to.

        Returns:
            List of triggered rule results.
        """
        campaigns = self.camp_repo.get_active()
        triggered = []

        for camp in campaigns:
            summary = self.analytics_repo.get_campaign_summary(camp["id"])
            if not summary:
                continue

            for rule in DEFAULT_RULES:
                if not rule.get("enabled"):
                    continue

                condition = rule["condition"]
                metric    = condition["metric"]
                operator  = condition["operator"]
                threshold = condition["value"]

                actual = summary.get(metric, 0) or 0

                if _evaluate_condition(actual, operator, threshold):
                    result = self._execute_action(
                        rule, camp, actual, admin_user_id
                    )
                    triggered.append(result)
                    logger.info(
                        "Rule '%s' triggered on '%s': %s=%.4f %s %.4f",
                        rule["name"], camp["name"],
                        metric, actual, operator, threshold
                    )

        return triggered

    def _execute_action(self, rule: dict, camp: dict,
                        actual_value: float, admin_user_id: int) -> dict:
        """
        Execute the action for a triggered rule.

        Actions supported: pause | notify
        """
        action      = rule.get("action")
        campaign_id = camp["id"]
        camp_name   = camp["name"]

        result = {
            "rule_id":       rule["id"],
            "rule_name":     rule["name"],
            "campaign_id":   campaign_id,
            "campaign_name": camp_name,
            "action":        action,
            "actual_value":  actual_value,
            "executed":      False,
        }

        if action == "pause":
            self.camp_repo.update_status(campaign_id, "paused")
            self.notification_repo.create(
                user_id=admin_user_id,
                title=f"Auto-paused: {camp_name}",
                message=f"Rule '{rule['name']}' triggered. Campaign paused automatically.",
                ntype="warning",
                related_id=campaign_id
            )
            result["executed"] = True

        elif action == "notify":
            self.notification_repo.create(
                user_id=admin_user_id,
                title=f"Rule Alert: {rule['name']}",
                message=(
                    f"Campaign '{camp_name}': {rule['description']}. "
                    f"Current value: {actual_value:.4f}"
                ),
                ntype="warning",
                related_id=campaign_id
            )
            result["executed"] = True

        return result
"""
adapters/base_adapter.py
Abstract base class all platform adapters must follow.
"""
from abc import ABC, abstractmethod


class BaseAdapter(ABC):

    @abstractmethod
    def get_campaigns(self) -> list[dict]:
        """Return all campaigns from this platform."""
        pass

    @abstractmethod
    def create_campaign(self, data: dict) -> dict:
        """Create a new campaign. Return created campaign dict."""
        pass

    @abstractmethod
    def update_campaign(self, campaign_id: str, data: dict) -> dict:
        """Update campaign fields. Return updated campaign dict."""
        pass

    @abstractmethod
    def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign. Return True if successful."""
        pass

    @abstractmethod
    def get_metrics(self, campaign_id: str, days: int = 30) -> list[dict]:
        """Return daily metrics for a campaign."""
        pass

    @abstractmethod
    def pause_campaign(self, campaign_id: str) -> bool:
        """Pause a running campaign."""
        pass

    @abstractmethod
    def resume_campaign(self, campaign_id: str) -> bool:
        """Resume a paused campaign."""
        pass
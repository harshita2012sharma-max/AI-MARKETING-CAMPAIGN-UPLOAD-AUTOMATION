"""
adapters/adapter_factory.py
=============================
Loads the correct adapter class based on config/platforms.py

Improvement: Caches adapter instances so the same object is
reused across calls. This is important because adapters now
have internal storage — creating a new object every time would
lose all previously created campaigns.
"""
import importlib
import logging
from config.platforms import ADAPTERS
from adapters.base_adapter import BaseAdapter

logger = logging.getLogger(__name__)

# Cache: stores one instance per platform
# { "google": GoogleAdsMockAdapter(), "meta": ..., "bing": ... }
_adapter_cache: dict[str, BaseAdapter] = {}


class AdapterFactory:

    @staticmethod
    def get(platform: str) -> BaseAdapter:
        """
        Return the adapter instance for a platform.
        Returns cached instance if already created.

        Args:
            platform: 'google' | 'meta' | 'bing'

        Returns:
            Adapter instance (cached).
        """
        if platform not in ADAPTERS:
            raise ValueError(
                f"Unknown platform '{platform}'. "
                f"Available: {list(ADAPTERS.keys())}"
            )

        # Return cached instance if exists
        if platform in _adapter_cache:
            return _adapter_cache[platform]

        # Create new instance and cache it
        class_path  = ADAPTERS[platform]
        module_path, class_name = class_path.rsplit(".", 1)

        try:
            module   = importlib.import_module(module_path)
            cls      = getattr(module, class_name)
            instance = cls()
            _adapter_cache[platform] = instance
            logger.info("Adapter created and cached for platform: %s", platform)
            return instance
        except (ImportError, AttributeError) as exc:
            logger.error("Failed to load adapter %s: %s", class_path, exc)
            raise

    @staticmethod
    def get_all() -> dict[str, BaseAdapter]:
        """Return all 3 adapter instances at once."""
        return {
            platform: AdapterFactory.get(platform)
            for platform in ADAPTERS.keys()
        }

    @staticmethod
    def clear_cache() -> None:
        """
        Clear the adapter cache.
        Call this if you switch from mock to real adapters at runtime.
        """
        _adapter_cache.clear()
        logger.info("Adapter cache cleared.")
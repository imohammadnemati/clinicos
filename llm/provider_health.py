import asyncio
import logging
from typing import Dict, Optional
from .cooldown_manager import CooldownManager
from .quota_manager import QuotaManager
from .metrics import MetricsCollector

logger = logging.getLogger(__name__)

class ProviderHealth:
    def __init__(self, cooldown_manager: CooldownManager, quota_manager: QuotaManager, metrics: MetricsCollector):
        self.cooldown = cooldown_manager
        self.quota = quota_manager
        self.metrics = metrics
    
    def is_provider_usable(self, provider_name: str) -> bool:
        if self.cooldown.is_in_cooldown(provider_name):
            return False
        # Also could check if remaining quota is zero, but that is handled in weight.
        return True
    
    def get_health_status(self, provider_name: str) -> dict:
        return {
            "cooldown_remaining": self.cooldown.remaining_cooldown(provider_name),
            "rpm_usage": self.quota.get_rpm_usage(provider_name),
            "remaining_quota": self.quota.get_remaining_quota(provider_name),
            "avg_latency": self.metrics.get_average_latency(provider_name),
            "success_rate": self.metrics.get_success_rate(provider_name),
            "last_error": self.metrics.last_error.get(provider_name)
        }

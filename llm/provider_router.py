import asyncio
import time
import random
import logging
from typing import List, Tuple, Dict, Any, Optional
from .provider_manager import ProviderManager
from .exceptions import ProviderUnavailableError

logger = logging.getLogger(__name__)

class ProviderRouter:
    def __init__(self, config: dict):
        self.manager = ProviderManager(config)
        self.task_profiles = {
            "medical_risk": ["gemini", "openai"],        # preferred order
            "facts_extraction": ["qwen", "deepseek"],
            "reply_generation": ["deepseek", "openrouter", "qwen", "gemini", "openai"]
        }
        self.provider_weights = self._compute_initial_weights()
    
    def _compute_initial_weights(self) -> Dict[str, float]:
        """Compute priority_weight = (score * 0.7) + (normalized_remaining_quota * 0.3)"""
        weights = {}
        for name in self.manager.get_all_provider_names():
            score = self.manager.scoring.get_score(name)
            # Normalize remaining quota (0-1). Assume unknown = 0.5.
            quota = self.manager.quota.get_remaining_quota(name)
            if quota is None:
                norm_quota = 0.5
            else:
                # Assume max daily quota = 1000 for normalization (configurable)
                max_quota = 1000
                norm_quota = min(1.0, quota / max_quota)
            weight = (score * 0.7) + (norm_quota * 0.3)
            weights[name] = weight
        return weights
    
    def _update_weights(self):
        """Recalculate weights (called after each request)."""
        self.provider_weights = self._compute_initial_weights()
    
    def _get_sorted_providers_for_task(self, task: str) -> List[str]:
        """Get providers sorted by priority_weight, respecting task profile if provided."""
        all_providers = self.manager.get_all_provider_names()
        # Start with task preference order
        preferred = self.task_profiles.get(task, [])
        # Ensure all providers are considered, with priority to preferred first
        ordered = []
        for p in preferred:
            if p in all_providers and p not in ordered:
                ordered.append(p)
        for p in all_providers:
            if p not in ordered:
                ordered.append(p)
        # Now sort by priority_weight descending, but keep preference order as tie-breaker
        # Actually, we want to sort by weight, but weight already includes quota.
        ordered.sort(key=lambda x: self.provider_weights.get(x, 0), reverse=True)
        return ordered
    
    async def generate(self, prompt: str, task: str = "reply_generation", **kwargs) -> str:
        """Generate response using best available provider with failover."""
        providers_order = self._get_sorted_providers_for_task(task)
        last_exception = None
        for provider_name in providers_order:
            provider = self.manager.get_provider(provider_name)
            if not provider or not provider.is_available():
                continue
            if self.manager.cooldown.is_in_cooldown(provider_name):
                logger.debug(f"Provider {provider_name} in cooldown, skipping")
                continue
            start_time = time.time()
            try:
                response = await provider.generate(prompt, **kwargs)
                latency = time.time() - start_time
                self.manager.update_success(provider_name, latency)
                self.manager.record_quota_usage(provider_name)
                # Decrease remaining quota estimate
                self.manager.quota.decrement_quota(provider_name)
                self._update_weights()
                logger.info(f"Provider {provider_name} succeeded in {latency:.2f}s (task={task})")
                return response
            except Exception as e:
                latency = time.time() - start_time
                error_msg = str(e)
                logger.error(f"Provider {provider_name} failed: {error_msg} (latency {latency:.2f}s)")
                self.manager.update_failure(provider_name, error_msg)
                # Check if error requires cooldown (rate limit, quota exhaustion)
                if any(x in error_msg.lower() for x in ["429", "rate limit", "quota exceeded", "resource_exhausted"]):
                    self.manager.mark_cooldown(provider_name)
                    logger.warning(f"Provider {provider_name} entered cooldown (15min)")
                last_exception = e
                continue
        # If all providers failed
        raise ProviderUnavailableError(f"All LLM providers failed. Last error: {last_exception}")

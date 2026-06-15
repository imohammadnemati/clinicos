"""
Provider Router – Deterministic provider selection based on priority weight.
The router selects the best available provider (highest weight) and falls back to the next if it fails.
It never knows about models – only provider names.
All state (scores, cooldown) is obtained from ProviderManager.
"""

import logging
from typing import List, Tuple, Optional
from .provider_manager import ProviderManager
from .exceptions import ProviderUnavailableError

logger = logging.getLogger(__name__)


class ProviderRouter:
    def __init__(self, provider_manager: ProviderManager):
        self.manager = provider_manager

    def _get_sorted_providers(self) -> List[Tuple[str, float]]:
        """
        Return a list of (provider_name, priority_weight) sorted descending by weight.
        Skips providers that are in cooldown.
        Weight = (score * 0.7) + (quota_score * 0.3)
        """
        candidates = []
        for name in self.manager.get_all_provider_names():
            if self.manager.is_in_cooldown(name):
                logger.debug(f"Provider {name} is in cooldown – skipped")
                continue
            weight = self.manager.get_provider_priority_weight(name)
            candidates.append((name, weight))
        # Sort by weight descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates

    async def generate(self, prompt: str, task: str = "conversation", **kwargs) -> str:
        """
        Generate a response by trying providers in priority order until one succeeds.
        Args:
            prompt: The user prompt.
            task: Ignored in this simplified router (reserved for future specialization).
            **kwargs: Additional arguments passed to the provider's generate() method.
        Returns:
            The response text from the first successful provider.
        Raises:
            ProviderUnavailableError if all providers fail.
        """
        sorted_providers = self._get_sorted_providers()
        if not sorted_providers:
            raise ProviderUnavailableError("No providers available (all in cooldown or none registered)")

        last_exception = None
        for provider_name, weight in sorted_providers:
            provider = self.manager.get_provider(provider_name)
            if not provider:
                continue
            logger.info(f"Trying provider {provider_name} (weight={weight:.2f}) for task={task}")
            try:
                # Call the provider's generate method (passes through kwargs)
                response = await provider.generate(prompt, **kwargs)
                # Record success (increase score, reset failures, record cost)
                # Estimate tokens roughly (characters/4 is a rough approximation)
                estimated_tokens = len(prompt + response) // 4
                self.manager.record_success(provider_name, estimated_tokens)
                logger.info(f"Provider {provider_name} succeeded")
                return response
            except Exception as e:
                logger.error(f"Provider {provider_name} failed: {e}")
                self.manager.record_failure(provider_name)
                last_exception = e
                continue

        # All providers failed
        raise ProviderUnavailableError(f"All providers failed. Last error: {last_exception}")
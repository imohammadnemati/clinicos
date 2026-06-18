"""
Provider Manager – Registers provider instances, tracks their state via StateStore,
and provides a unified interface for the router to query provider scores, cooldown,
and to record success/failure outcomes.
All state (scores, failures, cooldown) is stored in Redis via StateStore.
"""

import logging
from typing import Dict, List, Optional

from .base_provider import BaseLLMProvider
from .state_store import StateStore
from .cost_manager import CostManager
from llm.config import INITIAL_SCORES

# Import all new providers
from llm.providers.groq_provider import GroqProvider
from llm.providers.mistral_provider import MistralProvider
from llm.providers.cohere_provider import CohereProvider
from llm.providers.deepseek_provider import DeepSeekProvider
from llm.providers.gemini_provider import GeminiProvider
from llm.providers.openai_provider import OpenAIProvider
from llm.providers.openrouter_provider import OpenRouterProvider

logger = logging.getLogger(__name__)


class ProviderManager:
    def __init__(self, providers: Dict[str, BaseLLMProvider],
                 state_store: StateStore,
                 cost_manager: CostManager):
        """
        Args:
            providers: Dictionary mapping provider name to provider instance.
            state_store: Redis-backed state store (single source of truth).
            cost_manager: Cost manager for quota scores.
        """
        self.providers = providers
        self.state_store = state_store
        self.cost_manager = cost_manager
        self._ensure_initial_scores()

    def _ensure_initial_scores(self):
        """Ensure that every provider has a score in Redis (set only if missing)."""
        for name in self.providers.keys():
            # get_score returns INITIAL_SCORES if not set, but we also need to write it
            # to Redis if it's completely missing so that future reads are consistent.
            current = self.state_store.get_score(name)
            if current == INITIAL_SCORES.get(name, 50):
                # Score already matches initial, assume it's stored
                continue
            # If Redis didn't have the key, get_score returns INITIAL_SCORES value,
            # but we still need to persist it to Redis.
            self.state_store.set_score(name, INITIAL_SCORES.get(name, 50))
            # Also ensure failure counter and cooldown are cleared (just in case)
            self.state_store.reset_failures(name)
            self.state_store.clear_cooldown(name)

    def get_all_provider_names(self) -> List[str]:
        """Return list of all registered provider names (order not important)."""
        return list(self.providers.keys())

    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        """Return provider instance by name."""
        return self.providers.get(name)

    def get_score(self, provider_name: str) -> int:
        """Get current score for provider (from Redis)."""
        return self.state_store.get_score(provider_name)

    def get_quota_score(self, provider_name: str) -> float:
        """Get quota score (0-100) from CostManager."""
        return self.cost_manager.get_remaining_budget_score(provider_name)

    def is_in_cooldown(self, provider_name: str) -> bool:
        """Check if provider is in cooldown."""
        return self.state_store.is_in_cooldown(provider_name)

    def record_success(self, provider_name: str, estimated_tokens: int = 0):
        """
        Record a successful request.
        Updates score (+1), resets failure counter, and records cost (if tokens provided).
        """
        self.state_store.record_success(provider_name)
        self.state_store.reset_failures(provider_name)
        # Estimate cost based on token count (optional)
        if estimated_tokens > 0:
            # Approximate cost: assume $0.001 per 1K tokens for estimation
            cost = (estimated_tokens / 1000.0) * 0.001
            self.cost_manager.record_usage(provider_name, cost)

    def record_failure(self, provider_name: str):
        """
        Record a failed request (network error, 5xx, 429, timeout, etc.).
        Decreases score by penalty, increments failure counter, and may trigger cooldown.
        """
        fail_count = self.state_store.record_failure(provider_name)
        # Check if cooldown threshold is reached
        from llm.config import CONSECUTIVE_FAILURES_THRESHOLD
        if fail_count >= CONSECUTIVE_FAILURES_THRESHOLD:
            self.state_store.start_cooldown(provider_name)
            logger.warning(f"Provider {provider_name} entered cooldown after {fail_count} consecutive failures")

    def get_provider_priority_weight(self, provider_name: str) -> float:
        """
        Compute priority weight = (score * 0.7) + (quota_score * 0.3)
        Used by the router to sort providers deterministically.
        """
        score = self.get_score(provider_name)
        quota = self.get_quota_score(provider_name)
        # Both score and quota are 0-200 and 0-100 respectively; normalise to 0-1 range?
        # Score is 0-200, we'll use raw value (max 200). Quota is 0-100.
        # Weight formula keeps original scaling (no extra normalisation) as per requirements.
        # However to keep values comparable, we use raw numbers.
        return (score * 0.7) + (quota * 0.3)

    def get_provider_status(self, provider_name: str) -> dict:
        """Return diagnostic status for a provider (used by admin commands)."""
        return {
            "name": provider_name,
            "score": self.get_score(provider_name),
            "quota_score": self.get_quota_score(provider_name),
            "in_cooldown": self.is_in_cooldown(provider_name),
            "failure_count": self.state_store.get_failure_count(provider_name),
        }
"""
Provider Manager – Only supports FreeLLMAPI.
All external providers are removed to avoid import errors.
"""

import logging
from typing import Dict, List, Optional

from .base_provider import BaseLLMProvider
from .state_store import StateStore
from .cost_manager import CostManager
from llm.config import INITIAL_SCORES

# No specific provider imports – providers are passed from patient_agent.py

logger = logging.getLogger(__name__)


class ProviderManager:
    def __init__(self, providers: Dict[str, BaseLLMProvider],
                 state_store: StateStore,
                 cost_manager: CostManager):
        self.providers = providers
        self.state_store = state_store
        self.cost_manager = cost_manager
        self._ensure_initial_scores()

    def _ensure_initial_scores(self):
        for name in self.providers.keys():
            current = self.state_store.get_score(name)
            if current == INITIAL_SCORES.get(name, 50):
                continue
            self.state_store.set_score(name, INITIAL_SCORES.get(name, 50))
            self.state_store.reset_failures(name)
            self.state_store.clear_cooldown(name)

    def get_all_provider_names(self) -> List[str]:
        return list(self.providers.keys())

    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        return self.providers.get(name)

    def get_score(self, provider_name: str) -> int:
        return self.state_store.get_score(provider_name)

    def get_quota_score(self, provider_name: str) -> float:
        return self.cost_manager.get_remaining_budget_score(provider_name)

    def is_in_cooldown(self, provider_name: str) -> bool:
        return self.state_store.is_in_cooldown(provider_name)

    def record_success(self, provider_name: str, estimated_tokens: int = 0):
        self.state_store.record_success(provider_name)
        self.state_store.reset_failures(provider_name)
        if estimated_tokens > 0:
            cost = (estimated_tokens / 1000.0) * 0.001
            self.cost_manager.record_usage(provider_name, cost)

    def record_failure(self, provider_name: str):
        fail_count = self.state_store.record_failure(provider_name)
        from llm.config import CONSECUTIVE_FAILURES_THRESHOLD
        if fail_count >= CONSECUTIVE_FAILURES_THRESHOLD:
            self.state_store.start_cooldown(provider_name)
            logger.warning(f"Provider {provider_name} entered cooldown after {fail_count} consecutive failures")

    def get_provider_priority_weight(self, provider_name: str) -> float:
        score = self.get_score(provider_name)
        quota = self.get_quota_score(provider_name)
        return (score * 0.7) + (quota * 0.3)

    def get_provider_status(self, provider_name: str) -> dict:
        return {
            "name": provider_name,
            "score": self.get_score(provider_name),
            "quota_score": self.get_quota_score(provider_name),
            "in_cooldown": self.is_in_cooldown(provider_name),
            "failure_count": self.state_store.get_failure_count(provider_name),
        }

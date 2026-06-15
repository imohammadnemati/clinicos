"""
Cost Manager – Tracks token spend per provider and returns a quota_score (0–100)
to influence routing decisions. For free providers (e.g., OpenRouter) always returns 100.
Spend data is persisted in Redis.
"""

import time
import redis
from llm.config import REDIS_URL, DAILY_BUDGET, MONTHLY_BUDGET, FREE_PROVIDERS
import logging

logger = logging.getLogger(__name__)


class CostManager:
    def __init__(self):
        self.redis = None
        if REDIS_URL:
            try:
                self.redis = redis.from_url(REDIS_URL, decode_responses=True)
                self.redis.ping()
                logger.info("CostManager connected to Redis")
            except Exception as e:
                logger.error(f"CostManager Redis connection failed: {e}. Spend tracking will be disabled.")
                self.redis = None
        else:
            logger.warning("REDIS_URL not set. Spend tracking disabled.")

    # ---------- Keys ----------
    def _daily_key(self, provider: str) -> str:
        return f"llm:spend:daily:{provider}"

    def _monthly_key(self, provider: str) -> str:
        return f"llm:spend:monthly:{provider}"

    # ---------- Record Usage ----------
    def record_usage(self, provider: str, estimated_cost: float):
        """
        Record estimated cost for a request (called by router after successful response).
        For free providers, this method does nothing (no tracking needed).
        """
        if provider in FREE_PROVIDERS:
            return
        if not self.redis:
            return

        now = time.time()
        # Daily bucket (reset every 24h)
        daily_key = self._daily_key(provider)
        self.redis.incrbyfloat(daily_key, estimated_cost)
        # Set expiry to 48h to be safe (cleanup)
        self.redis.expire(daily_key, 48 * 3600)

        # Monthly bucket (reset every ~30 days – we don't set expiry, rely on manual reset or ignore)
        monthly_key = self._monthly_key(provider)
        self.redis.incrbyfloat(monthly_key, estimated_cost)

    # ---------- Spend Retrieval ----------
    def get_daily_spend(self, provider: str) -> float:
        """Return current daily spend for provider (USD)."""
        if provider in FREE_PROVIDERS or not self.redis:
            return 0.0
        val = self.redis.get(self._daily_key(provider))
        return float(val) if val else 0.0

    def get_monthly_spend(self, provider: str) -> float:
        """Return current monthly spend for provider (USD)."""
        if provider in FREE_PROVIDERS or not self.redis:
            return 0.0
        val = self.redis.get(self._monthly_key(provider))
        return float(val) if val else 0.0

    # ---------- Quota Score (0–100) ----------
    def get_remaining_budget_score(self, provider: str) -> float:
        """
        Returns a score from 0 to 100 where higher means more budget left.
        For free providers → always 100.
        For paid providers → computed from daily and monthly spend caps.
        """
        if provider in FREE_PROVIDERS:
            return 100.0

        daily_spent = self.get_daily_spend(provider)
        monthly_spent = self.get_monthly_spend(provider)

        daily_ratio = min(1.0, daily_spent / DAILY_BUDGET) if DAILY_BUDGET > 0 else 1.0
        monthly_ratio = min(1.0, monthly_spent / MONTHLY_BUDGET) if MONTHLY_BUDGET > 0 else 1.0

        # Take the worse (higher ratio) of daily and monthly
        combined_ratio = max(daily_ratio, monthly_ratio)
        # Score = (1 - ratio) * 100, clamped to 0-100
        score = (1.0 - combined_ratio) * 100.0
        return max(0.0, min(100.0, score))

    # ---------- Admin / Debug ----------
    def reset_daily_spend(self, provider: str):
        """Manually reset daily spend (e.g., for testing)."""
        if self.redis:
            self.redis.delete(self._daily_key(provider))

    def reset_monthly_spend(self, provider: str):
        """Manually reset monthly spend."""
        if self.redis:
            self.redis.delete(self._monthly_key(provider))

    def get_spend_summary(self, provider: str) -> dict:
        """Return spend summary for a provider (for debugging)."""
        return {
            "daily_spend": self.get_daily_spend(provider),
            "monthly_spend": self.get_monthly_spend(provider),
            "daily_budget": DAILY_BUDGET,
            "monthly_budget": MONTHLY_BUDGET,
            "quota_score": self.get_remaining_budget_score(provider),
        }
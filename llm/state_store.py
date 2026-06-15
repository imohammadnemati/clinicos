"""
State Store – Single source of truth for provider scores, failure counts, and cooldown.
All data is stored in Redis with simple key‑value semantics.
No complex transactions – updates are atomic per provider using Redis's built‑in operations.
"""

import json
import time
from typing import Optional, Dict, Any
import redis
from llm.config import REDIS_URL, INITIAL_SCORES, SCORE_SUCCESS_INCREMENT, SCORE_FAILURE_PENALTY, MAX_SCORE, MIN_SCORE, CONSECUTIVE_FAILURES_THRESHOLD, COOLDOWN_SECONDS
import logging

logger = logging.getLogger(__name__)


class StateStore:
    def __init__(self):
        self.redis = None
        if REDIS_URL:
            try:
                self.redis = redis.from_url(REDIS_URL, decode_responses=True)
                # Test connection
                self.redis.ping()
                logger.info("StateStore connected to Redis")
            except Exception as e:
                logger.error(f"Redis connection failed: {e}. State will be lost on restart.")
                self.redis = None
        else:
            logger.warning("REDIS_URL not set. State will be lost on restart.")

    # ---------- Keys ----------
    def _score_key(self, provider: str) -> str:
        return f"llm:score:{provider}"

    def _fail_key(self, provider: str) -> str:
        return f"llm:fail:{provider}"

    def _cooldown_key(self, provider: str) -> str:
        return f"llm:cooldown:{provider}"

    # ---------- Score Management ----------
    def get_score(self, provider: str) -> int:
        """Get current score for provider, fallback to INITIAL_SCORES if not set."""
        if self.redis:
            val = self.redis.get(self._score_key(provider))
            if val is not None:
                return int(val)
        return INITIAL_SCORES.get(provider, 50)

    def set_score(self, provider: str, score: int):
        """Set score directly (used after recovery or manual override)."""
        if self.redis:
            self.redis.set(self._score_key(provider), score)
        # In‑memory fallback is not used – rely on Redis only.

    def record_success(self, provider: str):
        """Increase score by SCORE_SUCCESS_INCREMENT, cap at MAX_SCORE."""
        current = self.get_score(provider)
        new_score = min(MAX_SCORE, current + SCORE_SUCCESS_INCREMENT)
        if self.redis:
            self.redis.set(self._score_key(provider), new_score)
        # Reset failure count on success
        if self.redis:
            self.redis.delete(self._fail_key(provider))
        logger.debug(f"Provider {provider} score: {current} -> {new_score} (success)")

    def record_failure(self, provider: str) -> int:
        """
        Decrease score by SCORE_FAILURE_PENALTY (floor at MIN_SCORE).
        Increment consecutive failure counter.
        Returns the new failure count.
        """
        current = self.get_score(provider)
        new_score = max(MIN_SCORE, current - SCORE_FAILURE_PENALTY)
        if self.redis:
            self.redis.set(self._score_key(provider), new_score)
            # Increment failure counter
            fail_count = self.redis.incr(self._fail_key(provider))
            # Set expiry on failure counter (optional, but keep for a while)
            self.redis.expire(self._fail_key(provider), 3600)  # 1 hour
            logger.debug(f"Provider {provider} score: {current} -> {new_score} (failure), fail_count={fail_count}")
            return int(fail_count)
        return 1  # fallback

    def reset_failures(self, provider: str):
        """Reset failure count (called after success or manual reset)."""
        if self.redis:
            self.redis.delete(self._fail_key(provider))

    def get_failure_count(self, provider: str) -> int:
        """Return current consecutive failure count."""
        if self.redis:
            val = self.redis.get(self._fail_key(provider))
            if val is not None:
                return int(val)
        return 0

    # ---------- Cooldown Management ----------
    def is_in_cooldown(self, provider: str) -> bool:
        """Check if provider is currently in cooldown."""
        if self.redis:
            remaining = self.redis.ttl(self._cooldown_key(provider))
            if remaining > 0:
                return True
            if remaining == -1:  # key exists but no TTL? clean up
                self.redis.delete(self._cooldown_key(provider))
        return False

    def start_cooldown(self, provider: str):
        """Put provider into cooldown for COOLDOWN_SECONDS seconds."""
        if self.redis:
            self.redis.setex(self._cooldown_key(provider), COOLDOWN_SECONDS, "1")
            logger.warning(f"Provider {provider} entered cooldown for {COOLDOWN_SECONDS}s")

    def clear_cooldown(self, provider: str):
        """Manually remove cooldown (e.g., after admin intervention)."""
        if self.redis:
            self.redis.delete(self._cooldown_key(provider))

    # ---------- Full state retrieval (for admin/debug) ----------
    def get_provider_state(self, provider: str) -> Dict[str, Any]:
        """Return complete state for a provider (score, failures, cooldown)."""
        return {
            "score": self.get_score(provider),
            "failure_count": self.get_failure_count(provider),
            "in_cooldown": self.is_in_cooldown(provider),
        }

    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Return state for all known providers (based on INITIAL_SCORES keys)."""
        states = {}
        for provider in INITIAL_SCORES.keys():
            states[provider] = self.get_provider_state(provider)
        return states
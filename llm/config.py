"""
LLM Configuration – re‑exports settings from main config.
Exports all variables needed by llm modules (cost_manager, state_store, etc.).
"""

# ========== Re‑export from main config ==========
from config import (
    REDIS_URL,
    INITIAL_SCORES,
    SCORE_SUCCESS_INCREMENT,
    SCORE_FAILURE_PENALTY,
    MAX_SCORE,
    MIN_SCORE,
    CONSECUTIVE_FAILURES_THRESHOLD,
    COOLDOWN_SECONDS,
    DAILY_BUDGET,
    MONTHLY_BUDGET,
    FREE_PROVIDERS,
)

# ========== No external API keys are imported ==========
# All Local LLM settings are defined in the main config.

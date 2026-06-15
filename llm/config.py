"""
LLM Configuration – Exports settings from main config for use inside the llm package.
This avoids circular imports and keeps all configuration centralized in config.py.
"""

import sys
import os

# Add parent directory to path to import main config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    # API Keys
    DEEPSEEK_API_KEY,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    OPENROUTER_API_KEY,
    
    # OpenRouter free models
    OPENROUTER_FREE_MODELS,
    
    # Scoring & Cooldown
    INITIAL_SCORES,
    SCORE_SUCCESS_INCREMENT,
    SCORE_FAILURE_PENALTY,
    MAX_SCORE,
    MIN_SCORE,
    CONSECUTIVE_FAILURES_THRESHOLD,
    COOLDOWN_SECONDS,
    
    # Cost Manager
    DAILY_BUDGET,
    MONTHLY_BUDGET,
    FREE_PROVIDERS,
    
    # Redis
    REDIS_URL,
)

__all__ = [
    "DEEPSEEK_API_KEY",
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "OPENROUTER_API_KEY",
    "OPENROUTER_FREE_MODELS",
    "INITIAL_SCORES",
    "SCORE_SUCCESS_INCREMENT",
    "SCORE_FAILURE_PENALTY",
    "MAX_SCORE",
    "MIN_SCORE",
    "CONSECUTIVE_FAILURES_THRESHOLD",
    "COOLDOWN_SECONDS",
    "DAILY_BUDGET",
    "MONTHLY_BUDGET",
    "FREE_PROVIDERS",
    "REDIS_URL",

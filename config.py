"""
ClinicOS – Central Configuration
All environment variables are read here. No hardcoded secrets.
"""

import os
import json
from typing import List, Optional

# ========== Telegram ==========
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_TELEGRAM_ID = int(os.getenv("OWNER_TELEGRAM_ID", "0"))

# ========== Database ==========
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///clinic_brain.db")
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "10"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
DATABASE_POOL_TIMEOUT = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
DATABASE_POOL_RECYCLE = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# ========== Redis ==========
REDIS_URL = os.getenv("REDIS_URL", "")

# ========== LLM Providers – API Keys ==========
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# ========== OpenRouter Free‑Mode Only – Strict Allowlist ==========
# Must be a JSON array of strings, each ending with ":free"
# Example: '["deepseek/deepseek-chat-v3-0324:free","meta-llama/llama-3.3-70b-instruct:free"]'
OPENROUTER_FREE_MODELS_RAW = os.getenv("OPENROUTER_FREE_MODELS", "[]")
try:
    OPENROUTER_FREE_MODELS = json.loads(OPENROUTER_FREE_MODELS_RAW)
except json.JSONDecodeError:
    OPENROUTER_FREE_MODELS = []

# Validate at runtime (called in bot.py startup)
def validate_openrouter_config():
    if not OPENROUTER_FREE_MODELS:
        raise ValueError("OPENROUTER_FREE_MODELS is empty or invalid. Must be a non‑empty JSON array.")
    for model in OPENROUTER_FREE_MODELS:
        if not isinstance(model, str) or not model.endswith(":free"):
            raise ValueError(f"Model '{model}' does not end with ':free'. OpenRouter free mode only.")

# ========== LLM Base Scores (initial) ==========
# These are starting scores; actual scores are stored in Redis and evolve over time.
INITIAL_SCORES = {
    "deepseek": 100,
    "gemini": 90,
    "openai": 70,
    "openrouter": 50,      # intentionally low, used as fallback only
}

# ========== Scoring & Cooldown Rules ==========
SCORE_SUCCESS_INCREMENT = 1
SCORE_FAILURE_PENALTY = 20
MAX_SCORE = 200
MIN_SCORE = 0
CONSECUTIVE_FAILURES_THRESHOLD = 3
COOLDOWN_SECONDS = 15 * 60   # 15 minutes

# ========== Cost Manager (Quota Score) ==========
DAILY_BUDGET = float(os.getenv("DAILY_BUDGET", "5.0"))        # dollars per day
MONTHLY_BUDGET = float(os.getenv("MONTHLY_BUDGET", "50.0"))  # dollars per month
# Free providers always return quota_score = 100
FREE_PROVIDERS = ["openrouter"]

# ========== Lead & Session (existing) ==========
LEAD_THRESHOLD = float(os.getenv("LEAD_THRESHOLD", "7.0"))
SESSION_HOURS = int(os.getenv("SESSION_HOURS", "24"))
ACTIVE_SESSION_GRACE_MINUTES = int(os.getenv("ACTIVE_SESSION_GRACE_MINUTES", "90"))

# ========== Memory ==========
MAX_CONTEXT_MEMORIES = int(os.getenv("MAX_CONTEXT_MEMORIES", "3"))
MAX_CONTEXT_EVENTS = int(os.getenv("MAX_CONTEXT_EVENTS", "5"))
MAX_SUMMARY_CHARS = int(os.getenv("MAX_SUMMARY_CHARS", "500"))

# ========== Follow‑up ==========
DEFAULT_FOLLOWUP_DAYS = int(os.getenv("DEFAULT_FOLLOWUP_DAYS", "3"))
SECOND_FOLLOWUP_DAYS = int(os.getenv("SECOND_FOLLOWUP_DAYS", "7"))
THIRD_FOLLOWUP_DAYS = int(os.getenv("THIRD_FOLLOWUP_DAYS", "14"))
MAX_RECOVERY_ATTEMPTS = int(os.getenv("MAX_RECOVERY_ATTEMPTS", "3"))

# ========== Appointment ==========
DEFAULT_REMINDER_HOURS = int(os.getenv("DEFAULT_REMINDER_HOURS", "24"))

# ========== Working hours ==========
WORKING_HOURS_START = int(os.getenv("WORKING_HOURS_START", "8"))
WORKING_HOURS_END = int(os.getenv("WORKING_HOURS_END", "22"))
ACTIVE_TIMEOUT_MINUTES = int(os.getenv("ACTIVE_TIMEOUT_MINUTES", "30"))

# ========== Safety & Modes ==========
MEDICAL_SAFETY_MODE = os.getenv("MEDICAL_SAFETY_MODE", "True").lower() == "true"
READONLY_MODE = os.getenv("READONLY_MODE", "False").lower() == "true"

# ========== Logging ==========
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/clinic_brain.log")

# ========== Helper Functions ==========
def get_config_summary() -> dict:
    """Return a summary of key configuration (without secrets)."""
    return {
        "bot_token_configured": bool(BOT_TOKEN),
        "owner_telegram_id": OWNER_TELEGRAM_ID,
        "database_url": DATABASE_URL.split("://")[0],
        "redis_configured": bool(REDIS_URL),
        "deepseek_configured": bool(DEEPSEEK_API_KEY),
        "gemini_configured": bool(GEMINI_API_KEY),
        "openai_configured": bool(OPENAI_API_KEY),
        "openrouter_configured": bool(OPENROUTER_API_KEY),
        "openrouter_free_models_count": len(OPENROUTER_FREE_MODELS),
        "initial_scores": INITIAL_SCORES,
        "lead_threshold": LEAD_THRESHOLD,
        "session_hours": SESSION_HOURS,
        "max_recovery_attempts": MAX_RECOVERY_ATTEMPTS,
        "reminder_hours": DEFAULT_REMINDER_HOURS,
        "working_hours": f"{WORKING_HOURS_START}:00 - {WORKING_HOURS_END}:00",
        "medical_safety_mode": MEDICAL_SAFETY_MODE,
        "readonly_mode": READONLY_MODE,
        "debug_mode": DEBUG_MODE,
    }

if __name__ == "__main__":
    print("=" * 50)
    print("ClinicOS Configuration Summary")
    print("=" * 50)
    for k, v in get_config_summary().items():
        print(f"{k}: {v}")
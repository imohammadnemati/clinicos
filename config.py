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
# DeepSeek is removed – no longer used
DEEPSEEK_API_KEY = ""  # intentionally left empty
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# ========== Active Providers ==========
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
# COHERE_API_KEY removed

# ========== Provider Models – Centralized Configuration ==========
# Update this dictionary if a model is deprecated or you want to switch.
# Each provider's default model is read from here.
PROVIDER_MODELS = {
    "groq": "llama-3.1-8b-instant",              # or "mixtral-8x7b-32768"
    "openrouter": "meta-llama/llama-3.1-8b-instruct:free",
    "gemini": "gemini-1.5-pro",                  # or "gemini-1.5-flash"
    "mistral": "mistral-small-latest",
    "openai": "gpt-3.5-turbo",                   # or "gpt-4"
}

# ========== OpenRouter Free Mode – Models ==========
OPENROUTER_FREE_MODELS = os.getenv("OPENROUTER_FREE_MODELS", "").split(",") if os.getenv("OPENROUTER_FREE_MODELS") else []

# ========== LLM Base Scores (initial) ==========
INITIAL_SCORES = {
    "groq": 95,          # Free, super fast
    "openrouter": 90,    # Free, multiple models
    "gemini": 85,        # Free, good quality
    "mistral": 85,       # Free, 5000/month
    "openai": 40,        # Paid – last resort
    # "deepseek" removed
}

# ========== Scoring & Cooldown Rules ==========
SCORE_SUCCESS_INCREMENT = 1
SCORE_FAILURE_PENALTY = 20
MAX_SCORE = 200
MIN_SCORE = 0
CONSECUTIVE_FAILURES_THRESHOLD = 3
COOLDOWN_SECONDS = 15 * 60   # 15 minutes

# ========== Cost Manager (Quota Score) ==========
DAILY_BUDGET = float(os.getenv("DAILY_BUDGET", "5.0"))
MONTHLY_BUDGET = float(os.getenv("MONTHLY_BUDGET", "50.0"))
FREE_PROVIDERS = ["openrouter", "groq", "gemini", "mistral"]  # all except openai

# ========== Lead & Session ==========
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

# ========== Speech‑to‑Text (Local Whisper) ==========
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")

# ========== Gemini ==========
GEMINI_MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", "2048"))  # Ensure full responses

# ========== Helper Functions ==========
def validate_openrouter_config() -> None:
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not set. OpenRouter provider requires an API key.")

def get_config_summary() -> dict:
    return {
        "bot_token_configured": bool(BOT_TOKEN),
        "owner_telegram_id": OWNER_TELEGRAM_ID,
        "database_url": DATABASE_URL.split("://")[0],
        "redis_configured": bool(REDIS_URL),
        "deepseek_configured": bool(DEEPSEEK_API_KEY),  # always False now
        "openai_configured": bool(OPENAI_API_KEY),
        "gemini_configured": bool(GEMINI_API_KEY),
        "openrouter_configured": bool(OPENROUTER_API_KEY),
        "groq_configured": bool(GROQ_API_KEY),
        "mistral_configured": bool(MISTRAL_API_KEY),
        "cohere_configured": False,  # removed
        "openrouter_free_models_count": len(OPENROUTER_FREE_MODELS),
        "initial_scores": INITIAL_SCORES,
        "provider_models": PROVIDER_MODELS,
        "lead_threshold": LEAD_THRESHOLD,
        "session_hours": SESSION_HOURS,
        "max_recovery_attempts": MAX_RECOVERY_ATTEMPTS,
        "reminder_hours": DEFAULT_REMINDER_HOURS,
        "working_hours": f"{WORKING_HOURS_START}:00 - {WORKING_HOURS_END}:00",
        "medical_safety_mode": MEDICAL_SAFETY_MODE,
        "readonly_mode": READONLY_MODE,
        "debug_mode": DEBUG_MODE,
        "whisper_model_size": WHISPER_MODEL_SIZE,
        "gemini_max_tokens": GEMINI_MAX_TOKENS,
    }

if __name__ == "__main__":
    print("=" * 50)
    print("ClinicOS Configuration Summary")
    print("=" * 50)
    for k, v in get_config_summary().items():
        print(f"{k}: {v}")
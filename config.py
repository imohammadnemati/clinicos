"""
ClinicOS – Central Configuration
Only FreeLLMAPI is used as the LLM provider.
All external API keys are removed.
Supports Facial Analysis feature with configurable limits.
"""

import os

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

# ========== FreeLLMAPI (Local Proxy) ==========
FREELLMAPI_BASE_URL = os.getenv("FREELLMAPI_BASE_URL", "https://freellmapi-production-7f3d.up.railway.app")
FREELLMAPI_API_KEY = os.getenv("FREELLMAPI_API_KEY", "")
FREELLMAPI_DEFAULT_MODEL = os.getenv("FREELLMAPI_DEFAULT_MODEL", "auto")

# ========== LLM Base Scores – only FreeLLMAPI ==========
INITIAL_SCORES = {
    "freellmapi": 100,
}

# ========== Scoring & Cooldown Rules ==========
SCORE_SUCCESS_INCREMENT = 1
SCORE_FAILURE_PENALTY = 20
MAX_SCORE = 200
MIN_SCORE = 0
CONSECUTIVE_FAILURES_THRESHOLD = 3
COOLDOWN_SECONDS = 15 * 60

# ========== Cost Manager (unused now) ==========
DAILY_BUDGET = float(os.getenv("DAILY_BUDGET", "5.0"))
MONTHLY_BUDGET = float(os.getenv("MONTHLY_BUDGET", "50.0"))
FREE_PROVIDERS = ["freellmapi"]

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

# ========== Facial Analysis ==========
MAX_PATIENT_FACIAL_ANALYSES = int(os.getenv("MAX_PATIENT_FACIAL_ANALYSES", "1"))
FACIAL_ANALYSIS_TIMEOUT = int(os.getenv("FACIAL_ANALYSIS_TIMEOUT", "30"))  # seconds
PDF_REPORT_ENABLED = os.getenv("PDF_REPORT_ENABLED", "true").lower() == "true"
PDF_REPORT_FONT_PATH = os.getenv("PDF_REPORT_FONT_PATH", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

# ========== Helper Functions ==========
def get_config_summary() -> dict:
    return {
        "bot_token_configured": bool(BOT_TOKEN),
        "owner_telegram_id": OWNER_TELEGRAM_ID,
        "database_url": DATABASE_URL.split("://")[0],
        "redis_configured": bool(REDIS_URL),
        "freellmapi_configured": bool(FREELLMAPI_API_KEY),
        "freellmapi_url": FREELLMAPI_BASE_URL,
        "initial_scores": INITIAL_SCORES,
        "lead_threshold": LEAD_THRESHOLD,
        "session_hours": SESSION_HOURS,
        "max_recovery_attempts": MAX_RECOVERY_ATTEMPTS,
        "reminder_hours": DEFAULT_REMINDER_HOURS,
        "working_hours": f"{WORKING_HOURS_START}:00 - {WORKING_HOURS_END}:00",
        "medical_safety_mode": MEDICAL_SAFETY_MODE,
        "readonly_mode": READONLY_MODE,
        "debug_mode": DEBUG_MODE,
        "max_patient_facial_analyses": MAX_PATIENT_FACIAL_ANALYSES,
        "facial_analysis_timeout": FACIAL_ANALYSIS_TIMEOUT,
        "pdf_report_enabled": PDF_REPORT_ENABLED,
        "pdf_report_font": PDF_REPORT_FONT_PATH,
    }

if __name__ == "__main__":
    print("=" * 50)
    print("ClinicOS Configuration (FreeLLMAPI + Facial Analysis)")
    print("=" * 50)
    for k, v in get_config_summary().items():
        print(f"{k}: {v}")

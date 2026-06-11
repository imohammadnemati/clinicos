import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_TELEGRAM_ID = int(os.getenv("OWNER_TELEGRAM_ID", "0"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///clinic_brain.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

LEAD_THRESHOLD = float(os.getenv("LEAD_THRESHOLD", "7.0"))
SESSION_HOURS = int(os.getenv("SESSION_HOURS", "24"))
ACTIVE_SESSION_GRACE_MINUTES = int(os.getenv("ACTIVE_SESSION_GRACE_MINUTES", "90"))
MAX_CONTEXT_MEMORIES = int(os.getenv("MAX_CONTEXT_MEMORIES", "3"))
MAX_CONTEXT_EVENTS = int(os.getenv("MAX_CONTEXT_EVENTS", "5"))
MAX_SUMMARY_CHARS = int(os.getenv("MAX_SUMMARY_CHARS", "500"))

DEFAULT_FOLLOWUP_DAYS = int(os.getenv("DEFAULT_FOLLOWUP_DAYS", "3"))
SECOND_FOLLOWUP_DAYS = int(os.getenv("SECOND_FOLLOWUP_DAYS", "7"))
THIRD_FOLLOWUP_DAYS = int(os.getenv("THIRD_FOLLOWUP_DAYS", "14"))
MAX_RECOVERY_ATTEMPTS = int(os.getenv("MAX_RECOVERY_ATTEMPTS", "3"))

DEFAULT_REMINDER_HOURS = int(os.getenv("DEFAULT_REMINDER_HOURS", "24"))
"""
فایل تنظیمات پروژه (Configuration File)
شامل تمام متغیرهای محیطی، تنظیمات دیتابیس، API و رفتار سیستم
"""

import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()


# ========== تنظیمات بات تلگرام ==========
# توکن بات (از @BotFather دریافت کنید)
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# شناسه تلگرام مالک کلینیک (عدد صحیح)
OWNER_TELEGRAM_ID = int(os.getenv("OWNER_TELEGRAM_ID", "0"))


# ========== تنظیمات دیتابیس ==========
# آدرس دیتابیس (SQLite برای توسعه، PostgreSQL برای تولید)
# مثال SQLite: sqlite:///clinic_brain.db
# مثال PostgreSQL: postgresql://user:pass@localhost/clinic_brain
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///clinic_brain.db")

# تنظیمات Connection Pool (فقط برای PostgreSQL استفاده می‌شود)
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "10"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
DATABASE_POOL_TIMEOUT = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
DATABASE_POOL_RECYCLE = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))

# حالت دیباگ (لاگ کردن کوئری‌های SQL)
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"


# ========== تنظیمات API هوش مصنوعی ==========
# کلید API گوگل جمینای (از Google AI Studio دریافت کنید)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# مدل Whisper برای تبدیل صدا به متن (در نسخه ساده غیرفعال است)
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")


# ========== تنظیمات لید و پیپلاین فروش ==========
# حداقل امتیاز برای تبدیل رویداد به لید (از 0 تا 10)
LEAD_THRESHOLD = float(os.getenv("LEAD_THRESHOLD", "7.0"))

# حداکثر زمان فعال بودن یک جلسه (ساعت)
SESSION_HOURS = int(os.getenv("SESSION_HOURS", "24"))

# مدت زمان فعال بودن مکالمه در خارج از ساعات کاری (دقیقه)
ACTIVE_SESSION_GRACE_MINUTES = int(os.getenv("ACTIVE_SESSION_GRACE_MINUTES", "90"))


# ========== تنظیمات حافظه و کانتکست ==========
# حداکثر تعداد حافظه‌های ارسالی در پرامپت
MAX_CONTEXT_MEMORIES = int(os.getenv("MAX_CONTEXT_MEMORIES", "3"))

# حداکثر تعداد رویدادهای ارسالی در پرامپت
MAX_CONTEXT_EVENTS = int(os.getenv("MAX_CONTEXT_EVENTS", "5"))

# حداکثر طول متن خلاصه بیمار (کاراکتر)
MAX_SUMMARY_CHARS = int(os.getenv("MAX_SUMMARY_CHARS", "500"))


# ========== تنظیمات بازیابی لیدهای از دست رفته ==========
# فاصله زمانی اولین پیگیری (روز)
DEFAULT_FOLLOWUP_DAYS = int(os.getenv("DEFAULT_FOLLOWUP_DAYS", "3"))

# فاصله زمانی دومین پیگیری (روز)
SECOND_FOLLOWUP_DAYS = int(os.getenv("SECOND_FOLLOWUP_DAYS", "7"))

# فاصله زمانی سومین پیگیری (روز)
THIRD_FOLLOWUP_DAYS = int(os.getenv("THIRD_FOLLOWUP_DAYS", "14"))

# حداکثر تعداد تلاش برای بازیابی لید
MAX_RECOVERY_ATTEMPTS = int(os.getenv("MAX_RECOVERY_ATTEMPTS", "3"))


# ========== تنظیمات نوبت‌دهی ==========
# تعداد ساعت قبل از نوبت برای ارسال یادآوری
DEFAULT_REMINDER_HOURS = int(os.getenv("DEFAULT_REMINDER_HOURS", "24"))


# ========== تنظیمات ساعات کاری کلینیک ==========
# ساعت شروع کار (پیش‌فرض: 8 صبح)
WORKING_HOURS_START = int(os.getenv("WORKING_HOURS_START", "8"))

# ساعت پایان کار (پیش‌فرض: 10 شب)
WORKING_HOURS_END = int(os.getenv("WORKING_HOURS_END", "22"))

# مدت زمان فعال بودن مکالمه بعد از ساعات کاری (دقیقه)
ACTIVE_TIMEOUT_MINUTES = int(os.getenv("ACTIVE_TIMEOUT_MINUTES", "30"))


# ========== تنظیمات هزینه و محدودیت ==========
# حداکثر تعداد درخواست به Gemini در روز (برای کنترل هزینه)
MAX_DAILY_GEMINI_CALLS = int(os.getenv("MAX_DAILY_GEMINI_CALLS", "1000"))

# هشدار هزینه (دلار) – در صورت تجاوز، اعلان ارسال می‌شود
COST_ALERT_THRESHOLD = float(os.getenv("COST_ALERT_THRESHOLD", "5.0"))


# ========== تنظیمات امنیتی ==========
# فعال‌سازی حالت ایمنی پزشکی (غیرفعال کردن پاسخ‌های پزشکی)
MEDICAL_SAFETY_MODE = os.getenv("MEDICAL_SAFETY_MODE", "True").lower() == "true"

# فعال‌سازی حالت فقط خواندنی (فقط ذخیره پیام، بدون پاسخ)
READONLY_MODE = os.getenv("READONLY_MODE", "False").lower() == "true"


# ========== تنظیمات پیشرفته ==========
# سطح لاگ (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# مسیر ذخیره فایل‌های لاگ
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/clinic_brain.log")


# ========== اعتبارسنجی تنظیمات اولیه ==========
def validate_config():
    """بررسی تنظیمات ضروری قبل از راه‌اندازی"""
    errors = []
    if not BOT_TOKEN:
        errors.append("BOT_TOKEN تنظیم نشده است")
    if OWNER_TELEGRAM_ID == 0:
        errors.append("OWNER_TELEGRAM_ID تنظیم نشده است")
    if not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY تنظیم نشده است")
    if errors:
        print("❌ خطای اعتبارسنجی تنظیمات:")
        for err in errors:
            print(f"   - {err}")
        return False
    return True


def get_config_summary() -> dict:
    """خلاصه تنظیمات (بدون مقادیر حساس) برای نمایش"""
    return {
        "bot_token_configured": bool(BOT_TOKEN),
        "owner_telegram_id": OWNER_TELEGRAM_ID,
        "database_url": DATABASE_URL.split("://")[0] if DATABASE_URL else "none",
        "gemini_configured": bool(GEMINI_API_KEY),
        "lead_threshold": LEAD_THRESHOLD,
        "session_hours": SESSION_HOURS,
        "max_recovery_attempts": MAX_RECOVERY_ATTEMPTS,
        "reminder_hours": DEFAULT_REMINDER_HOURS,
        "working_hours": f"{WORKING_HOURS_START}:00 - {WORKING_HOURS_END}:00",
        "medical_safety_mode": MEDICAL_SAFETY_MODE,
        "readonly_mode": READONLY_MODE,
        "debug_mode": DEBUG_MODE
    }


# اگر فایل به صورت مستقیم اجرا شد
if __name__ == "__main__":
    print("=" * 50)
    print("تنظیمات پروژه ClinicOS")
    print("=" * 50)
    if validate_config():
        for key, value in get_config_summary().items():
            print(f"{key}: {value}")
    else:
        print("لطفاً فایل .env را با مقادیر صحیح پر کنید.")
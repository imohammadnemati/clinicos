"""
فایل تنظیمات پروژه (Configuration File)
این فایل شامل تمام تنظیمات و متغیرهای محیطی پروژه است.
"""

import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()


# ========== تنظیمات بات تلگرام ==========
# توکن بات تلگرام (از @BotFather دریافت کنید)
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# شناسه تلگرام مالک کلینیک (عدد صحیح)
OWNER_TELEGRAM_ID = int(os.getenv("OWNER_TELEGRAM_ID", "0"))


# ========== تنظیمات دیتابیس ==========
# آدرس دیتابیس (SQLite برای توسعه، PostgreSQL برای تولید)
# مثال SQLite: sqlite:///clinic_brain.db
# مثال PostgreSQL: postgresql://user:pass@localhost/clinic_brain
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///clinic_brain.db")


# ========== تنظیمات API هوش مصنوعی ==========
# کلید API گوگل جمینای (از Google AI Studio دریافت کنید)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# کلید API گروک (اختیاری - برای سرویس جایگزین)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# مدل Whisper برای تبدیل صدا به متن (اختیاری - در نسخه ساده غیرفعال است)
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")


# ========== تنظیمات لید و پیپلاین فروش ==========
# حداقل امتیاز برای تبدیل رویداد به لید (از 0 تا 10)
LEAD_THRESHOLD = float(os.getenv("LEAD_THRESHOLD", "7.0"))

# حداکثر زمان فعال بودن یک جلسه (ساعت)
SESSION_HOURS = int(os.getenv("SESSION_HOURS", "24"))

# مدت زمان فعال بودن مکالمه در خارج از ساعات کاری (دقیقه)
ACTIVE_SESSION_GRACE_MINUTES = int(os.getenv("ACTIVE_SESSION_GRACE_MINUTES", "90"))


# ========== تنظیمات حافظه و کانتکست ==========
# حداکثر تعداد حافظه‌هایی که در پرامپت ارسال می‌شوند
MAX_CONTEXT_MEMORIES = int(os.getenv("MAX_CONTEXT_MEMORIES", "3"))

# حداکثر تعداد رویدادهایی که در پرامپت ارسال می‌شوند
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

# حداکثر تعداد درخواست تغییر زمان نوبت
MAX_RESCHEDULE_ATTEMPTS = int(os.getenv("MAX_RESCHEDULE_ATTEMPTS", "3"))


# ========== تنظیمات ساعات کاری ==========
# ساعت شروع کار (پیش‌فرض: 8 صبح)
WORKING_HOURS_START = int(os.getenv("WORKING_HOURS_START", "8"))

# ساعت پایان کار (پیش‌فرض: 10 شب)
WORKING_HOURS_END = int(os.getenv("WORKING_HOURS_END", "22"))

# مدت زمان فعال بودن مکالمه بعد از ساعات کاری (دقیقه)
ACTIVE_TIMEOUT_MINUTES = int(os.getenv("ACTIVE_TIMEOUT_MINUTES", "30"))


# ========== تنظیمات هزینه و محدودیت ==========
# حداکثر تعداد درخواست به Gemini در روز (برای کنترل هزینه)
MAX_DAILY_GEMINI_CALLS = int(os.getenv("MAX_DAILY_GEMINI_CALLS", "1000"))

# هشدار هزینه (دلار) - در صورت تجاوز، اعلان ارسال می‌شود
COST_ALERT_THRESHOLD = float(os.getenv("COST_ALERT_THRESHOLD", "5.0"))


# ========== تنظیمات امنیتی ==========
# فعال‌سازی حالت ایمنی پزشکی (غیرفعال کردن پاسخ‌های پزشکی)
MEDICAL_SAFETY_MODE = os.getenv("MEDICAL_SAFETY_MODE", "True").lower() == "true"

# فعال‌سازی حالت فقط خواندنی (فقط ذخیره پیام، بدون پاسخ)
READONLY_MODE = os.getenv("READONLY_MODE", "False").lower() == "true"


# ========== تنظیمات پیشرفته ==========
# سطح لاگ (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# فعال‌سازی حالت دیباگ
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# مسیر ذخیره فایل‌های لاگ
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/clinic_brain.log")


# ========== اعتبارسنجی تنظیمات اولیه ==========
def validate_config():
    """
    اعتبارسنجی تنظیمات قبل از راه‌اندازی
    اگر تنظیمات ضروری وجود نداشته باشد، خطا می‌دهد
    """
    errors = []
    
    if not BOT_TOKEN:
        errors.append("BOT_TOKEN تنظیم نشده است. لطفاً در فایل .env قرار دهید.")
    
    if OWNER_TELEGRAM_ID == 0:
        errors.append("OWNER_TELEGRAM_ID تنظیم نشده است. لطفاً در فایل .env قرار دهید.")
    
    if not GEMINI_API_KEY and not GROQ_API_KEY:
        errors.append("هیچ کلید API (GEMINI_API_KEY یا GROQ_API_KEY) تنظیم نشده است.")
    
    if errors:
        error_msg = "\n".join(errors)
        print(f"❌ خطای اعتبارسنجی تنظیمات:\n{error_msg}")
        return False
    
    print("✅ تنظیمات با موفقیت اعتبارسنجی شد.")
    return True


# ========== توابع کمکی ==========
def get_config_summary() -> dict:
    """
    دریافت خلاصه تنظیمات (بدون مقادیر حساس)
    برای نمایش در داشبورد
    """
    return {
        "bot_token_configured": bool(BOT_TOKEN),
        "owner_telegram_id": OWNER_TELEGRAM_ID,
        "database_url": DATABASE_URL.split("://")[0] if DATABASE_URL else "none",
        "gemini_configured": bool(GEMINI_API_KEY),
        "groq_configured": bool(GROQ_API_KEY),
        "lead_threshold": LEAD_THRESHOLD,
        "session_hours": SESSION_HOURS,
        "max_recovery_attempts": MAX_RECOVERY_ATTEMPTS,
        "reminder_hours": DEFAULT_REMINDER_HOURS,
        "working_hours": f"{WORKING_HOURS_START}:00 - {WORKING_HOURS_END}:00",
        "medical_safety_mode": MEDICAL_SAFETY_MODE,
        "readonly_mode": READONLY_MODE,
        "debug_mode": DEBUG_MODE
    }


def update_config_from_dict(config_dict: dict):
    """
    به‌روزرسانی تنظیمات از دیکشنری (برای استفاده در زمان اجرا)
    توجه: تغییرات در فایل .env ذخیره نمی‌شود
    """
    global LEAD_THRESHOLD, SESSION_HOURS, MAX_RECOVERY_ATTEMPTS
    
    if "lead_threshold" in config_dict:
        LEAD_THRESHOLD = float(config_dict["lead_threshold"])
    if "session_hours" in config_dict:
        SESSION_HOURS = int(config_dict["session_hours"])
    if "max_recovery_attempts" in config_dict:
        MAX_RECOVERY_ATTEMPTS = int(config_dict["max_recovery_attempts"])


# اگر فایل به صورت مستقیم اجرا شد، تنظیمات را نمایش بده
if __name__ == "__main__":
    print("=" * 50)
    print("تنظیمات پروژه ClinicOS")
    print("=" * 50)
    if validate_config():
        summary = get_config_summary()
        for key, value in summary.items():
            print(f"{key}: {value}")
    else:
        print("لطفاً فایل .env را با مقادیر صحیح پر کنید.")
        print("مثال فایل .env:")
        print("""
BOT_TOKEN=1234567890:ABCdefGHIjklm...
OWNER_TELEGRAM_ID=123456789
DATABASE_URL=sqlite:///clinic_brain.db
GEMINI_API_KEY=AIzaSy...
GROQ_API_KEY=gsk_...
WHISPER_MODEL=base
LEAD_THRESHOLD=7.0
SESSION_HOURS=24
ACTIVE_SESSION_GRACE_MINUTES=90
MAX_CONTEXT_MEMORIES=3
MAX_CONTEXT_EVENTS=5
MAX_SUMMARY_CHARS=500
DEFAULT_FOLLOWUP_DAYS=3
SECOND_FOLLOWUP_DAYS=7
THIRD_FOLLOWUP_DAYS=14
MAX_RECOVERY_ATTEMPTS=3
DEFAULT_REMINDER_HOURS=24
MAX_RESCHEDULE_ATTEMPTS=3
WORKING_HOURS_START=8
WORKING_HOURS_END=22
ACTIVE_TIMEOUT_MINUTES=30
MAX_DAILY_GEMINI_CALLS=1000
COST_ALERT_THRESHOLD=5.0
MEDICAL_SAFETY_MODE=True
READONLY_MODE=False
LOG_LEVEL=INFO
DEBUG_MODE=False
        """)
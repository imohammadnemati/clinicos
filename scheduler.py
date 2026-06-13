from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import asyncio
import logging
from lost_lead_recovery import recover_lost_leads
from appointment_engine import send_reminders, check_no_shows
from kpi_engine import calculate_daily_kpi
from database import SessionLocal
from models import Clinic

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def nightly_jobs():
    logger.info("🌙 شروع وظایف شبانه...")
    try:
        await recover_lost_leads()
        logger.info("✅ بازیابی لیدها انجام شد.")
    except Exception as e:
        logger.error(f"❌ خطا در بازیابی لیدها: {e}")
    try:
        await send_reminders()
        logger.info("✅ یادآوری نوبت‌ها ارسال شد.")
    except Exception as e:
        logger.error(f"❌ خطا در ارسال یادآوری: {e}")
    try:
        await check_no_shows()
        logger.info("✅ تشخیص عدم حضور انجام شد.")
    except Exception as e:
        logger.error(f"❌ خطا در تشخیص عدم حضور: {e}")
    try:
        db = SessionLocal()
        clinics = db.query(Clinic).all()
        db.close()
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        for clinic in clinics:
            calculate_daily_kpi(clinic.id, yesterday)
        logger.info("✅ آمار روزانه محاسبه شد.")
    except Exception as e:
        logger.error(f"❌ خطا در محاسبه آمار: {e}")
    logger.info("✅ وظایف شبانه پایان یافت.")

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(nightly_jobs, CronTrigger(hour=2, minute=0), id="nightly_jobs")
        scheduler.start()
        logger.info("⏰ زمان‌بند راه‌اندازی شد.")
    else:
        logger.warning("زمان‌بند قبلاً در حال اجراست.")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("⏰ زمان‌بند متوقف شد.")

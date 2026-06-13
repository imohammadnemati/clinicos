from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging
from lost_lead_recovery import recover_lost_leads
from appointment_engine import send_reminders, check_no_shows
from kpi_engine import calculate_daily_kpi
from database import SessionLocal
from models import Clinic

logger = logging.getLogger(__name__)

_scheduler = None

def get_scheduler():
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler

async def nightly_jobs():
    logger.info("🌙 Starting nightly jobs...")
    try:
        await recover_lost_leads()
        logger.info("✅ Lost leads recovery done.")
    except Exception as e:
        logger.error(f"❌ Lost leads error: {e}")
    try:
        await send_reminders()
        logger.info("✅ Reminders sent.")
    except Exception as e:
        logger.error(f"❌ Reminders error: {e}")
    try:
        await check_no_shows()
        logger.info("✅ No-shows checked.")
    except Exception as e:
        logger.error(f"❌ No-shows error: {e}")
    try:
        db = SessionLocal()
        clinics = db.query(Clinic).all()
        db.close()
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        for clinic in clinics:
            calculate_daily_kpi(clinic.id, yesterday)
        logger.info("✅ Daily KPIs calculated.")
    except Exception as e:
        logger.error(f"❌ KPIs error: {e}")
    logger.info("✅ Nightly jobs finished.")

def init_scheduler():
    """Add the nightly job to the scheduler (does not start it)."""
    sched = get_scheduler()
    if not sched.get_job("nightly_jobs"):
        sched.add_job(nightly_jobs, CronTrigger(hour=2, minute=0), id="nightly_jobs")
        logger.info("Nightly job added to scheduler.")
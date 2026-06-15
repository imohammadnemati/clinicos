"""
Scheduler – Background tasks for ClinicOS.
Runs nightly jobs: lost lead recovery, appointment reminders, no‑show detection, KPI calculation.
No LLM dependencies – all tasks call existing business logic modules.
"""

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


def get_scheduler() -> AsyncIOScheduler:
    """Return the singleton scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


async def nightly_jobs():
    """Run all nightly maintenance tasks."""
    logger.info("🌙 Starting nightly jobs...")

    # 1. Recover lost leads
    try:
        await recover_lost_leads()
        logger.info("✅ Lost lead recovery completed.")
    except Exception as e:
        logger.error(f"❌ Lost lead recovery failed: {e}")

    # 2. Send appointment reminders
    try:
        await send_reminders()
        logger.info("✅ Appointment reminders sent.")
    except Exception as e:
        logger.error(f"❌ Appointment reminders failed: {e}")

    # 3. Check for no‑shows
    try:
        await check_no_shows()
        logger.info("✅ No‑show check completed.")
    except Exception as e:
        logger.error(f"❌ No‑show check failed: {e}")

    # 4. Calculate daily KPIs for all clinics
    try:
        db = SessionLocal()
        clinics = db.query(Clinic).all()
        db.close()
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        for clinic in clinics:
            calculate_daily_kpi(clinic.id, yesterday)
        logger.info("✅ Daily KPIs calculated.")
    except Exception as e:
        logger.error(f"❌ KPI calculation failed: {e}")

    logger.info("✅ Nightly jobs finished.")


def init_scheduler():
    """Initialize the scheduler by adding the nightly job (does not start it)."""
    sched = get_scheduler()
    if not sched.get_job("nightly_jobs"):
        sched.add_job(nightly_jobs, CronTrigger(hour=2, minute=0), id="nightly_jobs")
        logger.info("Nightly job added to scheduler.")


def start_scheduler():
    """Start the scheduler (called after the event loop is running)."""
    sched = get_scheduler()
    if not sched.running:
        # Ensure job exists (idempotent)
        if not sched.get_job("nightly_jobs"):
            sched.add_job(nightly_jobs, CronTrigger(hour=2, minute=0), id="nightly_jobs")
        sched.start()
        logger.info("⏰ Scheduler started.")


def stop_scheduler():
    """Stop the scheduler (clean shutdown)."""
    sched = get_scheduler()
    if sched.running:
        sched.shutdown(wait=False)
        logger.info("⏰ Scheduler stopped.")
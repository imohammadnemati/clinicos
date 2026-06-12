"""
ماژول زمان‌بندی (Scheduler)
مسئول اجرای وظایف دوره‌ای: بازیابی لیدها، یادآوری نوبت‌ها، پاکسازی حافظه و محاسبه KPI.
"""

from apscheduler.schedulers.async_ import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import asyncio
import logging

from lost_lead_recovery import recover_lost_leads
from appointment_engine import send_reminders, check_no_shows
from kpi_engine import calculate_daily_kpi
from database import SessionLocal
from models import (
    Clinic,
    Patient,
    PatientMemory,
    PatientProfile,
    Session,
    Event,
    RawMessage,
    ConversationState,
    Lead
)

logger = logging.getLogger(__name__)

# ایجاد شیء زمان‌بند (یک نمونه سراسری)
_scheduler = None


def get_scheduler():
    """دریافت نمونه زمان‌بند (Singleton)"""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


# ========== وظیفه: یکپارچه‌سازی حافظه بیماران (در نسخه ساده فقط لاگ) ==========
async def consolidate_all_patients_memories():
    """جای خالی برای نسخه کامل (در حال حاضر فقط لاگ)"""
    logger.info("🔄 یکپارچه‌سازی حافظه بیماران (در نسخه ساده غیرفعال است)")


# ========== وظیفه: پاکسازی حافظه بیماران بی‌کیفیت ==========
async def cleanup_memory():
    """
    پاکسازی حافظه بیماران Spam, Cold, Dead با ترتیب امن (حذف وابسته‌ها قبل از والد)
    """
    logger.info("🧹 شروع پاکسازی حافظه بیماران...")
    db = SessionLocal()
    now = datetime.utcnow()

    try:
        # ===== 1. Spam: 7 روز =====
        spam_cutoff = now - timedelta(days=7)
        spams = db.query(Patient).filter(
            Patient.status == 'spam',
            Patient.last_seen < spam_cutoff,
            Patient.memory_purged == False
        ).yield_per(100)

        for patient in spams:
            try:
                # حذف رکوردهای وابسته به ترتیب امن
                db.query(ConversationState).filter(
                    ConversationState.session_id.in_(
                        db.query(Session.id).filter_by(patient_id=patient.id)
                    )
                ).delete(synchronize_session=False)
                db.query(PatientMemory).filter_by(patient_id=patient.id).delete()
                db.query(RawMessage).filter_by(patient_id=patient.id).delete()
                db.query(Event).filter_by(patient_id=patient.id).delete()
                db.query(Session).filter_by(patient_id=patient.id).delete()
                db.query(PatientProfile).filter_by(patient_id=patient.id).delete()

                patient.memory_purged = True
                patient.status = 'archived'
                logger.info(f"حافظه بیمار spam {patient.id} پاکسازی شد.")
            except Exception as e:
                logger.error(f"خطا در پاکسازی spam {patient.id}: {e}")

        # ===== 2. Cold: 60 روز =====
        cold_cutoff = now - timedelta(days=60)
        colds = db.query(Patient).filter(
            Patient.status == 'cold',
            Patient.last_seen < cold_cutoff,
            Patient.memory_purged == False
        ).yield_per(100)

        for patient in colds:
            try:
                summary = build_patient_summary(patient.id, db)
                patient.summary_data = summary

                db.query(ConversationState).filter(
                    ConversationState.session_id.in_(
                        db.query(Session.id).filter_by(patient_id=patient.id)
                    )
                ).delete(synchronize_session=False)
                db.query(PatientMemory).filter_by(patient_id=patient.id).delete()
                db.query(RawMessage).filter_by(patient_id=patient.id).delete()
                db.query(Event).filter_by(patient_id=patient.id).delete()
                db.query(Session).filter_by(patient_id=patient.id).delete()
                db.query(PatientProfile).filter_by(patient_id=patient.id).delete()

                patient.memory_purged = True
                patient.status = 'archived_cold'
                logger.info(f"حافظه بیمار cold {patient.id} پاکسازی شد.")
            except Exception as e:
                logger.error(f"خطا در پاکسازی cold {patient.id}: {e}")

        # ===== 3. Dead: 120 روز =====
        dead_cutoff = now - timedelta(days=120)
        deads = db.query(Patient).filter(
            Patient.status == 'dead',
            Patient.last_seen < dead_cutoff,
            Patient.memory_purged == False
        ).yield_per(100)

        for patient in deads:
            try:
                summary = build_patient_summary(patient.id, db)
                patient.summary_data = summary

                db.query(ConversationState).filter(
                    ConversationState.session_id.in_(
                        db.query(Session.id).filter_by(patient_id=patient.id)
                    )
                ).delete(synchronize_session=False)
                db.query(PatientMemory).filter_by(patient_id=patient.id).delete()
                db.query(RawMessage).filter_by(patient_id=patient.id).delete()
                db.query(Event).filter_by(patient_id=patient.id).delete()
                db.query(Session).filter_by(patient_id=patient.id).delete()
                db.query(PatientProfile).filter_by(patient_id=patient.id).delete()

                patient.memory_purged = True
                patient.status = 'archived_dead'
                logger.info(f"حافظه بیمار dead {patient.id} پاکسازی شد.")
            except Exception as e:
                logger.error(f"خطا در پاکسازی dead {patient.id}: {e}")

        db.commit()
        logger.info("✅ پاکسازی حافظه بیماران انجام شد.")
    except Exception as e:
        logger.error(f"خطا در پاکسازی حافظه: {e}")
        db.rollback()
    finally:
        db.close()


def build_patient_summary(patient_id: int, db) -> dict:
    """ساخت خلاصه از اطلاعات بیمار قبل از پاکسازی"""
    try:
        events = db.query(Event).filter_by(patient_id=patient_id).order_by(
            Event.created_at.desc()
        ).limit(10).all()
        leads = db.query(Lead).filter_by(patient_id=patient_id).all()

        max_lead_score = max([l.lead_score for l in leads]) if leads else 0
        service_interests = list(set([e.service for e in events if e.service and e.service != 'none']))
        last_intent = events[0].intent_type if events else None

        return {
            "message_count": len(events),
            "lead_score_max": max_lead_score,
            "service_interest": service_interests[0] if service_interests else None,
            "last_intent": last_intent,
            "last_seen": events[0].created_at.isoformat() if events else None
        }
    except Exception as e:
        logger.error(f"خطا در خلاصه‌سازی بیمار {patient_id}: {e}")
        return {}


# ========== وظایف آمار و محاسبات ==========
async def update_daily_metrics():
    logger.info("📊 شروع محاسبه آمار روزانه...")
    db = SessionLocal()
    try:
        clinics = db.query(Clinic).all()
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        for clinic in clinics:
            try:
                calculate_daily_kpi(clinic.id, yesterday)
            except Exception as e:
                logger.error(f"خطا در KPI کلینیک {clinic.id}: {e}")
        logger.info(f"✅ آمار روزانه برای {len(clinics)} کلینیک محاسبه شد.")
    finally:
        db.close()


async def update_system_metrics():
    logger.info("📈 شروع به‌روزرسانی آمار سیستمی...")
    db = SessionLocal()
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    try:
        from models import SystemMetric
        total_messages = db.query(RawMessage).filter(
            RawMessage.created_at >= today_start
        ).count()
        metric = SystemMetric(
            clinic_id=None,
            date=today_start,
            total_messages=total_messages,
            llm_calls=0,
            llm_cost=0.0,
            human_handoffs=0,
            medical_flags=0,
            bookings=0,
            created_at=now
        )
        db.add(metric)
        db.commit()
        logger.info("✅ آمار سیستمی به‌روزرسانی شد.")
    except Exception as e:
        logger.error(f"خطا در به‌روزرسانی آمار سیستمی: {e}")
        db.rollback()
    finally:
        db.close()


# ========== وظایف شبانه اصلی ==========
async def nightly_jobs():
    logger.info("🌙 شروع اجرای وظایف شبانه...")
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
        await consolidate_all_patients_memories()
        logger.info("✅ یکپارچه‌سازی حافظه انجام شد.")
    except Exception as e:
        logger.error(f"❌ خطا در یکپارچه‌سازی حافظه: {e}")

    try:
        await cleanup_memory()
        logger.info("✅ پاکسازی حافظه انجام شد.")
    except Exception as e:
        logger.error(f"❌ خطا در پاکسازی حافظه: {e}")

    try:
        await update_daily_metrics()
        logger.info("✅ آمار روزانه محاسبه شد.")
    except Exception as e:
        logger.error(f"❌ خطا در محاسبه آمار روزانه: {e}")

    try:
        await update_system_metrics()
        logger.info("✅ آمار سیستمی به‌روزرسانی شد.")
    except Exception as e:
        logger.error(f"❌ خطا در به‌روزرسانی آمار سیستمی: {e}")

    logger.info("✅ همه وظایف شبانه پایان یافت.")


# ========== راه‌اندازی و توقف زمان‌بند ==========
def start_scheduler():
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.add_job(
            nightly_jobs,
            trigger=CronTrigger(hour=2, minute=0),
            id="nightly_jobs",
            replace_existing=True
        )
        scheduler.start()
        logger.info("⏰ زمان‌بند با موفقیت راه‌اندازی شد.")
    else:
        logger.warning("زمان‌بند در حال اجراست، از راه‌اندازی مجدد جلوگیری شد.")


def stop_scheduler():
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("⏰ زمان‌بند متوقف شد.")


def get_scheduled_jobs():
    scheduler = get_scheduler()
    if scheduler.running:
        return [{"id": job.id, "next_run": job.next_run_time} for job in scheduler.get_jobs()]
    return []


if __name__ == "__main__":
    print("=" * 50)
    print("ماژول زمان‌بند ClinicOS (اصلاح شده)")
    print("=" * 50)
    start_scheduler()
    jobs = get_scheduled_jobs()
    for job in jobs:
        print(f"Job: {job['id']}, next run: {job['next_run']}")
    print("زمان‌بند در حال اجراست. Ctrl+C برای توقف.")
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        stop_scheduler()
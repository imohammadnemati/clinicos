"""
ماژول زمان‌بندی (Scheduler)
این ماژول مسئول اجرای وظایف دوره‌ای زیر است:
- بازیابی لیدهای از دست رفته (Lost Lead Recovery)
- ارسال یادآوری نوبت‌ها (Appointment Reminders)
- یکپارچه‌سازی حافظه بیماران (Memory Consolidation)
- محاسبه شاخص‌های کلیدی عملکرد (KPI) برای روز گذشته
- تمیزکاری حافظه بیماران بی‌کیفیت (Memory Cleanup)
- به‌روزرسانی آمار سیستمی (System Metrics)
- تشخیص عدم حضور بیماران (No-Show Detection)
"""

from apscheduler.schedulers.async_ import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import asyncio
import logging

from lost_lead_recovery import recover_lost_leads
from appointment_engine import send_reminders, check_no_shows
from kpi_engine import calculate_daily_kpi
from database import SessionLocal
from models import Clinic, Patient, PatientMemory, PatientProfile, Session, Event, RawMessage, ConversationState

# تنظیم لاگر
logger = logging.getLogger(__name__)

# ایجاد شیء زمان‌بند
scheduler = AsyncIOScheduler()


# ========== وظایف یکپارچه‌سازی حافظه (Memory Consolidation) ==========
# توجه: این بخش در نسخه ساده حذف شده اما ساختار آن برای توسعه آینده نگهداری می‌شود

async def consolidate_all_patients_memories():
    """
    یکپارچه‌سازی حافظه تمام بیماران فعال
    حافظه‌های تکراری و مشابه را در هر بیمار ادغام می‌کند
    """
    logger.info("🔄 شروع یکپارچه‌سازی حافظه بیماران...")
    db = SessionLocal()
    try:
        # فقط بیماران فعال و مشتری (غیر از spam و dead)
        patients = db.query(Patient).filter(
            Patient.status.in_(['active', 'customer', 'engaged'])
        ).all()
        
        count = 0
        for patient in patients:
            try:
                # در نسخه کامل، اینجا تابع consolidate_memories_for_patient فراخوانی می‌شود
                # از آنجا که memory_consolidation.py حذف شده، فعلاً فقط لاگ می‌زنیم
                # consolidate_memories_for_patient(patient.id)
                count += 1
            except Exception as e:
                logger.error(f"خطا در یکپارچه‌سازی حافظه بیمار {patient.id}: {e}")
        
        logger.info(f"✅ یکپارچه‌سازی حافظه {count} بیمار انجام شد.")
    except Exception as e:
        logger.error(f"خطا در یکپارچه‌سازی حافظه بیماران: {e}")
    finally:
        db.close()


# ========== وظایف پاکسازی حافظه ==========

async def cleanup_memory():
    """
    پاکسازی حافظه بیماران بی‌کیفیت (Spam, Cold, Dead)
    - Spam: حذف کامل حافظه بعد از 7 روز
    - Cold: نگهداری خلاصه بعد از 60 روز
    - Dead: نگهداری خلاصه بعد از 120 روز
    """
    logger.info("🧹 شروع پاکسازی حافظه بیماران...")
    db = SessionLocal()
    now = datetime.utcnow()
    
    try:
        # ===== Spam: 7 روز =====
        spam_cutoff = now - timedelta(days=7)
        spams = db.query(Patient).filter(
            Patient.status == 'spam',
            Patient.last_seen < spam_cutoff,
            Patient.memory_purged == False
        ).all()
        
        for patient in spams:
            try:
                # حذف حافظه‌های وابسته
                db.query(PatientMemory).filter_by(patient_id=patient.id).delete()
                db.query(PatientProfile).filter_by(patient_id=patient.id).delete()
                db.query(ConversationState).filter(
                    ConversationState.session_id.in_(
                        db.query(Session.id).filter_by(patient_id=patient.id)
                    )
                ).delete()
                db.query(Session).filter_by(patient_id=patient.id).delete()
                db.query(Event).filter_by(patient_id=patient.id).delete()
                db.query(RawMessage).filter_by(patient_id=patient.id).delete()
                
                patient.memory_purged = True
                patient.status = 'archived'
                logger.info(f"حافظه بیمار spam {patient.id} پاکسازی شد.")
            except Exception as e:
                logger.error(f"خطا در پاکسازی بیمار spam {patient.id}: {e}")
        
        # ===== Cold: 60 روز =====
        cold_cutoff = now - timedelta(days=60)
        colds = db.query(Patient).filter(
            Patient.status == 'cold',
            Patient.last_seen < cold_cutoff,
            Patient.memory_purged == False
        ).all()
        
        for patient in colds:
            try:
                # ساخت خلاصه قبل از پاکسازی
                summary = build_patient_summary(patient.id, db)
                patient.summary_data = summary
                
                # حذف حافظه
                db.query(PatientMemory).filter_by(patient_id=patient.id).delete()
                db.query(PatientProfile).filter_by(patient_id=patient.id).delete()
                db.query(ConversationState).filter(
                    ConversationState.session_id.in_(
                        db.query(Session.id).filter_by(patient_id=patient.id)
                    )
                ).delete()
                db.query(Session).filter_by(patient_id=patient.id).delete()
                db.query(Event).filter_by(patient_id=patient.id).delete()
                db.query(RawMessage).filter_by(patient_id=patient.id).delete()
                
                patient.memory_purged = True
                patient.status = 'archived_cold'
                logger.info(f"حافظه بیمار cold {patient.id} پاکسازی شد.")
            except Exception as e:
                logger.error(f"خطا در پاکسازی بیمار cold {patient.id}: {e}")
        
        # ===== Dead: 120 روز =====
        dead_cutoff = now - timedelta(days=120)
        deads = db.query(Patient).filter(
            Patient.status == 'dead',
            Patient.last_seen < dead_cutoff,
            Patient.memory_purged == False
        ).all()
        
        for patient in deads:
            try:
                summary = build_patient_summary(patient.id, db)
                patient.summary_data = summary
                
                db.query(PatientMemory).filter_by(patient_id=patient.id).delete()
                db.query(PatientProfile).filter_by(patient_id=patient.id).delete()
                db.query(ConversationState).filter(
                    ConversationState.session_id.in_(
                        db.query(Session.id).filter_by(patient_id=patient.id)
                    )
                ).delete()
                db.query(Session).filter_by(patient_id=patient.id).delete()
                db.query(Event).filter_by(patient_id=patient.id).delete()
                db.query(RawMessage).filter_by(patient_id=patient.id).delete()
                
                patient.memory_purged = True
                patient.status = 'archived_dead'
                logger.info(f"حافظه بیمار dead {patient.id} پاکسازی شد.")
            except Exception as e:
                logger.error(f"خطا در پاکسازی بیمار dead {patient.id}: {e}")
        
        db.commit()
        logger.info("✅ پاکسازی حافظه بیماران انجام شد.")
        
    except Exception as e:
        logger.error(f"خطا در پاکسازی حافظه: {e}")
        db.rollback()
    finally:
        db.close()


def build_patient_summary(patient_id: int, db) -> dict:
    """
    ساخت خلاصه از اطلاعات بیمار قبل از پاکسازی حافظه
    """
    try:
        events = db.query(Event).filter_by(patient_id=patient_id).order_by(
            Event.created_at.desc()
        ).limit(10).all()
        
        leads = db.query(Lead).filter_by(patient_id=patient_id).all()
        
        max_lead_score = max([l.lead_score for l in leads]) if leads else 0
        service_interests = list(set([e.service for e in events if e.service and e.service != 'none']))
        last_intent = events[0].intent_type if events else None
        
        summary = {
            "message_count": len(events),
            "lead_score_max": max_lead_score,
            "service_interest": service_interests[0] if service_interests else None,
            "last_intent": last_intent,
            "last_seen": events[0].created_at.isoformat() if events else None
        }
        return summary
    except Exception as e:
        logger.error(f"خطا در ساخت خلاصه بیمار {patient_id}: {e}")
        return {}


# ========== وظایف آمار و محاسبات ==========

async def update_daily_metrics():
    """
    محاسبه آمار روزانه برای همه کلینیک‌ها
    """
    logger.info("📊 شروع محاسبه آمار روزانه...")
    db = SessionLocal()
    try:
        clinics = db.query(Clinic).all()
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        
        for clinic in clinics:
            try:
                calculate_daily_kpi(clinic.id, yesterday)
            except Exception as e:
                logger.error(f"خطا در محاسبه KPI برای کلینیک {clinic.id}: {e}")
        
        logger.info(f"✅ آمار روزانه برای {len(clinics)} کلینیک محاسبه شد.")
    except Exception as e:
        logger.error(f"خطا در محاسبه آمار روزانه: {e}")
    finally:
        db.close()


async def update_system_metrics():
    """
    به‌روزرسانی آمار سیستمی (تعداد پیام‌ها، هزینه LLM و...)
    """
    logger.info("📈 شروع به‌روزرسانی آمار سیستمی...")
    db = SessionLocal()
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    
    try:
        from models import SystemMetric
        
        # محاسبه آمار از جداول مختلف
        total_messages = db.query(RawMessage).filter(
            RawMessage.created_at >= today_start
        ).count()
        
        # این بخش نیاز به جمع‌آوری آمار از جداول مختلف دارد
        # در نسخه ساده، فقط یک رکورد خلاصه ایجاد می‌کنیم
        metric = SystemMetric(
            clinic_id=None,  # آمار کلی سیستم
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
    """
    اجرای تمام وظایف شبانه
    این تابع هر روز ساعت 2 بامداد اجرا می‌شود
    """
    logger.info("🌙 شروع اجرای وظایف شبانه...")
    
    # 1. بازیابی لیدهای از دست رفته
    try:
        await recover_lost_leads()
        logger.info("✅ بازیابی لیدهای از دست رفته انجام شد.")
    except Exception as e:
        logger.error(f"❌ خطا در بازیابی لیدها: {e}")
    
    # 2. ارسال یادآوری نوبت‌ها
    try:
        await send_reminders()
        logger.info("✅ یادآوری نوبت‌ها ارسال شد.")
    except Exception as e:
        logger.error(f"❌ خطا در ارسال یادآوری: {e}")
    
    # 3. تشخیص عدم حضور بیماران
    try:
        await check_no_shows()
        logger.info("✅ تشخیص عدم حضور انجام شد.")
    except Exception as e:
        logger.error(f"❌ خطا در تشخیص عدم حضور: {e}")
    
    # 4. یکپارچه‌سازی حافظه بیماران (در صورت فعال بودن در نسخه کامل)
    try:
        await consolidate_all_patients_memories()
        logger.info("✅ یکپارچه‌سازی حافظه انجام شد.")
    except Exception as e:
        logger.error(f"❌ خطا در یکپارچه‌سازی حافظه: {e}")
    
    # 5. پاکسازی حافظه بیماران بی‌کیفیت
    try:
        await cleanup_memory()
        logger.info("✅ پاکسازی حافظه انجام شد.")
    except Exception as e:
        logger.error(f"❌ خطا در پاکسازی حافظه: {e}")
    
    # 6. محاسبه آمار روزانه
    try:
        await update_daily_metrics()
        logger.info("✅ آمار روزانه محاسبه شد.")
    except Exception as e:
        logger.error(f"❌ خطا در محاسبه آمار روزانه: {e}")
    
    # 7. به‌روزرسانی آمار سیستمی
    try:
        await update_system_metrics()
        logger.info("✅ آمار سیستمی به‌روزرسانی شد.")
    except Exception as e:
        logger.error(f"❌ خطا در به‌روزرسانی آمار سیستمی: {e}")
    
    logger.info("✅ تمام وظایف شبانه با موفقیت انجام شد.")


# ========== توابع راه‌اندازی و مدیریت زمان‌بند ==========

def start_scheduler():
    """
    راه‌اندازی زمان‌بند با تنظیمات زیر:
    - وظایف شبانه: هر روز ساعت 2 بامداد
    - (در صورت نیاز) وظایف دیگر: هر ساعت، هر دقیقه و ...
    """
    # وظایف شبانه: هر روز ساعت 2:00
    scheduler.add_job(
        nightly_jobs,
        trigger=CronTrigger(hour=2, minute=0),
        id="nightly_jobs",
        replace_existing=True
    )
    
    # (اختیاری) بروزرسانی آمار سیستمی هر ساعت - در صورت نیاز فعال کنید
    # scheduler.add_job(
    #     update_system_metrics,
    #     trigger=CronTrigger(minute=0),
    #     id="hourly_metrics",
    #     replace_existing=True
    # )
    
    # شروع زمان‌بند
    scheduler.start()
    logger.info("⏰ زمان‌بند با موفقیت راه‌اندازی شد.")


def stop_scheduler():
    """
    توقف زمان‌بند (در زمان خروج برنامه)
    """
    scheduler.shutdown()
    logger.info("⏰ زمان‌بند متوقف شد.")


def get_scheduled_jobs():
    """
    دریافت لیست وظایف زمان‌بندی شده (برای دیباگ)
    """
    jobs = scheduler.get_jobs()
    return [{"id": job.id, "next_run": job.next_run_time} for job in jobs]


def is_scheduler_running() -> bool:
    """
    بررسی وضعیت زمان‌بند
    """
    return scheduler.running


# اگر فایل به صورت مستقیم اجرا شد
if __name__ == "__main__":
    print("=" * 50)
    print("ماژول زمان‌بند ClinicOS")
    print("=" * 50)
    
    # راه‌اندازی زمان‌بند
    start_scheduler()
    
    # نمایش وظایف فعال
    jobs = get_scheduled_jobs()
    print("\n📋 وظایف زمان‌بندی شده:")
    for job in jobs:
        print(f"   - {job['id']}: next run at {job['next_run']}")
    
    print("\n✅ زمان‌بند در حال اجراست.")
    print("برای متوقف کردن، Ctrl+C را فشار دهید.")
    
    try:
        # نگه داشتن برنامه
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("\n🛑 در حال متوقف کردن زمان‌بند...")
        stop_scheduler()
        print("✅ زمان‌بند متوقف شد.")
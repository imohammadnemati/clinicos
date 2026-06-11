"""
ماژول زمان‌بندی (Scheduler)
این ماژول مسئول اجرای وظایف دوره‌ای زیر است:
- بازیابی لیدهای از دست رفته (Lost Lead Recovery)
- ارسال یادآوری نوبت‌ها (Appointment Reminders)
- یکپارچه‌سازی حافظه بیماران (Memory Consolidation)
- محاسبه شاخص‌های کلیدی عملکرد (KPI) برای روز گذشته
- تمیزکاری حافظه بیماران بی‌کیفیت (Memory Cleanup)
- به‌روزرسانی آمار سیستمی (System Metrics)
"""

from apscheduler.schedulers.async_ import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import asyncio

from database import SessionLocal
from models import Patient, Clinic, SystemMetric
from lost_lead_recovery import recover_lost_leads
from appointment_engine import send_reminders
from memory_consolidation import consolidate_memories_for_patient
from kpi_engine import calculate_daily_kpi

# ایجاد شیء زمان‌بند
scheduler = AsyncIOScheduler()


async def consolidate_all_patients_memories():
    """
    یکپارچه‌سازی حافظه تمام بیماران
    حافظه‌های تکراری و مشابه را در هر بیمار ادغام می‌کند
    """
    print("🔄 شروع یکپارچه‌سازی حافظه بیماران...")
    db = SessionLocal()
    patients = db.query(Patient).filter(
        Patient.status.in_(['active', 'customer', 'engaged'])
    ).all()
    db.close()
    
    count = 0
    for patient in patients:
        try:
            consolidate_memories_for_patient(patient.id)
            count += 1
        except Exception as e:
            print(f"خطا در یکپارچه‌سازی حافظه بیمار {patient.id}: {e}")
    
    print(f"✅ یکپارچه‌سازی حافظه {count} بیمار انجام شد.")


async def cleanup_memory():
    """
    پاکسازی حافظه بیماران بی‌کیفیت (Spam, Cold, Dead)
    - Spam: حذف کامل حافظه بعد از 7 روز
    - Cold: نگهداری خلاصه بعد از 60 روز
    - Dead: نگهداری خلاصه بعد از 120 روز
    """
    print("🧹 شروع پاکسازی حافظه بیماران...")
    db = SessionLocal()
    now = datetime.utcnow()
    
    # Spam: 7 روز
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
            db.commit()
        except Exception as e:
            print(f"خطا در پاکسازی بیمار {patient.id}: {e}")
    
    # Cold: 60 روز
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
            db.commit()
        except Exception as e:
            print(f"خطا در پاکسازی بیمار cold {patient.id}: {e}")
    
    # Dead: 120 روز
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
            db.commit()
        except Exception as e:
            print(f"خطا در پاکسازی بیمار dead {patient.id}: {e}")
    
    db.close()
    print("✅ پاکسازی حافظه بیماران انجام شد.")


def build_patient_summary(patient_id: int, db) -> dict:
    """
    ساخت خلاصه از اطلاعات بیمار قبل از پاکسازی حافظه
    """
    from models import Event, Lead
    
    events = db.query(Event).filter_by(patient_id=patient_id).order_by(Event.created_at.desc()).limit(10).all()
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


async def update_daily_metrics():
    """
    محاسبه آمار روزانه برای همه کلینیک‌ها
    """
    print("📊 شروع محاسبه آمار روزانه...")
    db = SessionLocal()
    clinics = db.query(Clinic).all()
    db.close()
    
    yesterday = datetime.utcnow().date() - timedelta(days=1)
    
    for clinic in clinics:
        try:
            calculate_daily_kpi(clinic.id, yesterday)
        except Exception as e:
            print(f"خطا در محاسبه KPI برای کلینیک {clinic.id}: {e}")
    
    print(f"✅ آمار روزانه برای {len(clinics)} کلینیک محاسبه شد.")


async def update_system_metrics():
    """
    به‌روزرسانی آمار سیستمی (تعداد پیام‌ها، هزینه LLM و...)
    """
    print("📈 شروع به‌روزرسانی آمار سیستمی...")
    db = SessionLocal()
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    
    # این بخش نیاز به جمع‌آوری آمار از جداول مختلف دارد
    # در نسخه ساده، فقط یک رکورد خالی ایجاد می‌کنیم
    metric = SystemMetric(
        clinic_id=None,  # آمار کلی سیستم
        date=today_start,
        total_messages=0,
        llm_calls=0,
        llm_cost=0.0,
        human_handoffs=0,
        medical_flags=0,
        bookings=0,
        created_at=now
    )
    db.add(metric)
    db.commit()
    db.close()
    print("✅ آمار سیستمی به‌روزرسانی شد.")


async def nightly_jobs():
    """
    اجرای تمام وظایف شبانه
    این تابع هر روز ساعت 2 بامداد اجرا می‌شود
    """
    print("🌙 شروع اجرای وظایف شبانه...")
    
    # 1. بازیابی لیدهای از دست رفته
    try:
        await recover_lost_leads()
        print("✅ بازیابی لیدهای از دست رفته انجام شد.")
    except Exception as e:
        print(f"❌ خطا در بازیابی لیدها: {e}")
    
    # 2. ارسال یادآوری نوبت‌ها
    try:
        await send_reminders()
        print("✅ یادآوری نوبت‌ها ارسال شد.")
    except Exception as e:
        print(f"❌ خطا در ارسال یادآوری: {e}")
    
    # 3. یکپارچه‌سازی حافظه بیماران
    try:
        await consolidate_all_patients_memories()
        print("✅ یکپارچه‌سازی حافظه انجام شد.")
    except Exception as e:
        print(f"❌ خطا در یکپارچه‌سازی حافظه: {e}")
    
    # 4. پاکسازی حافظه بیماران بی‌کیفیت
    try:
        await cleanup_memory()
        print("✅ پاکسازی حافظه انجام شد.")
    except Exception as e:
        print(f"❌ خطا در پاکسازی حافظه: {e}")
    
    # 5. محاسبه آمار روزانه
    try:
        await update_daily_metrics()
        print("✅ آمار روزانه محاسبه شد.")
    except Exception as e:
        print(f"❌ خطا در محاسبه آمار روزانه: {e}")
    
    # 6. به‌روزرسانی آمار سیستمی
    try:
        await update_system_metrics()
        print("✅ آمار سیستمی به‌روزرسانی شد.")
    except Exception as e:
        print(f"❌ خطا در به‌روزرسانی آمار سیستمی: {e}")
    
    print("✅ تمام وظایف شبانه با موفقیت انجام شد.")


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
    
    # (اختیاری) بروزرسانی آمار سیستمی هر ساعت
    # scheduler.add_job(
    #     update_system_metrics,
    #     trigger=CronTrigger(minute=0),
    #     id="hourly_metrics",
    #     replace_existing=True
    # )
    
    # شروع زمان‌بند
    scheduler.start()
    print("⏰ زمان‌بند با موفقیت راه‌اندازی شد.")


def stop_scheduler():
    """
    توقف زمان‌بند (در زمان خروج برنامه)
    """
    scheduler.shutdown()
    print("⏰ زمان‌بند متوقف شد.")


def get_scheduled_jobs():
    """
    دریافت لیست وظایف زمان‌بندی شده (برای دیباگ)
    """
    jobs = scheduler.get_jobs()
    return [{"id": job.id, "next_run": job.next_run_time} for job in jobs]
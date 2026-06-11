"""
ماژول مدیریت جلسات (Session Manager)
این ماژول مسئول ایجاد، نگهداری و بستن جلسات مکالمه با بیماران است.

قابلیت‌ها:
- ایجاد جلسه جدید برای بیمار
- یافتن جلسه فعال موجود
- بستن خودکار جلسات منقضی شده
- مدیریت زمان آخرین فعالیت جلسه
- پشتیبانی از حافظه کوتاه‌مدت مکالمه
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from database import SessionLocal
from models import Session
from config import SESSION_HOURS
import logging

# تنظیم لاگر
logger = logging.getLogger(__name__)


# ========== توابع اصلی مدیریت جلسات ==========

def get_or_create_session(clinic_id: int, patient_id: int) -> int:
    """
    دریافت جلسه فعال موجود یا ایجاد جلسه جدید برای بیمار
    پارامترها:
        clinic_id: شناسه کلینیک
        patient_id: شناسه بیمار
    خروجی:
        شناسه جلسه (session_id)
    """
    db = SessionLocal()
    now = datetime.utcnow()
    
    try:
        # محاسبه زمان آستانه برای جلسات فعال (بر اساس SESSION_HOURS)
        cutoff = now - timedelta(hours=SESSION_HOURS)
        
        # جستجوی جلسه فعال در بازه زمانی مجاز
        active_session = db.query(Session).filter(
            Session.clinic_id == clinic_id,
            Session.patient_id == patient_id,
            Session.is_active == True,
            Session.start_time > cutoff
        ).first()
        
        if active_session:
            # به‌روزرسانی زمان آخرین فعالیت
            active_session.last_activity = now
            db.commit()
            logger.debug(f"جلسه فعال موجود برای بیمار {patient_id}: {active_session.id}")
            return active_session.id
        
        # بستن جلسات قدیمی و غیرفعال
        db.query(Session).filter(
            Session.clinic_id == clinic_id,
            Session.patient_id == patient_id,
            Session.is_active == True
        ).update({
            "is_active": False,
            "end_time": now
        })
        
        # ایجاد جلسه جدید
        new_session = Session(
            clinic_id=clinic_id,
            patient_id=patient_id,
            start_time=now,
            last_activity=now,
            is_active=True,
            requires_human=False,
            conversation_status='active'
        )
        db.add(new_session)
        db.commit()
        
        session_id = new_session.id
        logger.info(f"جلسه جدید برای بیمار {patient_id} ایجاد شد: {session_id}")
        return session_id
        
    except Exception as e:
        logger.error(f"خطا در ایجاد/دریافت جلسه برای بیمار {patient_id}: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def get_active_session(clinic_id: int, patient_id: int) -> Optional[Session]:
    """
    دریافت جلسه فعال بیمار (بدون ایجاد جلسه جدید)
    پارامترها:
        clinic_id: شناسه کلینیک
        patient_id: شناسه بیمار
    خروجی:
        شیء جلسه یا None در صورت عدم وجود جلسه فعال
    """
    db = SessionLocal()
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=SESSION_HOURS)
    
    try:
        session = db.query(Session).filter(
            Session.clinic_id == clinic_id,
            Session.patient_id == patient_id,
            Session.is_active == True,
            Session.start_time > cutoff
        ).first()
        return session
    except Exception as e:
        logger.error(f"خطا در دریافت جلسه فعال برای بیمار {patient_id}: {e}")
        return None
    finally:
        db.close()


def close_session(session_id: int) -> bool:
    """
    بستن جلسه (غیرفعال کردن)
    پارامترها:
        session_id: شناسه جلسه
    خروجی:
        True در صورت موفقیت، False در غیر این صورت
    """
    db = SessionLocal()
    now = datetime.utcnow()
    
    try:
        result = db.query(Session).filter_by(id=session_id).update({
            "is_active": False,
            "end_time": now
        })
        db.commit()
        
        if result:
            logger.info(f"جلسه {session_id} بسته شد.")
            return True
        else:
            logger.warning(f"جلسه {session_id} یافت نشد.")
            return False
    except Exception as e:
        logger.error(f"خطا در بستن جلسه {session_id}: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def update_session_activity(session_id: int) -> bool:
    """
    به‌روزرسانی زمان آخرین فعالیت جلسه
    پارامترها:
        session_id: شناسه جلسه
    خروجی:
        True در صورت موفقیت، False در غیر این صورت
    """
    db = SessionLocal()
    try:
        session = db.query(Session).filter_by(id=session_id).first()
        if session:
            session.last_activity = datetime.utcnow()
            db.commit()
            logger.debug(f"زمان آخرین فعالیت جلسه {session_id} به‌روزرسانی شد.")
            return True
        else:
            logger.warning(f"جلسه {session_id} یافت نشد.")
            return False
    except Exception as e:
        logger.error(f"خطا در به‌روزرسانی فعالیت جلسه {session_id}: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def set_session_requires_human(session_id: int, requires_human: bool = True) -> bool:
    """
    تنظیم وضعیت نیاز به مداخله انسانی در جلسه
    پارامترها:
        session_id: شناسه جلسه
        requires_human: آیا نیاز به انسان دارد؟
    خروجی:
        True در صورت موفقیت، False در غیر این صورت
    """
    db = SessionLocal()
    
    try:
        result = db.query(Session).filter_by(id=session_id).update({
            "requires_human": requires_human,
            "conversation_status": "human_required" if requires_human else "active"
        })
        db.commit()
        return result > 0
    except Exception as e:
        logger.error(f"خطا در تنظیم human handoff جلسه {session_id}: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def get_session_conversation_state(session_id: int) -> Optional[dict]:
    """
    دریافت وضعیت مکالمه جلسه
    پارامترها:
        session_id: شناسه جلسه
    خروجی:
        دیکشنری شامل اطلاعات جلسه یا None
    """
    db = SessionLocal()
    
    try:
        session = db.query(Session).filter_by(id=session_id).first()
        if not session:
            return None
        
        return {
            "id": session.id,
            "patient_id": session.patient_id,
            "start_time": session.start_time,
            "is_active": session.is_active,
            "requires_human": session.requires_human,
            "conversation_status": session.conversation_status,
            "last_activity": session.last_activity
        }
    except Exception as e:
        logger.error(f"خطا در دریافت وضعیت جلسه {session_id}: {e}")
        return None
    finally:
        db.close()


def is_session_active(session_id: int) -> bool:
    """
    بررسی فعال بودن جلسه
    پارامترها:
        session_id: شناسه جلسه
    خروجی:
        True اگر جلسه فعال باشد، False در غیر این صورت
    """
    db = SessionLocal()
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=SESSION_HOURS)
    
    try:
        session = db.query(Session).filter(
            Session.id == session_id,
            Session.is_active == True,
            Session.start_time > cutoff
        ).first()
        return session is not None
    except Exception as e:
        logger.error(f"خطا در بررسی فعال بودن جلسه {session_id}: {e}")
        return False
    finally:
        db.close()


def close_all_patient_sessions(patient_id: int) -> int:
    """
    بستن تمام جلسات فعال یک بیمار
    پارامترها:
        patient_id: شناسه بیمار
    خروجی:
        تعداد جلسات بسته شده
    """
    db = SessionLocal()
    now = datetime.utcnow()
    
    try:
        result = db.query(Session).filter(
            Session.patient_id == patient_id,
            Session.is_active == True
        ).update({
            "is_active": False,
            "end_time": now
        })
        db.commit()
        
        if result:
            logger.info(f"{result} جلسه فعال برای بیمار {patient_id} بسته شد.")
        return result
    except Exception as e:
        logger.error(f"خطا در بستن جلسات بیمار {patient_id}: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def get_patient_session_history(patient_id: int, limit: int = 10) -> list:
    """
    دریافت تاریخچه جلسات بیمار (آخرین جلسات)
    پارامترها:
        patient_id: شناسه بیمار
        limit: حداکثر تعداد جلسات
    خروجی:
        لیست جلسات
    """
    db = SessionLocal()
    
    try:
        sessions = db.query(Session).filter(
            Session.patient_id == patient_id
        ).order_by(Session.start_time.desc()).limit(limit).all()
        
        return [
            {
                "id": s.id,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "is_active": s.is_active,
                "requires_human": s.requires_human
            }
            for s in sessions
        ]
    except Exception as e:
        logger.error(f"خطا در دریافت تاریخچه جلسات بیمار {patient_id}: {e}")
        return []
    finally:
        db.close()


def get_active_sessions_count(clinic_id: int) -> int:
    """
    دریافت تعداد جلسات فعال کلینیک
    پارامترها:
        clinic_id: شناسه کلینیک
    خروجی:
        تعداد جلسات فعال
    """
    db = SessionLocal()
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=SESSION_HOURS)
    
    try:
        count = db.query(Session).filter(
            Session.clinic_id == clinic_id,
            Session.is_active == True,
            Session.start_time > cutoff
        ).count()
        return count
    except Exception as e:
        logger.error(f"خطا در دریافت تعداد جلسات فعال کلینیک {clinic_id}: {e}")
        return 0
    finally:
        db.close()


def format_session_duration(session: Session) -> str:
    """
    فرمت کردن مدت زمان جلسه برای نمایش
    """
    if not session.end_time:
        end = datetime.utcnow()
    else:
        end = session.end_time
    
    duration = end - session.start_time
    minutes = int(duration.total_seconds() / 60)
    
    if minutes < 60:
        return f"{minutes} دقیقه"
    else:
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours} ساعت و {mins} دقیقه"


# اگر فایل به صورت مستقیم اجرا شد
if __name__ == "__main__":
    print("=" * 50)
    print("ماژول مدیریت جلسات ClinicOS")
    print("=" * 50)
    print("✅ ماژول session_manager بارگذاری شد.")
    print("توابع اصلی: get_or_create_session(), close_session(), update_session_activity()")
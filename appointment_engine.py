"""
ماژول موتور نوبت‌دهی (Appointment Engine)
مسئول مدیریت فرآیند نوبت‌دهی: ایجاد، تأیید، لغو، تغییر زمان، یادآوری و تکمیل نوبت.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from database import SessionLocal
from models import (
    Appointment, AppointmentRequest, Lead, PipelineHistory,
    PatientAlias, Staff, Clinic, Patient
)
from config import BOT_TOKEN
import requests
import asyncio
import logging

logger = logging.getLogger(__name__)

# ========== ثابت‌های وضعیت نوبت (جلوگیری از اشتباه تایپی) ==========
APPOINTMENT_PENDING = "pending"
APPOINTMENT_CONFIRMED = "confirmed"
APPOINTMENT_SCHEDULED = "scheduled"
APPOINTMENT_COMPLETED = "completed"
APPOINTMENT_CANCELLED = "cancelled"
APPOINTMENT_NO_SHOW = "no_show"

APPOINTMENT_REQUEST_PENDING = "pending"
APPOINTMENT_REQUEST_CONFIRMED = "confirmed"
APPOINTMENT_REQUEST_CANCELLED = "cancelled"

# تنظیمات پیش‌فرض
DEFAULT_REMINDER_HOURS = 24
MAX_RESCHEDULE_ATTEMPTS = 3


async def send_telegram_message(chat_id: int, text: str) -> bool:
    """ارسال پیام به تلگرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"خطا در ارسال پیام به تلگرام: {e}")
        return False


# ========== توابع داخلی کمکی ==========
def _is_future_date(date: datetime) -> bool:
    """بررسی اینکه تاریخ در آینده است (با حاشیه 5 دقیقه)"""
    return date > (datetime.utcnow() + timedelta(minutes=5))


def _get_existing_appointment(patient_id: int, appointment_date: datetime) -> Optional[Appointment]:
    """بررسی وجود نوبت تکراری (برای جلوگیری از داپلیکیت)"""
    db = SessionLocal()
    try:
        existing = db.query(Appointment).filter(
            Appointment.patient_id == patient_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status.in_([APPOINTMENT_SCHEDULED, APPOINTMENT_CONFIRMED])
        ).first()
        return existing
    finally:
        db.close()


# ========== توابع اصلی مدیریت نوبت ==========
def create_appointment(
    lead_id: int,
    appointment_date: datetime,
    staff_id: Optional[int] = None,
    notes: Optional[str] = None
) -> Optional[Appointment]:
    """
    ایجاد مستقیم نوبت (بدون درخواست قبلی) – با بررسی داپلیکیت و تاریخ آینده
    """
    if not _is_future_date(appointment_date):
        logger.error("تاریخ نوبت باید در آینده باشد")
        return None

    db = SessionLocal()
    try:
        lead = db.query(Lead).filter_by(id=lead_id).first()
        if not lead:
            logger.error(f"لید {lead_id} یافت نشد")
            return None

        # بررسی نوبت تکراری
        existing = _get_existing_appointment(lead.patient_id, appointment_date)
        if existing:
            logger.warning(f"نوبت تکراری برای بیمار {lead.patient_id} در تاریخ {appointment_date}")
            return existing

        # ایجاد نوبت
        appointment = Appointment(
            clinic_id=lead.clinic_id,
            lead_id=lead_id,
            patient_id=lead.patient_id,
            service=lead.service,
            appointment_date=appointment_date,
            status=APPOINTMENT_SCHEDULED,
            reminder_sent=False,
            no_show=False,
            created_at=datetime.utcnow()
        )
        db.add(appointment)
        db.flush()

        # به‌روزرسانی پیپلاین لید
        lead.pipeline_stage = "booked"
        ph = PipelineHistory(lead_id=lead.id, stage="booked", changed_at=datetime.utcnow())
        if staff_id:
            ph.changed_by = staff_id
        db.add(ph)

        db.commit()
        logger.info(f"نوبت جدید برای لید {lead_id} در تاریخ {appointment_date} ایجاد شد")
        return appointment
    except Exception as e:
        logger.error(f"خطا در ایجاد نوبت: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def create_appointment_request(
    lead_id: int,
    suggested_date: datetime,
    notes: Optional[str] = None
) -> Optional[int]:
    """ایجاد درخواست نوبت جدید (نیازمند تأیید منشی/پزشک)"""
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter_by(id=lead_id).first()
        if not lead:
            logger.error(f"لید {lead_id} یافت نشد")
            return None

        # بررسی نوبت تکراری در حالت درخواست
        existing_req = db.query(AppointmentRequest).filter(
            AppointmentRequest.lead_id == lead_id,
            AppointmentRequest.status == APPOINTMENT_REQUEST_PENDING
        ).first()
        if existing_req:
            logger.warning(f"درخواست نوبت قبلاً برای لید {lead_id} وجود دارد")
            return existing_req.id

        appointment_request = AppointmentRequest(
            clinic_id=lead.clinic_id,
            lead_id=lead_id,
            suggested_date=suggested_date,
            status=APPOINTMENT_REQUEST_PENDING,
            notes=notes,
            created_at=datetime.utcnow()
        )
        db.add(appointment_request)

        # به‌روزرسانی پیپلاین لید به "در انتظار مشاوره"
        lead.pipeline_stage = "consultation"
        ph = PipelineHistory(lead_id=lead.id, stage="consultation", changed_at=datetime.utcnow())
        db.add(ph)
        db.commit()

        # ارسال اعلان به کارکنان
        asyncio.create_task(_notify_staff_for_request(lead.clinic_id, appointment_request.id))
        return appointment_request.id
    except Exception as e:
        logger.error(f"خطا در ایجاد درخواست نوبت: {e}")
        db.rollback()
        return None
    finally:
        db.close()


async def _notify_staff_for_request(clinic_id: int, request_id: int):
    """اعلان به کارکنان برای درخواست نوبت جدید"""
    db = SessionLocal()
    try:
        staff_list = db.query(Staff).filter(
            Staff.clinic_id == clinic_id,
            Staff.role.in_(['owner', 'doctor', 'secretary'])
        ).all()
        req = db.query(AppointmentRequest).filter_by(id=request_id).first()
        if not req:
            return
        lead = db.query(Lead).filter_by(id=req.lead_id).first()
        patient = db.query(Patient).filter_by(id=lead.patient_id).first() if lead else None

        message = f"📅 *درخواست نوبت جدید*\n\n"
        message += f"بیمار: {patient.name if patient else 'نامشخص'}\n"
        message += f"خدمت: {lead.service if lead else 'نامشخص'}\n"
        message += f"تاریخ پیشنهادی: {req.suggested_date}\n"
        message += f"شناسه درخواست: `{request_id}`\n"
        message += f"برای تأیید: `/confirm_appt {request_id} [YYYY-MM-DD HH:MM]`"

        for staff in staff_list:
            await send_telegram_message(staff.telegram_id, message)
            await asyncio.sleep(0.5)
    finally:
        db.close()


def confirm_appointment(request_id: int, confirmed_date: datetime, staff_id: int) -> bool:
    """تأیید درخواست نوبت و تبدیل به نوبت قطعی (با بررسی تاریخ آینده و عدم تکراری)"""
    if not _is_future_date(confirmed_date):
        logger.error("تاریخ تأیید شده باید در آینده باشد")
        return False

    db = SessionLocal()
    try:
        appointment_request = db.query(AppointmentRequest).filter_by(id=request_id).first()
        if not appointment_request or appointment_request.status != APPOINTMENT_REQUEST_PENDING:
            logger.error(f"درخواست {request_id} معتبر نیست")
            return False

        lead = db.query(Lead).filter_by(id=appointment_request.lead_id).first()
        if not lead:
            return False

        # بررسی نوبت تکراری
        existing = _get_existing_appointment(lead.patient_id, confirmed_date)
        if existing:
            logger.warning(f"نوبت تکراری برای بیمار {lead.patient_id} در تاریخ {confirmed_date}")
            # می‌توانیم همان نوبت را برگردانیم، ولی در اینجا خطا در نظر می‌گیریم
            return False

        # به‌روزرسانی درخواست
        appointment_request.status = APPOINTMENT_REQUEST_CONFIRMED
        appointment_request.confirmed_date = confirmed_date
        appointment_request.confirmed_by = staff_id

        # ایجاد نوبت قطعی
        appointment = Appointment(
            clinic_id=appointment_request.clinic_id,
            lead_id=appointment_request.lead_id,
            patient_id=lead.patient_id,
            service=lead.service,
            appointment_date=confirmed_date,
            status=APPOINTMENT_SCHEDULED,
            reminder_sent=False,
            no_show=False,
            created_at=datetime.utcnow()
        )
        db.add(appointment)

        # به‌روزرسانی پیپلاین لید
        lead.pipeline_stage = "booked"
        ph = PipelineHistory(lead_id=lead.id, stage="booked", changed_at=datetime.utcnow(), changed_by=staff_id)
        db.add(ph)

        db.commit()

        # ارسال پیام تأیید به بیمار
        asyncio.create_task(_notify_patient_confirmed(lead.patient_id, confirmed_date, lead.service))
        return True
    except Exception as e:
        logger.error(f"خطا در تأیید نوبت: {e}")
        db.rollback()
        return False
    finally:
        db.close()


async def _notify_patient_confirmed(patient_id: int, appointment_date: datetime, service: str):
    """ارسال پیام تأیید نوبت به بیمار"""
    db = SessionLocal()
    try:
        alias = db.query(PatientAlias).filter_by(patient_id=patient_id, platform='telegram').first()
        if alias and alias.external_user_id:
            date_str = appointment_date.strftime("%Y/%m/%d ساعت %H:%M")
            message = f"✅ *نوبت شما تأیید شد*\n\nخدمت: {service}\nتاریخ و ساعت: {date_str}\n\n📌 لطفاً ۱۵ دقیقه قبل حضور داشته باشید."
            await send_telegram_message(int(alias.external_user_id), message)
    finally:
        db.close()


def cancel_appointment(appointment_id: int, reason: Optional[str] = None, staff_id: Optional[int] = None) -> bool:
    """لغو نوبت (با به‌روزرسانی پیپلاین)"""
    db = SessionLocal()
    try:
        appointment = db.query(Appointment).filter_by(id=appointment_id).first()
        if not appointment or appointment.status == APPOINTMENT_CANCELLED:
            return False

        appointment.status = APPOINTMENT_CANCELLED
        lead = db.query(Lead).filter_by(id=appointment.lead_id).first()
        if lead:
            lead.pipeline_stage = "lost"
            ph = PipelineHistory(lead_id=lead.id, stage="lost", changed_at=datetime.utcnow(), changed_by=staff_id)
            db.add(ph)

        db.commit()
        asyncio.create_task(_notify_patient_cancellation(appointment.patient_id, appointment.service, reason))
        return True
    except Exception as e:
        logger.error(f"خطا در لغو نوبت: {e}")
        db.rollback()
        return False
    finally:
        db.close()


async def _notify_patient_cancellation(patient_id: int, service: str, reason: Optional[str] = None):
    db = SessionLocal()
    try:
        alias = db.query(PatientAlias).filter_by(patient_id=patient_id, platform='telegram').first()
        if alias and alias.external_user_id:
            message = f"❌ *لغو نوبت*\n\nخدمت: {service}\n" + (f"دلیل: {reason}\n" if reason else "")
            await send_telegram_message(int(alias.external_user_id), message)
    finally:
        db.close()


def complete_appointment(appointment_id: int, revenue: Optional[float] = None) -> bool:
    """تکمیل نوبت و ثبت درآمد"""
    db = SessionLocal()
    try:
        appointment = db.query(Appointment).filter_by(id=appointment_id).first()
        if not appointment or appointment.status != APPOINTMENT_SCHEDULED:
            return False
        appointment.status = APPOINTMENT_COMPLETED
        if revenue is not None:
            appointment.revenue = revenue
        lead = db.query(Lead).filter_by(id=appointment.lead_id).first()
        if lead:
            lead.pipeline_stage = "completed"
            ph = PipelineHistory(lead_id=lead.id, stage="completed", changed_at=datetime.utcnow())
            db.add(ph)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"خطا در تکمیل نوبت: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def reschedule_appointment(appointment_id: int, new_date: datetime, staff_id: Optional[int] = None) -> bool:
    """تغییر زمان نوبت (با بررسی تاریخ آینده و عدم تکراری)"""
    if not _is_future_date(new_date):
        return False
    db = SessionLocal()
    try:
        appointment = db.query(Appointment).filter_by(id=appointment_id).first()
        if not appointment:
            return False
        # بررسی نوبت تکراری
        existing = _get_existing_appointment(appointment.patient_id, new_date)
        if existing:
            return False
        old_date = appointment.appointment_date
        appointment.appointment_date = new_date
        appointment.reminder_sent = False
        db.commit()
        asyncio.create_task(_notify_patient_reschedule(appointment.patient_id, old_date, new_date, appointment.service))
        return True
    except Exception as e:
        logger.error(f"خطا در تغییر زمان نوبت: {e}")
        db.rollback()
        return False
    finally:
        db.close()


async def _notify_patient_reschedule(patient_id: int, old_date: datetime, new_date: datetime, service: str):
    db = SessionLocal()
    try:
        alias = db.query(PatientAlias).filter_by(patient_id=patient_id, platform='telegram').first()
        if alias and alias.external_user_id:
            old_str = old_date.strftime("%Y/%m/%d ساعت %H:%M")
            new_str = new_date.strftime("%Y/%m/%d ساعت %H:%M")
            message = f"🔄 *تغییر زمان نوبت*\n\nخدمت: {service}\nتاریخ قبلی: {old_str}\nتاریخ جدید: {new_str}"
            await send_telegram_message(int(alias.external_user_id), message)
    finally:
        db.close()


async def send_reminders():
    """ارسال یادآوری نوبت‌های 24 ساعت آینده (با جلوگیری از ارسال تکراری)"""
    logger.info("📅 شروع ارسال یادآوری نوبت‌ها...")
    db = SessionLocal()
    now = datetime.utcnow()
    reminder_time = now + timedelta(hours=DEFAULT_REMINDER_HOURS)

    appointments = db.query(Appointment).filter(
        Appointment.status == APPOINTMENT_SCHEDULED,
        Appointment.reminder_sent == False,
        Appointment.appointment_date <= reminder_time,
        Appointment.appointment_date > now
    ).all()

    sent = 0
    for appt in appointments:
        alias = db.query(PatientAlias).filter_by(patient_id=appt.patient_id, platform='telegram').first()
        if alias and alias.external_user_id:
            hours_left = int((appt.appointment_date - now).total_seconds() / 3600)
            date_str = appt.appointment_date.strftime("%Y/%m/%d ساعت %H:%M")
            message = f"🔔 *یادآوری نوبت*\n\nخدمت: {appt.service}\nتاریخ و ساعت: {date_str}\n⏰ {hours_left} ساعت دیگر"
            await send_telegram_message(int(alias.external_user_id), message)
            appt.reminder_sent = True
            sent += 1
            await asyncio.sleep(0.5)
    db.commit()
    db.close()
    logger.info(f"✅ {sent} یادآوری ارسال شد.")


async def check_no_shows():
    """تشخیص عدم حضور (نوبت‌های گذشته بدون انجام)"""
    logger.info("🔍 بررسی نوبت‌های بدون حضور...")
    db = SessionLocal()
    now = datetime.utcnow()
    check_time = now - timedelta(hours=2)

    past_appointments = db.query(Appointment).filter(
        Appointment.status == APPOINTMENT_SCHEDULED,
        Appointment.appointment_date <= check_time,
        Appointment.no_show == False
    ).all()

    for appt in past_appointments:
        appt.status = APPOINTMENT_NO_SHOW
        appt.no_show = True
        lead = db.query(Lead).filter_by(id=appt.lead_id).first()
        if lead:
            lead.pipeline_stage = "no_show"
            ph = PipelineHistory(lead_id=lead.id, stage="no_show", changed_at=datetime.utcnow())
            db.add(ph)
    db.commit()
    db.close()
    logger.info(f"✅ {len(past_appointments)} نوبت بدون حضور ثبت شد.")


def get_upcoming_appointments(clinic_id: int, days: int = 7) -> List[Dict]:
    db = SessionLocal()
    now = datetime.utcnow()
    future = now + timedelta(days=days)
    appointments = db.query(Appointment, Patient).join(Patient).filter(
        Appointment.clinic_id == clinic_id,
        Appointment.status == APPOINTMENT_SCHEDULED,
        Appointment.appointment_date > now,
        Appointment.appointment_date <= future
    ).order_by(Appointment.appointment_date).all()
    result = [{"id": a.id, "patient_name": p.name, "service": a.service, "date": a.appointment_date.isoformat()} for a, p in appointments]
    db.close()
    return result


def get_today_appointments(clinic_id: int) -> List[Dict]:
    db = SessionLocal()
    now = datetime.utcnow()
    start = datetime(now.year, now.month, now.day)
    end = start + timedelta(days=1)
    appointments = db.query(Appointment, Patient).join(Patient).filter(
        Appointment.clinic_id == clinic_id,
        Appointment.status == APPOINTMENT_SCHEDULED,
        Appointment.appointment_date >= start,
        Appointment.appointment_date < end
    ).order_by(Appointment.appointment_date).all()
    result = [{"id": a.id, "patient_name": p.name, "service": a.service, "time": a.appointment_date.strftime("%H:%M")} for a, p in appointments]
    db.close()
    return result
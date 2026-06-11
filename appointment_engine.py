"""
ماژول موتور نوبت‌دهی (Appointment Engine)
این ماژول مسئول مدیریت فرآیند نوبت‌دهی است:
- ثبت درخواست نوبت
- تأیید نوبت توسط منشی/پزشک
- ارسال یادآوری خودکار نوبت
- تشخیص عدم حضور (No-Show)
- مدیریت تغییر زمان نوبت (Reschedule)
- لغو نوبت
- ارتباط با لید و پیپلاین فروش
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from database import SessionLocal
from models import (
    Appointment, AppointmentRequest, Lead, LeadStatusHistory, 
    PipelineHistory, PatientAlias, Staff, Clinic, Patient
)
from config import BOT_TOKEN, OWNER_TELEGRAM_ID
import requests
import asyncio
import json

# تنظیمات پیش‌فرض
DEFAULT_REMINDER_HOURS = 24  # یادآوری 24 ساعت قبل
MAX_RESCHEDULE_ATTEMPTS = 3  # حداکثر تعداد درخواست تغییر زمان


async def send_telegram_message(chat_id: int, text: str) -> bool:
    """
    ارسال پیام به تلگرام
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"خطا در ارسال پیام به تلگرام: {e}")
        return False


def create_appointment_request(
    lead_id: int, 
    suggested_date: datetime,
    suggested_time: Optional[str] = None,
    notes: Optional[str] = None
) -> Optional[int]:
    """
    ایجاد درخواست نوبت جدید از روی لید
    پارامترها:
        lead_id: شناسه لید
        suggested_date: تاریخ پیشنهادی
        suggested_time: ساعت پیشنهادی (اختیاری)
        notes: توضیحات اضافی
    خروجی:
        شناسه درخواست نوبت یا None در صورت خطا
    """
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter_by(id=lead_id).first()
        if not lead:
            print(f"لید با شناسه {lead_id} یافت نشد.")
            return None
        
        # ترکیب تاریخ و ساعت
        if suggested_time:
            suggested_datetime = datetime.strptime(
                f"{suggested_date.date()} {suggested_time}", 
                "%Y-%m-%d %H:%M"
            )
        else:
            suggested_datetime = suggested_date
        
        # ایجاد درخواست نوبت
        appointment_request = AppointmentRequest(
            clinic_id=lead.clinic_id,
            lead_id=lead_id,
            suggested_date=suggested_datetime,
            status='pending',
            notes=notes,
            created_at=datetime.utcnow()
        )
        db.add(appointment_request)
        
        # به‌روزرسانی وضعیت لید
        lead.pipeline_stage = 'consultation'
        ph = PipelineHistory(lead_id=lead_id, stage='consultation', changed_at=datetime.utcnow())
        db.add(ph)
        
        db.commit()
        request_id = appointment_request.id
        
        # ارسال اعلان به منشی‌ها و پزشک (اجرای غیرهمگام)
        asyncio.create_task(notify_staff_for_appointment_request(lead.clinic_id, request_id))
        
        return request_id
    except Exception as e:
        print(f"خطا در ایجاد درخواست نوبت: {e}")
        db.rollback()
        return None
    finally:
        db.close()


async def notify_staff_for_appointment_request(clinic_id: int, request_id: int):
    """
    ارسال اعلان به کارکنان کلینیک برای درخواست نوبت جدید
    """
    db = SessionLocal()
    try:
        staff_list = db.query(Staff).filter(
            Staff.clinic_id == clinic_id,
            Staff.role.in_(['owner', 'doctor', 'secretary'])
        ).all()
        
        appointment_request = db.query(AppointmentRequest).filter_by(id=request_id).first()
        if not appointment_request:
            return
            
        lead = db.query(Lead).filter_by(id=appointment_request.lead_id).first()
        patient = db.query(Patient).filter_by(id=lead.patient_id).first() if lead else None
        
        message = f"📅 *درخواست نوبت جدید*\n\n"
        message += f"بیمار: {patient.name if patient else 'نامشخص'}\n"
        message += f"خدمت: {lead.service if lead else 'نامشخص'}\n"
        message += f"تاریخ پیشنهادی: {appointment_request.suggested_date}\n"
        if appointment_request.notes:
            message += f"توضیحات: {appointment_request.notes}\n"
        message += f"\nشناسه درخواست: `{request_id}`\n"
        message += f"برای تأیید، از دستور زیر استفاده کنید:\n"
        message += f"/confirm_appt {request_id} [YYYY-MM-DD HH:MM]"
        
        for staff in staff_list:
            await send_telegram_message(staff.telegram_id, message)
            await asyncio.sleep(0.5)  # جلوگیری از rate limit
    except Exception as e:
        print(f"خطا در ارسال اعلان به کارکنان: {e}")
    finally:
        db.close()


def confirm_appointment(request_id: int, confirmed_date: datetime, staff_id: int) -> bool:
    """
    تأیید نوبت توسط منشی یا پزشک
    پارامترها:
        request_id: شناسه درخواست نوبت
        confirmed_date: تاریخ و زمان تأیید شده
        staff_id: شناسه کارکن تأییدکننده
    خروجی:
        True در صورت موفقیت، False در غیر این صورت
    """
    db = SessionLocal()
    try:
        appointment_request = db.query(AppointmentRequest).filter_by(id=request_id).first()
        if not appointment_request:
            print(f"درخواست نوبت {request_id} یافت نشد.")
            return False
        
        if appointment_request.status != 'pending':
            print(f"درخواست نوبت {request_id} قبلاً {appointment_request.status} شده است.")
            return False
        
        # به‌روزرسانی درخواست
        appointment_request.status = 'confirmed'
        appointment_request.confirmed_date = confirmed_date
        appointment_request.confirmed_by = staff_id
        
        # ایجاد نوبت قطعی
        lead = db.query(Lead).filter_by(id=appointment_request.lead_id).first()
        if not lead:
            print(f"لید مرتبط با درخواست {request_id} یافت نشد.")
            db.rollback()
            return False
        
        appointment = Appointment(
            clinic_id=appointment_request.clinic_id,
            lead_id=appointment_request.lead_id,
            patient_id=lead.patient_id,
            service=lead.service,
            appointment_date=confirmed_date,
            status='scheduled',
            reminder_sent=False,
            no_show=False,
            created_at=datetime.utcnow()
        )
        db.add(appointment)
        
        # به‌روزرسانی وضعیت لید
        lead.pipeline_stage = 'booked'
        ph = PipelineHistory(lead_id=lead.id, stage='booked', changed_at=datetime.utcnow())
        db.add(ph)
        
        db.commit()
        
        # ارسال پیام تأیید به بیمار (اجرای غیرهمگام)
        asyncio.create_task(notify_patient_appointment_confirmed(lead.patient_id, confirmed_date, lead.service))
        
        return True
    except Exception as e:
        print(f"خطا در تأیید نوبت: {e}")
        db.rollback()
        return False
    finally:
        db.close()


async def notify_patient_appointment_confirmed(patient_id: int, appointment_date: datetime, service: str):
    """
    ارسال پیام تأیید نوبت به بیمار
    """
    db = SessionLocal()
    try:
        alias = db.query(PatientAlias).filter_by(patient_id=patient_id, platform='telegram').first()
        if alias and alias.external_user_id:
            # فرمت تاریخ به فارسی
            date_str = appointment_date.strftime("%Y/%m/%d ساعت %H:%M")
            
            message = f"✅ *نوبت شما تأیید شد*\n\n"
            message += f"خدمت: {service}\n"
            message += f"تاریخ و ساعت: {date_str}\n\n"
            message += f"📌 لطفاً ۱۵ دقیقه قبل از نوبت حضور داشته باشید.\n"
            message += f"📞 در صورت نیاز به تغییر زمان، با کلینیک تماس بگیرید."
            
            await send_telegram_message(int(alias.external_user_id), message)
    except Exception as e:
        print(f"خطا در ارسال پیام تأیید به بیمار: {e}")
    finally:
        db.close()


async def send_reminders():
    """
    ارسال یادآوری نوبت به بیماران
    (این تابع توسط scheduler هر روز اجرا می‌شود)
    """
    print("📅 شروع ارسال یادآوری نوبت‌ها...")
    db = SessionLocal()
    now = datetime.utcnow()
    reminder_time = now + timedelta(hours=DEFAULT_REMINDER_HOURS)
    
    # نوبت‌های 24 ساعت آینده که یادآوری آنها ارسال نشده
    appointments = db.query(Appointment).filter(
        Appointment.status == 'scheduled',
        Appointment.reminder_sent == False,
        Appointment.appointment_date <= reminder_time,
        Appointment.appointment_date > now
    ).all()
    
    sent_count = 0
    for appt in appointments:
        alias = db.query(PatientAlias).filter_by(
            patient_id=appt.patient_id, 
            platform='telegram'
        ).first()
        
        if alias and alias.external_user_id:
            hours_left = int((appt.appointment_date - now).total_seconds() / 3600)
            date_str = appt.appointment_date.strftime("%Y/%m/%d ساعت %H:%M")
            
            if hours_left <= 24:
                message = f"🔔 *یادآوری نوبت*\n\n"
                message += f"خدمت: {appt.service}\n"
                message += f"تاریخ و ساعت: {date_str}\n"
                message += f"⏰ {hours_left} ساعت دیگر\n\n"
                message += f"📌 لطفاً در صورت عدم امکان حضور، با کلینیک تماس بگیرید."
                
                await send_telegram_message(int(alias.external_user_id), message)
                appt.reminder_sent = True
                sent_count += 1
                await asyncio.sleep(0.5)  # جلوگیری از rate limit
    
    db.commit()
    db.close()
    print(f"✅ {sent_count} یادآوری نوبت ارسال شد.")


async def check_no_shows():
    """
    تشخیص عدم حضور بیماران (No-Show)
    نوبت‌هایی که 2 ساعت از زمان آنها گذشته و وضعیت آنها مشخص نشده
    """
    print("🔍 بررسی نوبت‌های بدون حضور...")
    db = SessionLocal()
    now = datetime.utcnow()
    check_time = now - timedelta(hours=2)
    
    # نوبت‌های گذشته که هنوز به اتمام نرسیده‌اند
    past_appointments = db.query(Appointment).filter(
        Appointment.status == 'scheduled',
        Appointment.appointment_date <= check_time,
        Appointment.no_show == False
    ).all()
    
    no_show_count = 0
    for appt in past_appointments:
        # در نسخه واقعی، می‌توان از منشی پرسید یا خودکار علامت زد
        # فعلاً به صورت خودکار no_show می‌شوند (قابل تنظیم)
        appt.status = 'no_show'
        appt.no_show = True
        no_show_count += 1
        
        # به‌روزرسانی لید مرتبط
        lead = db.query(Lead).filter_by(id=appt.lead_id).first()
        if lead and lead.pipeline_stage == 'booked':
            lead.pipeline_stage = 'no_show'
            ph = PipelineHistory(lead_id=lead.id, stage='no_show', changed_at=datetime.utcnow())
            db.add(ph)
    
    db.commit()
    db.close()
    print(f"✅ {no_show_count} نوبت بدون حضور ثبت شد.")


def reschedule_appointment(appointment_id: int, new_date: datetime, reason: Optional[str] = None) -> bool:
    """
    تغییر زمان نوبت
    پارامترها:
        appointment_id: شناسه نوبت
        new_date: تاریخ و زمان جدید
        reason: دلیل تغییر زمان
    خروجی:
        True در صورت موفقیت، False در غیر این صورت
    """
    db = SessionLocal()
    try:
        appointment = db.query(Appointment).filter_by(id=appointment_id).first()
        if not appointment:
            print(f"نوبت {appointment_id} یافت نشد.")
            return False
        
        # ثبت تاریخ قدیمی
        old_date = appointment.appointment_date
        
        # به‌روزرسانی نوبت
        appointment.appointment_date = new_date
        appointment.reminder_sent = False  # نیاز به یادآوری مجدد
        
        # ثبت در تاریخچه (در صورت نیاز می‌توان جدول AppointmentHistory ایجاد کرد)
        
        db.commit()
        
        # ارسال پیام به بیمار (اجرای غیرهمگام)
        asyncio.create_task(
            notify_patient_reschedule(
                appointment.patient_id, 
                old_date, 
                new_date, 
                appointment.service
            )
        )
        
        return True
    except Exception as e:
        print(f"خطا در تغییر زمان نوبت: {e}")
        db.rollback()
        return False
    finally:
        db.close()


async def notify_patient_reschedule(patient_id: int, old_date: datetime, new_date: datetime, service: str):
    """
    ارسال پیام تغییر زمان نوبت به بیمار
    """
    db = SessionLocal()
    try:
        alias = db.query(PatientAlias).filter_by(patient_id=patient_id, platform='telegram').first()
        if alias and alias.external_user_id:
            old_str = old_date.strftime("%Y/%m/%d ساعت %H:%M")
            new_str = new_date.strftime("%Y/%m/%d ساعت %H:%M")
            
            message = f"🔄 *تغییر زمان نوبت*\n\n"
            message += f"خدمت: {service}\n"
            message += f"تاریخ قبلی: {old_str}\n"
            message += f"تاریخ جدید: {new_str}\n\n"
            message += f"📌 در صورت مغایرت، با کلینیک تماس بگیرید."
            
            await send_telegram_message(int(alias.external_user_id), message)
    except Exception as e:
        print(f"خطا در ارسال پیام تغییر زمان: {e}")
    finally:
        db.close()


def cancel_appointment(appointment_id: int, reason: Optional[str] = None) -> bool:
    """
    لغو نوبت
    """
    db = SessionLocal()
    try:
        appointment = db.query(Appointment).filter_by(id=appointment_id).first()
        if not appointment:
            print(f"نوبت {appointment_id} یافت نشد.")
            return False
        
        appointment.status = 'canceled'
        
        # به‌روزرسانی لید مرتبط
        lead = db.query(Lead).filter_by(id=appointment.lead_id).first()
        if lead:
            lead.pipeline_stage = 'lost'
            ph = PipelineHistory(lead_id=lead.id, stage='lost', changed_at=datetime.utcnow())
            db.add(ph)
        
        db.commit()
        
        # ارسال پیام لغو به بیمار (اجرای غیرهمگام)
        asyncio.create_task(
            notify_patient_cancellation(appointment.patient_id, appointment.service, reason)
        )
        
        return True
    except Exception as e:
        print(f"خطا در لغو نوبت: {e}")
        db.rollback()
        return False
    finally:
        db.close()


async def notify_patient_cancellation(patient_id: int, service: str, reason: Optional[str] = None):
    """
    ارسال پیام لغو نوبت به بیمار
    """
    db = SessionLocal()
    try:
        alias = db.query(PatientAlias).filter_by(patient_id=patient_id, platform='telegram').first()
        if alias and alias.external_user_id:
            message = f"❌ *لغو نوبت*\n\n"
            message += f"خدمت: {service}\n"
            if reason:
                message += f"دلیل: {reason}\n\n"
            message += f"📞 برای ثبت نوبت جدید با کلینیک تماس بگیرید."
            
            await send_telegram_message(int(alias.external_user_id), message)
    except Exception as e:
        print(f"خطا در ارسال پیام لغو نوبت: {e}")
    finally:
        db.close()


def get_upcoming_appointments(clinic_id: int, days: int = 7) -> List[Dict]:
    """
    دریافت نوبت‌های آینده کلینیک
    """
    db = SessionLocal()
    now = datetime.utcnow()
    future = now + timedelta(days=days)
    
    appointments = db.query(Appointment, Patient).join(
        Patient, Appointment.patient_id == Patient.id
    ).filter(
        Appointment.clinic_id == clinic_id,
        Appointment.status == 'scheduled',
        Appointment.appointment_date > now,
        Appointment.appointment_date <= future
    ).order_by(Appointment.appointment_date).all()
    
    result = []
    for appt, patient in appointments:
        result.append({
            'id': appt.id,
            'patient_name': patient.name,
            'service': appt.service,
            'date': appt.appointment_date.isoformat(),
            'reminder_sent': appt.reminder_sent
        })
    
    db.close()
    return result


def get_today_appointments(clinic_id: int) -> List[Dict]:
    """
    دریافت نوبت‌های امروز کلینیک
    """
    db = SessionLocal()
    now = datetime.utcnow()
    start_of_day = datetime(now.year, now.month, now.day)
    end_of_day = start_of_day + timedelta(days=1)
    
    appointments = db.query(Appointment, Patient).join(
        Patient, Appointment.patient_id == Patient.id
    ).filter(
        Appointment.clinic_id == clinic_id,
        Appointment.status == 'scheduled',
        Appointment.appointment_date >= start_of_day,
        Appointment.appointment_date < end_of_day
    ).order_by(Appointment.appointment_date).all()
    
    result = []
    for appt, patient in appointments:
        result.append({
            'id': appt.id,
            'patient_name': patient.name,
            'patient_phone': patient.phone,
            'service': appt.service,
            'time': appt.appointment_date.strftime("%H:%M")
        })
    
    db.close()
    return result


def get_appointment_by_id(appointment_id: int) -> Optional[Dict]:
    """
    دریافت اطلاعات نوبت با شناسه
    """
    db = SessionLocal()
    try:
        appt = db.query(Appointment).filter_by(id=appointment_id).first()
        if not appt:
            return None
        
        patient = db.query(Patient).filter_by(id=appt.patient_id).first()
        
        return {
            'id': appt.id,
            'patient_id': appt.patient_id,
            'patient_name': patient.name if patient else 'نامشخص',
            'service': appt.service,
            'date': appt.appointment_date.isoformat(),
            'status': appt.status,
            'reminder_sent': appt.reminder_sent,
            'no_show': appt.no_show
        }
    finally:
        db.close()
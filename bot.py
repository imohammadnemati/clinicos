"""
ClinicOS Telegram Bot – Redesigned UX
Fully compatible with existing database models (uses PatientAlias for telegram IDs).
Uses centralized Gemini client with auto model discovery and fallback.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ConversationHandler, filters, ContextTypes
)
from config import BOT_TOKEN, OWNER_TELEGRAM_ID
from database import SessionLocal, init_db
from models import Clinic, Staff, Patient, PatientAlias, Lead, Appointment, AppointmentRequest, PipelineHistory, EscalationLog
from patient_agent import process_patient_message
from appointment_engine import create_appointment_request
from scheduler import start_scheduler
from kpi_engine import get_kpi_summary
from gemini_client import get_gemini_client
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== Conversation States ==========
LANG_SELECT = 1
APPT_SERVICE, APPT_DATE, APPT_TIME, APPT_CONFIRM = range(10, 14)
STAFF_ID, STAFF_CONFIRM = range(20, 22)

# ========== Helper Functions (using PatientAlias) ==========

def get_patient_by_telegram_id(telegram_id: int, db) -> Optional[Patient]:
    """Find patient via PatientAlias."""
    alias = db.query(PatientAlias).filter_by(platform='telegram', external_user_id=str(telegram_id)).first()
    if alias:
        return db.query(Patient).filter_by(id=alias.patient_id).first()
    return None

def get_or_create_patient_by_telegram(telegram_id: int, name: str, db) -> Patient:
    """Create a new patient if not exists, using PatientAlias."""
    patient = get_patient_by_telegram_id(telegram_id, db)
    if patient:
        return patient
    clinic = db.query(Clinic).first()
    if not clinic:
        clinic = Clinic(name="Default Clinic", subdomain="default")
        db.add(clinic)
        db.commit()
    patient = Patient(clinic_id=clinic.id, name=name, first_seen=datetime.utcnow(), last_seen=datetime.utcnow())
    db.add(patient)
    db.flush()
    alias = PatientAlias(patient_id=patient.id, platform='telegram', external_user_id=str(telegram_id), confidence=0.9)
    db.add(alias)
    db.commit()
    return patient

def get_user_language(user_id: int, db) -> str:
    staff = db.query(Staff).filter_by(telegram_id=user_id).first()
    if staff and hasattr(staff, 'language') and staff.language:
        return staff.language
    patient = get_patient_by_telegram_id(user_id, db)
    if patient and patient.preferred_language:
        return patient.preferred_language
    return 'fa'

def set_user_language(user_id: int, lang: str, db):
    staff = db.query(Staff).filter_by(telegram_id=user_id).first()
    if staff:
        staff.language = lang
    else:
        patient = get_patient_by_telegram_id(user_id, db)
        if patient:
            patient.preferred_language = lang
    db.commit()

def get_user_role(user_id: int, db) -> str:
    staff = db.query(Staff).filter_by(telegram_id=user_id).first()
    if staff:
        return staff.role
    return 'patient'

def get_user_clinic_id(user_id: int, db) -> int:
    staff = db.query(Staff).filter_by(telegram_id=user_id).first()
    if staff:
        return staff.clinic_id
    patient = get_patient_by_telegram_id(user_id, db)
    if patient and patient.clinic_id:
        return patient.clinic_id
    clinic = db.query(Clinic).first()
    if not clinic:
        clinic = Clinic(name="Default Clinic", subdomain="default")
        db.add(clinic)
        db.commit()
    return clinic.id

def get_main_keyboard(role: str):
    if role == 'owner':
        buttons = [['📊 Dashboard', '👥 Staff'], ['🏥 Clinic', '⚙️ Settings'], ['💰 Revenue', '📈 Reports']]
    elif role == 'doctor':
        buttons = [['📅 Today', '👥 Patients'], ['🚨 Escalations', '📊 Performance']]
    elif role == 'secretary':
        buttons = [['📅 Appointments', '👥 Patients'], ['🔥 Leads', '🔔 Notifications'], ['📊 Statistics', '👩‍💼 Handoff']]
    else:
        buttons = [['🏠 Home', '📅 Book Appointment'], ['💬 Ask Clinic', '📋 Services'], ['👩‍💼 Human Receptionist', '📄 My Appointments']]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def format_dashboard(role: str, clinic_id: int, db, user_id: int) -> str:
    if role == 'owner':
        summary = get_kpi_summary(clinic_id)
        today = summary['today']
        return (f"📊 *Owner Dashboard*\n\n"
                f"📅 *Today*: {today['leads']} leads | {today['booked']} booked | 💰 {today['revenue']:,}")
    elif role == 'secretary':
        today = datetime.utcnow().date()
        start = datetime(today.year, today.month, today.day)
        from models import RawMessage
        messages = db.query(RawMessage).filter(RawMessage.created_at >= start).count()
        leads = db.query(Lead).filter(Lead.created_at >= start).count()
        appts = db.query(Appointment).filter(Appointment.appointment_date >= start).count()
        esc = db.query(EscalationLog).filter(EscalationLog.created_at >= start).count()
        return (f"📋 *Secretary Dashboard*\n\n"
                f"✉️ Messages: {messages}\n"
                f"🔥 Leads: {leads}\n"
                f"📅 Appointments: {appts}\n"
                f"🚨 Escalations: {esc}")
    elif role == 'doctor':
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        pending = db.query(EscalationLog).filter(
            EscalationLog.created_at >= today_start, EscalationLog.escalated_to == 'doctor'
        ).count()
        return f"👨‍⚕️ *Doctor Dashboard*\n\n🚨 Pending escalations: {pending}"
    else:
        patient = get_patient_by_telegram_id(user_id, db)
        name = patient.name if patient else "عزیز"
        return f"🏠 *Home*\n\nسلام {name} 🌷\nبه کلینیک خوش آمدید."

# ========== Conversation Handlers ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        lang = get_user_language(user_id, db)
        if lang:
            role = get_user_role(user_id, db)
            clinic_id = get_user_clinic_id(user_id, db)
            await send_main_menu(update, context, role, clinic_id, db, user_id)
            return
    finally:
        db.close()

    keyboard = [
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇦🇿 Azərbaycan", callback_data="lang_az")],
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")]
    ]
    await update.message.reply_text("🌐 لطفاً زبان خود را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))
    return LANG_SELECT

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = query.data.split('_')[1]
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        set_user_language(user_id, lang_code, db)
        role = get_user_role(user_id, db)
        clinic_id = get_user_clinic_id(user_id, db)
        welcome = {
            'fa': "🎉 خوش آمدید! زبان شما ثبت شد.",
            'en': "🎉 Welcome! Your language has been saved.",
            'az': "🎉 Xoş gəldiniz! Diliniz qeyd edildi.",
            'ar': "🎉 مرحباً! تم حفظ لغتك."
        }.get(lang_code, "Welcome!")
        await query.edit_message_text(welcome)
        await send_main_menu(update, context, role, clinic_id, db, user_id)
    finally:
        db.close()
    return ConversationHandler.END

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, role: str, clinic_id: int, db, user_id: int):
    text = format_dashboard(role, clinic_id, db, user_id)
    keyboard = get_main_keyboard(role)
    await update.effective_message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        role = get_user_role(user_id, db)
        clinic_id = get_user_clinic_id(user_id, db)
        lang = get_user_language(user_id, db)

        if text in ('📊 Dashboard', '🏠 Home'):
            await send_main_menu(update, context, role, clinic_id, db, user_id)
        elif text == '📅 Book Appointment':
            await start_appointment_booking(update, context, clinic_id)
        elif text in ('👩‍💼 Human Receptionist', '👩‍💼 Handoff'):
            await human_handoff(update, context, clinic_id)
        elif text == '👥 Staff' and role == 'owner':
            await show_staff_menu(update, context, clinic_id)
        elif text == '🔥 Leads' and role in ('secretary', 'owner'):
            await show_leads(update, context, clinic_id)
        elif text == '📅 Today' and role == 'doctor':
            await show_doctor_today(update, context, clinic_id)
        elif text == '🚨 Escalations' and role == 'doctor':
            await show_doctor_escalations(update, context, clinic_id)
        elif text == '📊 Statistics' and role == 'secretary':
            await show_secretary_stats(update, context, clinic_id)
        elif text == '📋 Staff List' and role == 'owner':
            await show_staff_list(update, context, clinic_id)
        elif text == '📅 Appointments' and role in ('secretary', 'doctor'):
            await show_appointments(update, context, clinic_id, role)
        elif text == '📄 My Appointments' and role == 'patient':
            await show_patient_appointments(update, context)
        elif text == '💬 Ask Clinic' and role == 'patient':
            await process_patient_message(update, None, clinic_id, "telegram", str(user_id), text, db=db)
        else:
            if role == 'patient':
                await process_patient_message(update, None, clinic_id, "telegram", str(user_id), text, db=db)
            else:
                await update.message.reply_text("❓ Unknown command. Use the menu.")
    finally:
        db.close()

# ========== Appointment Wizard ==========
async def start_appointment_booking(update: Update, context: ContextTypes.DEFAULT_TYPE, clinic_id: int):
    keyboard = [
        [InlineKeyboardButton("بوتاکس", callback_data="appt_service_botox")],
        [InlineKeyboardButton("فیلر", callback_data="appt_service_filler")],
        [InlineKeyboardButton("لیزر", callback_data="appt_service_laser")],
        [InlineKeyboardButton("مزوتراپی", callback_data="appt_service_mesotherapy")],
        [InlineKeyboardButton("جراحی", callback_data="appt_service_surgery")],
        [InlineKeyboardButton("❌ انصراف", callback_data="appt_cancel")]
    ]
    await update.message.reply_text("📅 لطفاً خدمت مورد نظر را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))
    return APPT_SERVICE

async def appointment_service_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "appt_cancel":
        await query.edit_message_text("❌ درخواست نوبت لغو شد.")
        return ConversationHandler.END
    service = data.split('_')[-1]
    context.user_data['booking_service'] = service
    await query.edit_message_text(f"خدمت: {service}\nلطفاً تاریخ مورد نظر را وارد کنید (مثال: 2025-06-15):")
    return APPT_DATE

async def appointment_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_str = update.message.text.strip()
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        context.user_data['booking_date'] = date_str
        await update.message.reply_text("لطفاً ساعت مورد نظر را وارد کنید (مثال: 15:30):")
        return APPT_TIME
    except ValueError:
        await update.message.reply_text("❌ فرمت تاریخ اشتباه. لطفاً به صورت YYYY-MM-DD وارد کنید:")
        return APPT_DATE

async def appointment_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_str = update.message.text.strip()
    import re
    if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', time_str):
        await update.message.reply_text("❌ فرمت ساعت اشتباه. مثال: 15:30")
        return APPT_TIME
    context.user_data['booking_time'] = time_str
    service = context.user_data['booking_service']
    date = context.user_data['booking_date']
    confirm_text = f"✅ تأیید نوبت:\nخدمت: {service}\nتاریخ: {date}\nساعت: {time_str}\nآیا اطلاعات صحیح است؟"
    keyboard = [[InlineKeyboardButton("✅ بله", callback_data="appt_confirm_yes")],
                [InlineKeyboardButton("❌ خیر", callback_data="appt_confirm_no")]]
    await update.message.reply_text(confirm_text, reply_markup=InlineKeyboardMarkup(keyboard))
    return APPT_CONFIRM

async def appointment_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "appt_confirm_no":
        await query.edit_message_text("❌ درخواست نوبت لغو شد.")
        return ConversationHandler.END
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        clinic_id = get_user_clinic_id(user_id, db)
        patient = get_patient_by_telegram_id(user_id, db)
        if not patient:
            patient = get_or_create_patient_by_telegram(user_id, update.effective_user.full_name, db)
        service = context.user_data['booking_service']
        date_str = context.user_data['booking_date']
        time_str = context.user_data['booking_time']
        suggested_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        lead = db.query(Lead).filter_by(patient_id=patient.id, pipeline_stage='new').first()
        if not lead:
            lead = Lead(clinic_id=clinic_id, patient_id=patient.id, service=service, lead_score=5.0, pipeline_stage='new')
            db.add(lead)
            db.commit()
        request_id = create_appointment_request(lead.id, suggested_datetime)
        await query.edit_message_text(f"✅ درخواست نوبت شما با شماره {request_id} ثبت شد. منشی‌ها به زودی تأیید خواهند کرد.")
    except Exception as e:
        logger.error(f"Booking error: {e}")
        await query.edit_message_text("❌ خطا در ثبت نوبت.")
    finally:
        db.close()
    return ConversationHandler.END

# ========== Human Handoff ==========
async def human_handoff(update: Update, context: ContextTypes.DEFAULT_TYPE, clinic_id: int):
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        patient = get_patient_by_telegram_id(user_id, db)
        if not patient:
            await update.message.reply_text("لطفاً ابتدا با ارسال /start ثبت‌نام کنید.")
            return
        escalation = EscalationLog(
            clinic_id=clinic_id, patient_id=patient.id, reason="human_request",
            trigger="button", escalated_to="secretary", created_at=datetime.utcnow()
        )
        db.add(escalation)
        db.commit()
        secretaries = db.query(Staff).filter_by(clinic_id=clinic_id, role='secretary').all()
        for sec in secretaries:
            await context.bot.send_message(
                chat_id=sec.telegram_id,
                text=f"🚨 درخواست جدید برای صحبت با منشی از بیمار {patient.name or patient.id}"
            )
        await update.message.reply_text("👩‍💼 درخواست شما به منشی منتقل شد. به زودی پاسخ خواهید گرفت.")
    finally:
        db.close()

# ========== Staff Management ==========
async def show_staff_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, clinic_id: int):
    keyboard = [
        [InlineKeyboardButton("➕ Add Doctor", callback_data="staff_add_doctor")],
        [InlineKeyboardButton("➕ Add Secretary", callback_data="staff_add_secretary")],
        [InlineKeyboardButton("➕ Add Admin", callback_data="staff_add_admin")],
        [InlineKeyboardButton("📋 Staff List", callback_data="staff_list")],
        [InlineKeyboardButton("🗑 Remove Staff", callback_data="staff_remove")],
        [InlineKeyboardButton("🔙 Back", callback_data="staff_back")]
    ]
    await update.message.reply_text("👥 Staff Management", reply_markup=InlineKeyboardMarkup(keyboard))

async def staff_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "staff_back":
        await query.edit_message_text("Returning...")
        user_id = update.effective_user.id
        db = SessionLocal()
        try:
            role = get_user_role(user_id, db)
            clinic_id = get_user_clinic_id(user_id, db)
            await send_main_menu(update, context, role, clinic_id, db, user_id)
        finally:
            db.close()
        return
    if data.startswith("staff_add"):
        role = data.split('_')[2]
        context.user_data['new_staff_role'] = role
        await query.edit_message_text(f"لطفاً شناسه تلگرام (Telegram ID) {role} جدید را وارد کنید:")
        return STAFF_ID
    elif data == "staff_list":
        await show_staff_list(update, context, None)
    elif data == "staff_remove":
        await show_remove_staff(update, context, None)

async def add_staff_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_id = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ شناسه باید عدد باشد. دوباره وارد کنید:")
        return STAFF_ID
    context.user_data['new_staff_id'] = new_id
    await update.message.reply_text(f"آیا از اضافه کردن کاربر {new_id} با نقش {context.user_data['new_staff_role']} مطمئن هستید؟ (بله/خیر)")
    return STAFF_CONFIRM

async def add_staff_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() not in ['بله', 'yes']:
        await update.message.reply_text("❌ عملیات لغو شد.")
        return ConversationHandler.END
    db = SessionLocal()
    try:
        clinic_id = get_user_clinic_id(update.effective_user.id, db)
        role = context.user_data['new_staff_role']
        new_id = context.user_data['new_staff_id']
        if db.query(Staff).filter_by(telegram_id=new_id).first():
            await update.message.reply_text("❌ کاربر قبلاً ثبت شده است.")
            return ConversationHandler.END
        new_staff = Staff(clinic_id=clinic_id, telegram_id=new_id, name=f"کاربر {new_id}", role=role, created_at=datetime.utcnow())
        db.add(new_staff)
        db.commit()
        await update.message.reply_text(f"✅ کاربر {new_id} با نقش {role} اضافه شد.")
    except Exception as e:
        logger.error(f"Add staff error: {e}")
        await update.message.reply_text("❌ خطا در اضافه کردن کاربر.")
    finally:
        db.close()
    return ConversationHandler.END

async def show_staff_list(update: Update, context: ContextTypes.DEFAULT_TYPE, clinic_id: int):
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        if clinic_id is None:
            clinic_id = get_user_clinic_id(user_id, db)
        staff = db.query(Staff).filter_by(clinic_id=clinic_id).all()
        if not staff:
            await update.message.reply_text("هیچ کارمندی ثبت نشده است.")
        else:
            msg = "📋 *لیست کارمندان*\n\n"
            for s in staff:
                msg += f"🆔 {s.telegram_id} – {s.name} ({s.role})\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
    finally:
        db.close()

async def show_remove_staff(update: Update, context: ContextTypes.DEFAULT_TYPE, clinic_id: int):
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        if clinic_id is None:
            clinic_id = get_user_clinic_id(user_id, db)
        staff = db.query(Staff).filter_by(clinic_id=clinic_id).all()
        if not staff:
            await update.message.reply_text("هیچ کارمندی برای حذف وجود ندارد.")
            return
        keyboard = [[InlineKeyboardButton(f"{s.name} ({s.role})", callback_data=f"remove_staff_{s.id}")] for s in staff]
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="staff_back")])
        await update.message.reply_text("کارمند مورد نظر برای حذف را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))
    finally:
        db.close()

async def remove_staff_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "staff_back":
        await query.edit_message_text("بازگشت...")
        user_id = update.effective_user.id
        db = SessionLocal()
        try:
            role = get_user_role(user_id, db)
            clinic_id = get_user_clinic_id(user_id, db)
            await send_main_menu(update, context, role, clinic_id, db, user_id)
        finally:
            db.close()
        return
    staff_id = int(data.split('_')[2])
    db = SessionLocal()
    try:
        staff = db.query(Staff).filter_by(id=staff_id).first()
        if staff:
            db.delete(staff)
            db.commit()
            await query.edit_message_text(f"✅ کارمند {staff.name} حذف شد.")
        else:
            await query.edit_message_text("❌ کارمند یافت نشد.")
    finally:
        db.close()

# ========== Other Feature Handlers ==========
async def show_leads(update: Update, context: ContextTypes.DEFAULT_TYPE, clinic_id: int):
    db = SessionLocal()
    try:
        leads = db.query(Lead).filter_by(clinic_id=clinic_id, pipeline_stage='new').order_by(Lead.lead_score.desc()).limit(20).all()
        if not leads:
            await update.message.reply_text("هیچ لید جدیدی وجود ندارد.")
        else:
            msg = "🔥 *لیدهای جدید*\n\n"
            for l in leads:
                patient = db.query(Patient).filter_by(id=l.patient_id).first()
                msg += f"• {patient.name if patient else 'ناشناس'} – {l.service} – امتیاز: {l.lead_score}\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
    finally:
        db.close()

async def show_doctor_today(update: Update, context: ContextTypes.DEFAULT_TYPE, clinic_id: int):
    db = SessionLocal()
    try:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        appointments = db.query(Appointment).filter(
            Appointment.clinic_id == clinic_id,
            Appointment.appointment_date >= today_start,
            Appointment.appointment_date < today_start + timedelta(days=1)
        ).all()
        if not appointments:
            await update.message.reply_text("📅 امروز نوبتی ندارید.")
        else:
            msg = "📅 *نوبت‌های امروز*\n\n"
            for a in appointments:
                patient = db.query(Patient).filter_by(id=a.patient_id).first()
                msg += f"• {patient.name if patient else 'بیمار'} – {a.service} – {a.appointment_date.strftime('%H:%M')}\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
    finally:
        db.close()

async def show_doctor_escalations(update: Update, context: ContextTypes.DEFAULT_TYPE, clinic_id: int):
    db = SessionLocal()
    try:
        escalations = db.query(EscalationLog).filter_by(clinic_id=clinic_id, escalated_to='doctor').order_by(EscalationLog.created_at.desc()).limit(10).all()
        if not escalations:
            await update.message.reply_text("✅ هیچ مورد ارجاعی وجود ندارد.")
        else:
            msg = "🚨 *موارد ارجاع به پزشک*\n\n"
            for e in escalations:
                patient = db.query(Patient).filter_by(id=e.patient_id).first()
                msg += f"• بیمار: {patient.name if patient else e.patient_id}\n  دلیل: {e.reason}\n  زمان: {e.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
    finally:
        db.close()

async def show_secretary_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, clinic_id: int):
    db = SessionLocal()
    try:
        today = datetime.utcnow().date()
        start = datetime(today.year, today.month, today.day)
        from models import RawMessage
        messages = db.query(RawMessage).filter(RawMessage.created_at >= start).count()
        leads = db.query(Lead).filter(Lead.created_at >= start).count()
        appointments = db.query(Appointment).filter(Appointment.appointment_date >= start).count()
        await update.message.reply_text(
            f"📊 *آمار امروز*\n\n✉️ پیام‌ها: {messages}\n🔥 لیدها: {leads}\n📅 نوبت‌ها: {appointments}",
            parse_mode='Markdown'
        )
    finally:
        db.close()

async def show_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE, clinic_id: int, role: str):
    db = SessionLocal()
    try:
        today = datetime.utcnow()
        appointments = db.query(Appointment).filter(
            Appointment.clinic_id == clinic_id, Appointment.appointment_date >= today
        ).order_by(Appointment.appointment_date).limit(20).all()
        if not appointments:
            await update.message.reply_text("📅 هیچ نوبتی یافت نشد.")
        else:
            msg = "📅 *لیست نوبت‌ها*\n\n"
            for a in appointments:
                patient = db.query(Patient).filter_by(id=a.patient_id).first()
                msg += f"• {patient.name if patient else 'بیمار'} – {a.service} – {a.appointment_date.strftime('%Y-%m-%d %H:%M')}\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
    finally:
        db.close()

async def show_patient_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        patient = get_patient_by_telegram_id(user_id, db)
        if not patient:
            await update.message.reply_text("لطفاً ابتدا /start را بزنید.")
            return
        appointments = db.query(Appointment).filter_by(patient_id=patient.id).order_by(Appointment.appointment_date.desc()).limit(10).all()
        if not appointments:
            await update.message.reply_text("📄 شما هیچ نوبتی ثبت نکرده‌اید.")
        else:
            msg = "📄 *نوبت‌های شما*\n\n"
            for a in appointments:
                msg += f"• {a.service} – {a.appointment_date.strftime('%Y-%m-%d %H:%M')} – {a.status}\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
    finally:
        db.close()

# ========== Gemini Test Command ==========
async def test_gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور تست اتصال به Gemini"""
    try:
        client = get_gemini_client()
        result = client.test_connection()
        if result:
            await update.message.reply_text("✅ تست Gemini: موفق\nمدل فعال: " + client.working_model)
        else:
            await update.message.reply_text("❌ تست Gemini: ناموفق. لطفاً لاگ‌ها را بررسی کنید.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در تست Gemini: {str(e)}")

# ========== Error Handler ==========
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}", exc_info=context.error)
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ خطای داخلی. لطفاً دقایقی دیگر تلاش کنید.")

# ========== Gemini Startup Diagnostic ==========
def diagnose_gemini():
    """بررسی اتصال Gemini در زمان راه‌اندازی"""
    try:
        client = get_gemini_client()
        logger.info(f"Gemini model selected: {client.working_model}")
        if client.test_connection():
            logger.info("Gemini connection test: SUCCESS")
        else:
            logger.error("Gemini connection test: FAILED")
    except Exception as e:
        logger.error(f"Gemini initialization failed: {e}")

# ========== Main Application ==========
def main():
    init_db()

    # حذف وب‌هوک قدیمی (در صورت وجود) برای جلوگیری از Conflict
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        logger.info("Webhook deleted.")
    except Exception as e:
        logger.warning(f"Could not delete webhook: {e}")

    # راه‌اندازی تشخیص Gemini
    diagnose_gemini()

    app = Application.builder().token(BOT_TOKEN).build()

    # ثبت هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test_gemini", test_gemini))
    app.add_handler(CallbackQueryHandler(language_callback, pattern='^lang_'))
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(staff_menu_callback, pattern='^staff_add_')],
        states={STAFF_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_staff_id)],
                STAFF_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_staff_confirm)]},
        fallbacks=[],
    ))
    app.add_handler(CallbackQueryHandler(staff_menu_callback, pattern='^staff_'))
    app.add_handler(CallbackQueryHandler(remove_staff_callback, pattern='^remove_staff_'))
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^📅 Book Appointment$'), start_appointment_booking)],
        states={
            APPT_SERVICE: [CallbackQueryHandler(appointment_service_callback, pattern='^appt_')],
            APPT_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, appointment_date)],
            APPT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, appointment_time)],
            APPT_CONFIRM: [CallbackQueryHandler(appointment_confirm_callback, pattern='^appt_confirm_')],
        },
        fallbacks=[CommandHandler('cancel', lambda u,c: u.message.reply_text("Cancelled"))],
    ))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler))
    app.add_error_handler(error_handler)

    start_scheduler()
    logger.info("🚀 ClinicOS bot started with full UX redesign and Gemini integration")
    app.run_polling()

if __name__ == "__main__":
    main()

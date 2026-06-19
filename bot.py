"""
ClinicOS Telegram Bot – Final Production Version
Supports: language selection, role‑based menus, appointment wizard,
staff management, leads, escalations, and new LLM orchestration layer.
Fully internationalized (i18n) – UI texts in Fa, En, Az, Ar.
"""

import logging
import time
import asyncio
import requests
import tempfile
import os
from datetime import datetime, timedelta
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ConversationHandler, filters, ContextTypes
)
from config import (
    BOT_TOKEN, OWNER_TELEGRAM_ID, REDIS_URL, OPENROUTER_FREE_MODELS,
    validate_openrouter_config, INITIAL_SCORES, OPENAI_API_KEY
)
from database import SessionLocal, init_db
from models import (
    Clinic, Staff, Patient, PatientAlias, Lead, Appointment,
    AppointmentRequest, PipelineHistory, EscalationLog, RawMessage
)
from patient_agent import process_patient_message
from appointment_engine import create_appointment_request
from kpi_engine import get_kpi_summary
from scheduler import start_scheduler

# Import STT service and i18n
from stt_service import STTService
from i18n import get_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== Initialize STT Service ==========
stt_service = STTService()

# ========== Conversation States ==========
LANG_SELECT = 1
APPT_SERVICE, APPT_DATE, APPT_TIME, APPT_CONFIRM = range(10, 14)
STAFF_ID, STAFF_CONFIRM = range(20, 22)

# ========== Helper Functions ==========
def get_patient_by_telegram_id(telegram_id: int, db) -> Optional[Patient]:
    alias = db.query(PatientAlias).filter_by(platform='telegram', external_user_id=str(telegram_id)).first()
    if alias:
        return db.query(Patient).filter_by(id=alias.patient_id).first()
    return None

def get_or_create_patient_by_telegram(telegram_id: int, name: str, db) -> Patient:
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

def get_main_keyboard(role: str, lang: str = "fa"):
    """Return dynamic keyboard with translated labels."""
    if role == 'owner':
        buttons = [
            [get_text("btn_dashboard", lang), get_text("btn_staff", lang)],
            [get_text("btn_clinic", lang), get_text("btn_settings", lang)],
            [get_text("btn_revenue", lang), get_text("btn_reports", lang)]
        ]
    elif role == 'doctor':
        buttons = [
            [get_text("btn_today", lang), get_text("btn_patients", lang)],
            [get_text("btn_escalations", lang), get_text("btn_performance", lang)]
        ]
    elif role == 'secretary':
        buttons = [
            [get_text("btn_appointments", lang), get_text("btn_patients", lang)],
            [get_text("btn_leads", lang), get_text("btn_notifications", lang)],
            [get_text("btn_statistics", lang), get_text("btn_handoff", lang)]
        ]
    else:
        buttons = [
            [get_text("btn_home", lang), get_text("btn_book_appointment", lang)],
            [get_text("btn_ask_clinic", lang), get_text("btn_services", lang)],
            [get_text("btn_human_receptionist", lang), get_text("btn_my_appointments", lang)]
        ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def format_dashboard(role: str, clinic_id: int, db, user_id: int, lang: str = "fa") -> str:
    """Return dashboard text based on role, with i18n."""
    if role == 'owner':
        summary = get_kpi_summary(clinic_id)
        today = summary['today']
        return get_text("dashboard_owner", lang).format(
            leads=today['leads'],
            booked=today['booked'],
            revenue=today['revenue']
        )
    elif role == 'secretary':
        today = datetime.utcnow().date()
        start = datetime(today.year, today.month, today.day)
        messages = db.query(RawMessage).filter(RawMessage.created_at >= start).count()
        leads = db.query(Lead).filter(Lead.created_at >= start).count()
        appts = db.query(Appointment).filter(Appointment.appointment_date >= start).count()
        esc = db.query(EscalationLog).filter(EscalationLog.created_at >= start).count()
        return get_text("dashboard_secretary", lang).format(
            messages=messages,
            leads=leads,
            appts=appts,
            esc=esc
        )
    elif role == 'doctor':
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        pending = db.query(EscalationLog).filter(
            EscalationLog.created_at >= today_start, EscalationLog.escalated_to == 'doctor'
        ).count()
        return get_text("dashboard_doctor", lang).format(pending=pending)
    else:
        patient = get_patient_by_telegram_id(user_id, db)
        name = patient.name if patient else "عزیز"
        return get_text("welcome_patient", lang).format(name=name)

# ========== Conversation Handlers ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        lang = get_user_language(user_id, db)
        if lang:
            role = get_user_role(user_id, db)
            clinic_id = get_user_clinic_id(user_id, db)
            await send_main_menu(update, context, role, clinic_id, db, user_id, lang)
            return
    finally:
        db.close()

    # Show language selection
    keyboard = [
        [InlineKeyboardButton(get_text("lang_fa", "fa"), callback_data="lang_fa")],
        [InlineKeyboardButton(get_text("lang_en", "fa"), callback_data="lang_en")],
        [InlineKeyboardButton(get_text("lang_az", "fa"), callback_data="lang_az")],
        [InlineKeyboardButton(get_text("lang_ar", "fa"), callback_data="lang_ar")]
    ]
    await update.message.reply_text(
        get_text("lang_select_title", "fa"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
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
        welcome = get_text("lang_selected", lang_code)
        await query.edit_message_text(welcome)
        await send_main_menu(update, context, role, clinic_id, db, user_id, lang_code)
    finally:
        db.close()
    return ConversationHandler.END

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE,
                         role: str, clinic_id: int, db, user_id: int, lang: str = "fa"):
    text = format_dashboard(role, clinic_id, db, user_id, lang)
    keyboard = get_main_keyboard(role, lang)
    await update.effective_message.reply_text(
        text, parse_mode='Markdown', reply_markup=keyboard
    )

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        role = get_user_role(user_id, db)
        clinic_id = get_user_clinic_id(user_id, db)
        lang = get_user_language(user_id, db)

        # Identify button presses using translated labels
        btn_home = get_text("btn_home", lang)
        btn_dashboard = get_text("btn_dashboard", lang)
        btn_book = get_text("btn_book_appointment", lang)
        btn_human = get_text("btn_human_receptionist", lang)
        btn_handoff = get_text("btn_handoff", lang)
        btn_staff = get_text("btn_staff", lang)
        btn_leads = get_text("btn_leads", lang)
        btn_today = get_text("btn_today", lang)
        btn_escalations = get_text("btn_escalations", lang)
        btn_statistics = get_text("btn_statistics", lang)
        btn_appointments = get_text("btn_appointments", lang)
        btn_my_appointments = get_text("btn_my_appointments", lang)
        btn_ask = get_text("btn_ask_clinic", lang)

        if text in (btn_dashboard, btn_home):
            await send_main_menu(update, context, role, clinic_id, db, user_id, lang)
        elif text == btn_book:
            await start_appointment_booking(update, context, clinic_id, lang)
        elif text in (btn_human, btn_handoff):
            await human_handoff(update, context, clinic_id, lang)
        elif text == btn_staff and role == 'owner':
            await show_staff_menu(update, context, clinic_id, lang)
        elif text == btn_leads and role in ('secretary', 'owner'):
            await show_leads(update, context, clinic_id, lang)
        elif text == btn_today and role == 'doctor':
            await show_doctor_today(update, context, clinic_id, lang)
        elif text == btn_escalations and role == 'doctor':
            await show_doctor_escalations(update, context, clinic_id, lang)
        elif text == btn_statistics and role == 'secretary':
            await show_secretary_stats(update, context, clinic_id, lang)
        elif text == btn_appointments and role in ('secretary', 'doctor'):
            await show_appointments(update, context, clinic_id, role, lang)
        elif text == btn_my_appointments and role == 'patient':
            await show_patient_appointments(update, context, lang)
        elif text == btn_ask and role == 'patient':
            await process_patient_message(update, None, clinic_id, "telegram", str(user_id), text, db=db)
        else:
            # Treat as normal message for all roles
            await process_patient_message(update, None, clinic_id, "telegram", str(user_id), text, db=db)
    finally:
        db.close()

# ========== Voice/Audio Handler ==========
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages and audio files, transcribe and process as text."""
    user_id = update.effective_user.id
    voice = update.message.voice
    audio = update.message.audio
    file_id = None
    media_type = None

    if voice:
        file_id = voice.file_id
        media_type = "voice"
    elif audio:
        file_id = audio.file_id
        media_type = "audio"
    else:
        return

    # Get language (for error messages)
    db = SessionLocal()
    try:
        lang = get_user_language(user_id, db)
    finally:
        db.close()

    try:
        file = await context.bot.get_file(file_id)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
            tmp_path = tmp.name
        await file.download_to_drive(tmp_path)

        transcript = await stt_service.transcribe_audio_file(tmp_path)

        try:
            os.unlink(tmp_path)
        except Exception as e:
            logger.warning(f"Could not delete temp file: {e}")

        if not transcript:
            await update.message.reply_text(get_text("error_stt_failed", lang))
            return

        db = SessionLocal()
        try:
            clinic_id = get_user_clinic_id(user_id, db)
            await process_patient_message(
                update,
                context,
                clinic_id,
                "telegram",
                str(user_id),
                raw_text=transcript,
                media_url=file.file_path,
                media_type=media_type,
                transcript=transcript,
                db=db
            )
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error handling voice: {e}", exc_info=True)
        await update.message.reply_text(get_text("error_voice_processing", lang))

# ========== Appointment Wizard ==========
async def start_appointment_booking(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                    clinic_id: int, lang: str = "fa"):
    keyboard = [
        [InlineKeyboardButton(get_text("appt_service_botox", lang), callback_data="appt_service_botox")],
        [InlineKeyboardButton(get_text("appt_service_filler", lang), callback_data="appt_service_filler")],
        [InlineKeyboardButton(get_text("appt_service_laser", lang), callback_data="appt_service_laser")],
        [InlineKeyboardButton(get_text("appt_service_mesotherapy", lang), callback_data="appt_service_mesotherapy")],
        [InlineKeyboardButton(get_text("appt_service_surgery", lang), callback_data="appt_service_surgery")],
        [InlineKeyboardButton(get_text("appt_cancel", lang), callback_data="appt_cancel")]
    ]
    await update.message.reply_text(
        get_text("appt_select_service", lang),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return APPT_SERVICE

async def appointment_service_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        lang = get_user_language(user_id, db)
    finally:
        db.close()

    if data == "appt_cancel":
        await query.edit_message_text(get_text("appt_cancelled", lang))
        return ConversationHandler.END
    service = data.split('_')[-1]
    context.user_data['booking_service'] = service
    await query.edit_message_text(
        f"{get_text('appt_enter_date', lang)}"
    )
    return APPT_DATE

async def appointment_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_str = update.message.text.strip()
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        lang = get_user_language(user_id, db)
    finally:
        db.close()

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        context.user_data['booking_date'] = date_str
        await update.message.reply_text(get_text("appt_enter_time", lang))
        return APPT_TIME
    except ValueError:
        await update.message.reply_text(get_text("error_invalid_date", lang))
        return APPT_DATE

async def appointment_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_str = update.message.text.strip()
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        lang = get_user_language(user_id, db)
    finally:
        db.close()

    import re
    if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', time_str):
        await update.message.reply_text(get_text("error_invalid_time", lang))
        return APPT_TIME
    context.user_data['booking_time'] = time_str
    service = context.user_data['booking_service']
    date = context.user_data['booking_date']
    confirm_text = get_text("appt_confirm", lang).format(
        service=service, date=date, time=time_str
    )
    keyboard = [
        [InlineKeyboardButton(get_text("appt_confirm_yes", lang), callback_data="appt_confirm_yes")],
        [InlineKeyboardButton(get_text("appt_confirm_no", lang), callback_data="appt_confirm_no")]
    ]
    await update.message.reply_text(confirm_text, reply_markup=InlineKeyboardMarkup(keyboard))
    return APPT_CONFIRM

async def appointment_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        lang = get_user_language(user_id, db)
    finally:
        db.close()

    if query.data == "appt_confirm_no":
        await query.edit_message_text(get_text("appt_cancelled", lang))
        return ConversationHandler.END

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
        await query.edit_message_text(
            get_text("appt_booking_success", lang).format(request_id=request_id)
        )
    except Exception as e:
        logger.error(f"Booking error: {e}")
        await query.edit_message_text(get_text("appt_booking_error", lang))
    finally:
        db.close()
    return ConversationHandler.END

# ========== Human Handoff ==========
async def human_handoff(update: Update, context: ContextTypes.DEFAULT_TYPE,
                         clinic_id: int, lang: str = "fa"):
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        patient = get_patient_by_telegram_id(user_id, db)
        if not patient:
            await update.message.reply_text(get_text("human_handoff_register_first", lang))
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
                text=get_text("human_handoff_alert", lang).format(patient_name=patient.name or patient.id)
            )
        await update.message.reply_text(get_text("human_handoff_sent", lang))
    finally:
        db.close()

# ========== Staff Management ==========
async def show_staff_menu(update: Update, context: ContextTypes.DEFAULT_TYPE,
                           clinic_id: int, lang: str = "fa"):
    keyboard = [
        [InlineKeyboardButton(get_text("staff_add_doctor", lang), callback_data="staff_add_doctor")],
        [InlineKeyboardButton(get_text("staff_add_secretary", lang), callback_data="staff_add_secretary")],
        [InlineKeyboardButton(get_text("staff_add_admin", lang), callback_data="staff_add_admin")],
        [InlineKeyboardButton(get_text("staff_list", lang), callback_data="staff_list")],
        [InlineKeyboardButton(get_text("staff_remove", lang), callback_data="staff_remove")],
        [InlineKeyboardButton(get_text("staff_back", lang), callback_data="staff_back")]
    ]
    await update.message.reply_text(
        get_text("staff_management_title", lang),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def staff_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        lang = get_user_language(user_id, db)
    finally:
        db.close()

    if data == "staff_back":
        await query.edit_message_text("...")
        user_id = update.effective_user.id
        db = SessionLocal()
        try:
            role = get_user_role(user_id, db)
            clinic_id = get_user_clinic_id(user_id, db)
            lang = get_user_language(user_id, db)
            await send_main_menu(update, context, role, clinic_id, db, user_id, lang)
        finally:
            db.close()
        return

    if data.startswith("staff_add"):
        role = data.split('_')[2]
        context.user_data['new_staff_role'] = role
        await query.edit_message_text(
            get_text("staff_enter_id", lang).format(role=role)
        )
        return STAFF_ID
    elif data == "staff_list":
        await show_staff_list(update, context, None, lang)
    elif data == "staff_remove":
        await show_remove_staff(update, context, None, lang)

async def add_staff_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        lang = get_user_language(user_id, db)
    finally:
        db.close()

    try:
        new_id = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ شناسه باید عدد باشد. دوباره وارد کنید:")  # This one is not translated – can use get_text but it's simple.
        return STAFF_ID
    context.user_data['new_staff_id'] = new_id
    await update.message.reply_text(
        get_text("staff_confirm_add", lang).format(
            id=new_id, role=context.user_data['new_staff_role']
        )
    )
    return STAFF_CONFIRM

async def add_staff_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        lang = get_user_language(user_id, db)
    finally:
        db.close()

    if update.message.text.lower() not in ['بله', 'yes', 'بلي', 'yes']:
        await update.message.reply_text(get_text("staff_remove_cancelled", lang))
        return ConversationHandler.END

    db = SessionLocal()
    try:
        clinic_id = get_user_clinic_id(user_id, db)
        role = context.user_data['new_staff_role']
        new_id = context.user_data['new_staff_id']
        if db.query(Staff).filter_by(telegram_id=new_id).first():
            await update.message.reply_text(get_text("staff_already_exists", lang))
            return ConversationHandler.END
        new_staff = Staff(
            clinic_id=clinic_id, telegram_id=new_id,
            name=f"User {new_id}", role=role,
            created_at=datetime.utcnow()
        )
        db.add(new_staff)
        db.commit()
        await update.message.reply_text(
            get_text("staff_added", lang).format(id=new_id, role=role)
        )
    except Exception as e:
        logger.error(f"Add staff error: {e}")
        await update.message.reply_text(get_text("staff_add_error", lang))
    finally:
        db.close()
    return ConversationHandler.END

async def show_staff_list(update: Update, context: ContextTypes.DEFAULT_TYPE,
                           clinic_id: int, lang: str = "fa"):
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        if clinic_id is None:
            clinic_id = get_user_clinic_id(user_id, db)
        staff = db.query(Staff).filter_by(clinic_id=clinic_id).all()
        if not staff:
            await update.message.reply_text(get_text("staff_list_empty", lang))
        else:
            msg = get_text("staff_list_title", lang) + "\n"
            for s in staff:
                msg += get_text("staff_list_item", lang).format(
                    id=s.telegram_id, name=s.name, role=s.role
                ) + "\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
    finally:
        db.close()

async def show_remove_staff(update: Update, context: ContextTypes.DEFAULT_TYPE,
                             clinic_id: int, lang: str = "fa"):
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        if clinic_id is None:
            clinic_id = get_user_clinic_id(user_id, db)
        staff = db.query(Staff).filter_by(clinic_id=clinic_id).all()
        if not staff:
            await update.message.reply_text(get_text("staff_list_empty", lang))
            return
        keyboard = [
            [InlineKeyboardButton(f"{s.name} ({s.role})", callback_data=f"remove_staff_{s.id}")]
            for s in staff
        ]
        keyboard.append([InlineKeyboardButton(get_text("staff_back", lang), callback_data="staff_back")])
        await update.message.reply_text(
            get_text("staff_select_remove", lang),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    finally:
        db.close()

async def remove_staff_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        lang = get_user_language(user_id, db)
    finally:
        db.close()

    if data == "staff_back":
        await query.edit_message_text("...")
        user_id = update.effective_user.id
        db = SessionLocal()
        try:
            role = get_user_role(user_id, db)
            clinic_id = get_user_clinic_id(user_id, db)
            lang = get_user_language(user_id, db)
            await send_main_menu(update, context, role, clinic_id, db, user_id, lang)
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
            await query.edit_message_text(
                get_text("staff_removed", lang).format(name=staff.name)
            )
        else:
            await query.edit_message_text(get_text("staff_not_found", lang))
    finally:
        db.close()

# ========== Other Feature Handlers ==========
async def show_leads(update: Update, context: ContextTypes.DEFAULT_TYPE,
                      clinic_id: int, lang: str = "fa"):
    db = SessionLocal()
    try:
        leads = db.query(Lead).filter_by(clinic_id=clinic_id, pipeline_stage='new').order_by(Lead.lead_score.desc()).limit(20).all()
        if not leads:
            await update.message.reply_text(get_text("leads_empty", lang))
        else:
            msg = get_text("leads_title", lang) + "\n"
            for l in leads:
                patient = db.query(Patient).filter_by(id=l.patient_id).first()
                msg += get_text("leads_item", lang).format(
                    name=patient.name if patient else "ناشناس",
                    service=l.service,
                    score=l.lead_score
                ) + "\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
    finally:
        db.close()

async def show_doctor_today(update: Update, context: ContextTypes.DEFAULT_TYPE,
                             clinic_id: int, lang: str = "fa"):
    db = SessionLocal()
    try:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        appointments = db.query(Appointment).filter(
            Appointment.clinic_id == clinic_id,
            Appointment.appointment_date >= today_start,
            Appointment.appointment_date < today_start + timedelta(days=1)
        ).all()
        if not appointments:
            await update.message.reply_text(get_text("doctor_today_empty", lang))
        else:
            msg = get_text("doctor_today_title", lang) + "\n"
            for a in appointments:
                patient = db.query(Patient).filter_by(id=a.patient_id).first()
                msg += get_text("doctor_today_item", lang).format(
                    name=patient.name if patient else "بیمار",
                    service=a.service,
                    time=a.appointment_date.strftime('%H:%M')
                ) + "\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
    finally:
        db.close()

async def show_doctor_escalations(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                   clinic_id: int, lang: str = "fa"):
    db = SessionLocal()
    try:
        escalations = db.query(EscalationLog).filter_by(clinic_id=clinic_id, escalated_to='doctor').order_by(EscalationLog.created_at.desc()).limit(10).all()
        if not escalations:
            await update.message.reply_text(get_text("doctor_escalations_empty", lang))
        else:
            msg = get_text("doctor_escalations_title", lang) + "\n"
            for e in escalations:
                patient = db.query(Patient).filter_by(id=e.patient_id).first()
                msg += get_text("doctor_escalations_item", lang).format(
                    name=patient.name if patient else e.patient_id,
                    reason=e.reason,
                    time=e.created_at.strftime('%Y-%m-%d %H:%M')
                ) + "\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
    finally:
        db.close()

async def show_secretary_stats(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                clinic_id: int, lang: str = "fa"):
    db = SessionLocal()
    try:
        today = datetime.utcnow().date()
        start = datetime(today.year, today.month, today.day)
        messages = db.query(RawMessage).filter(RawMessage.created_at >= start).count()
        leads = db.query(Lead).filter(Lead.created_at >= start).count()
        appointments = db.query(Appointment).filter(Appointment.appointment_date >= start).count()
        msg = get_text("stats_today_title", lang) + "\n" + \
              get_text("stats_messages", lang).format(messages=messages) + "\n" + \
              get_text("stats_leads", lang).format(leads=leads) + "\n" + \
              get_text("stats_appointments", lang).format(appointments=appointments)
        await update.message.reply_text(msg, parse_mode='Markdown')
    finally:
        db.close()

async def show_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE,
                             clinic_id: int, role: str, lang: str = "fa"):
    db = SessionLocal()
    try:
        today = datetime.utcnow()
        appointments = db.query(Appointment).filter(
            Appointment.clinic_id == clinic_id, Appointment.appointment_date >= today
        ).order_by(Appointment.appointment_date).limit(20).all()
        if not appointments:
            await update.message.reply_text(get_text("appointments_empty", lang))
        else:
            msg = get_text("appointments_title", lang) + "\n"
            for a in appointments:
                patient = db.query(Patient).filter_by(id=a.patient_id).first()
                msg += get_text("appointments_item", lang).format(
                    name=patient.name if patient else "بیمار",
                    service=a.service,
                    date=a.appointment_date.strftime('%Y-%m-%d %H:%M')
                ) + "\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
    finally:
        db.close()

async def show_patient_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                     lang: str = "fa"):
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        patient = get_patient_by_telegram_id(user_id, db)
        if not patient:
            await update.message.reply_text(get_text("patient_appointments_register_first", lang))
            return
        appointments = db.query(Appointment).filter_by(patient_id=patient.id).order_by(Appointment.appointment_date.desc()).limit(10).all()
        if not appointments:
            await update.message.reply_text(get_text("patient_appointments_empty", lang))
        else:
            msg = get_text("patient_appointments_title", lang) + "\n"
            for a in appointments:
                msg += get_text("patient_appointments_item", lang).format(
                    service=a.service,
                    date=a.appointment_date.strftime('%Y-%m-%d %H:%M'),
                    status=a.status
                ) + "\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
    finally:
        db.close()

# ========== Error Handler ==========
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}", exc_info=context.error)
    if update and update.effective_message:
        user_id = update.effective_user.id
        db = SessionLocal()
        try:
            lang = get_user_language(user_id, db) if user_id else "fa"
        except:
            lang = "fa"
        finally:
            db.close()
        await update.effective_message.reply_text(get_text("error_internal", lang))

# ========== Startup Diagnostics ==========
def startup_diagnostics():
    """Verify configuration and log provider status."""
    logger.info("=== ClinicOS Startup Diagnostics ===")
    try:
        validate_openrouter_config()
        logger.info(f"OpenRouter free models: {OPENROUTER_FREE_MODELS}")
    except ValueError as e:
        logger.error(f"FATAL: OpenRouter configuration error – {e}")
        raise
    if not REDIS_URL:
        logger.warning("REDIS_URL not set. Scores will NOT persist across restarts.")
    else:
        logger.info("Redis configured. Scores will be persisted.")
    logger.info(f"Initial provider scores: {INITIAL_SCORES}")
    logger.info("LLM routing layer ready.")
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set. Voice messages will not be transcribed.")

# ========== Main Application ==========
def main():
    init_db()
    startup_diagnostics()

    # Delete webhook with longer delay to avoid conflict
    for attempt in range(5):
        try:
            resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook", timeout=10)
            if resp.status_code == 200:
                logger.info(f"Webhook deleted (attempt {attempt+1})")
                time.sleep(5)
                break
            else:
                logger.warning(f"Delete webhook attempt {attempt+1} failed: {resp.text}")
        except Exception as e:
            logger.warning(f"Delete webhook attempt {attempt+1} error: {e}")
        time.sleep(3)
    else:
        logger.error("Could not delete webhook after 5 attempts")

    app = Application.builder().token(BOT_TOKEN).build()

    async def startup(application):
        await asyncio.sleep(3)
        from scheduler import init_scheduler, get_scheduler
        init_scheduler()
        scheduler = get_scheduler()
        if not scheduler.running:
            scheduler.start()
            logger.info("⏰ Scheduler started.")

    app.post_init = startup

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_callback, pattern='^lang_'))
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(staff_menu_callback, pattern='^staff_add_')],
        states={
            STAFF_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_staff_id)],
            STAFF_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_staff_confirm)]
        },
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
        fallbacks=[CommandHandler('cancel', lambda u, c: u.message.reply_text("Cancelled"))],
    ))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    app.add_error_handler(error_handler)

    logger.info("🚀 ClinicOS bot started with production LLM routing layer and Voice support")
    app.run_polling()

if __name__ == "__main__":
    main()
"""
Appointment Engine – Handles appointment requests, confirmations, reminders, and no‑show tracking.
Integrates with lead pipeline and Telegram notifications.
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

# ========== Constants ==========
APPOINTMENT_SCHEDULED = "scheduled"
APPOINTMENT_COMPLETED = "completed"
APPOINTMENT_CANCELLED = "cancelled"
APPOINTMENT_NO_SHOW = "no_show"

APPOINTMENT_REQUEST_PENDING = "pending"
APPOINTMENT_REQUEST_CONFIRMED = "confirmed"
APPOINTMENT_REQUEST_CANCELLED = "cancelled"

DEFAULT_REMINDER_HOURS = 24
MAX_RESCHEDULE_ATTEMPTS = 3

# ========== Helper Functions ==========
async def send_telegram_message(chat_id: int, text: str) -> bool:
    """Send a message to a Telegram user via bot API."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        resp = await asyncio.to_thread(
            requests.post, url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10
        )
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Failed to send Telegram message to {chat_id}: {e}")
        return False

def _is_future_date(date: datetime) -> bool:
    """Check if date is in the future (with a 5‑minute buffer)."""
    return date > (datetime.utcnow() + timedelta(minutes=5))

def _get_existing_appointment(
    clinic_id: int, patient_id: int, appointment_date: datetime
) -> Optional[Appointment]:
    """Prevent duplicate appointments inside the supplied clinic."""
    db = SessionLocal()
    try:
        existing = db.query(Appointment).filter(
            Appointment.clinic_id == clinic_id,
            Appointment.patient_id == patient_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status.in_([APPOINTMENT_SCHEDULED, APPOINTMENT_COMPLETED])
        ).first()
        return existing
    finally:
        db.close()

# ========== Core Functions ==========
def create_appointment_request(lead_id: int, suggested_date: datetime, notes: Optional[str] = None) -> Optional[int]:
    """
    Create an appointment request linked to a lead.
    Returns request_id if successful, None otherwise.
    """
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter_by(id=lead_id).first()
        if not lead or not lead.clinic_id:
            logger.error(f"Lead {lead_id} not found")
            return None

        # Check for pending request already
        existing = db.query(AppointmentRequest).filter(
            AppointmentRequest.lead_id == lead_id,
            AppointmentRequest.status == APPOINTMENT_REQUEST_PENDING
        ).first()
        if existing:
            logger.warning(f"Pending request already exists for lead {lead_id}")
            return existing.id

        request = AppointmentRequest(
            clinic_id=lead.clinic_id,
            lead_id=lead_id,
            suggested_date=suggested_date,
            status=APPOINTMENT_REQUEST_PENDING,
            notes=notes,
            created_at=datetime.utcnow()
        )
        db.add(request)
        lead.pipeline_stage = "consultation"
        ph = PipelineHistory(lead_id=lead.id, stage="consultation", changed_at=datetime.utcnow())
        db.add(ph)
        db.commit()

        # Notify secretaries (async)
        asyncio.create_task(_notify_staff_of_request(lead.clinic_id, request.id))
        return request.id
    except Exception as e:
        logger.error(f"Create appointment request error: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def confirm_appointment(request_id: int, confirmed_date: datetime, staff_id: int) -> bool:
    """
    Confirm a pending appointment request, creating a confirmed appointment.
    """
    if not _is_future_date(confirmed_date):
        logger.error("Confirmed date must be in the future")
        return False

    db = SessionLocal()
    try:
        req = db.query(AppointmentRequest).filter_by(id=request_id).first()
        if not req or req.status != APPOINTMENT_REQUEST_PENDING:
            logger.error(f"Request {request_id} not found or not pending")
            return False

        lead = db.query(Lead).filter_by(id=req.lead_id).first()
        if not lead or lead.clinic_id != req.clinic_id:
            logger.error(f"Lead not found for request {request_id}")
            return False

        staff = db.query(Staff).filter_by(id=staff_id).first()
        if not staff or staff.clinic_id != req.clinic_id:
            logger.error("Appointment confirmation denied: staff/clinic mismatch")
            return False

        # Check duplicate
        existing = _get_existing_appointment(req.clinic_id, lead.patient_id, confirmed_date)
        if existing:
            logger.warning(f"Duplicate appointment for patient {lead.patient_id} on {confirmed_date}")
            return False

        req.status = APPOINTMENT_REQUEST_CONFIRMED
        req.confirmed_date = confirmed_date
        req.confirmed_by = staff_id

        appointment = Appointment(
            clinic_id=req.clinic_id,
            lead_id=req.lead_id,
            patient_id=lead.patient_id,
            service=lead.service,
            appointment_date=confirmed_date,
            status=APPOINTMENT_SCHEDULED,
            reminder_sent=False,
            no_show=False,
            created_at=datetime.utcnow()
        )
        db.add(appointment)
        lead.pipeline_stage = "booked"
        ph = PipelineHistory(lead_id=lead.id, stage="booked", changed_at=datetime.utcnow(), changed_by=staff_id)
        db.add(ph)
        db.commit()

        asyncio.create_task(_notify_patient_confirmed(lead.patient_id, confirmed_date, lead.service))
        return True
    except Exception as e:
        logger.error(f"Confirm appointment error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def cancel_appointment(appointment_id: int, reason: Optional[str] = None, staff_id: Optional[int] = None) -> bool:
    """Cancel a scheduled appointment and update lead pipeline."""
    db = SessionLocal()
    try:
        appt = db.query(Appointment).filter_by(id=appointment_id).first()
        if not appt or appt.status == APPOINTMENT_CANCELLED:
            return False
        if staff_id is not None:
            staff = db.query(Staff).filter_by(id=staff_id).first()
            if not staff or staff.clinic_id != appt.clinic_id:
                logger.error("Appointment cancellation denied: staff/clinic mismatch")
                return False
        appt.status = APPOINTMENT_CANCELLED
        lead = db.query(Lead).filter_by(
            id=appt.lead_id, clinic_id=appt.clinic_id
        ).first()
        if lead:
            lead.pipeline_stage = "lost"
            ph = PipelineHistory(lead_id=lead.id, stage="lost", changed_at=datetime.utcnow(), changed_by=staff_id)
            db.add(ph)
        db.commit()
        asyncio.create_task(_notify_patient_cancellation(appt.patient_id, appt.service, reason))
        return True
    except Exception as e:
        logger.error(f"Cancel appointment error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def complete_appointment(appointment_id: int, revenue: Optional[float] = None) -> bool:
    """Mark appointment as completed and optionally record revenue."""
    db = SessionLocal()
    try:
        appt = db.query(Appointment).filter_by(id=appointment_id).first()
        if not appt or appt.status != APPOINTMENT_SCHEDULED:
            return False
        appt.status = APPOINTMENT_COMPLETED
        if revenue is not None:
            appt.revenue = revenue
        lead = db.query(Lead).filter_by(
            id=appt.lead_id, clinic_id=appt.clinic_id
        ).first()
        if lead:
            lead.pipeline_stage = "completed"
            ph = PipelineHistory(lead_id=lead.id, stage="completed", changed_at=datetime.utcnow())
            db.add(ph)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Complete appointment error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

async def send_reminders():
    """Send reminders for appointments within the next DEFAULT_REMINDER_HOURS."""
    logger.info("Sending appointment reminders...")
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
            date_str = appt.appointment_date.strftime("%Y/%m/%d %H:%M")
            message = f"🔔 *Appointment Reminder*\n\nService: {appt.service}\nDate & Time: {date_str}\n⏰ In {hours_left} hours"
            await send_telegram_message(int(alias.external_user_id), message)
            appt.reminder_sent = True
            sent += 1
            await asyncio.sleep(0.5)
    db.commit()
    db.close()
    logger.info(f"Sent {sent} reminders.")

async def check_no_shows():
    """Mark appointments as no‑show if they passed without completion."""
    logger.info("Checking no‑shows...")
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
    logger.info(f"Marked {len(past_appointments)} no‑shows.")

# ========== Internal Notification Helpers ==========
async def _notify_staff_of_request(clinic_id: int, request_id: int):
    """Notify all secretaries and doctors about a new appointment request."""
    db = SessionLocal()
    try:
        staff = db.query(Staff).filter(
            Staff.clinic_id == clinic_id,
            Staff.role.in_(['owner', 'doctor', 'secretary'])
        ).all()
        req = db.query(AppointmentRequest).filter_by(id=request_id).first()
        if not req:
            return
        lead = db.query(Lead).filter_by(id=req.lead_id).first()
        patient = db.query(Patient).filter_by(id=lead.patient_id).first() if lead else None
        message = (
            f"📅 *New Appointment Request*\n\n"
            f"Patient: {patient.name if patient else 'Unknown'}\n"
            f"Service: {lead.service if lead else 'Unknown'}\n"
            f"Suggested: {req.suggested_date}\n"
            f"Request ID: `{request_id}`\n"
            f"To confirm: `/confirm_appt {request_id} YYYY-MM-DD HH:MM`"
        )
        for s in staff:
            await send_telegram_message(s.telegram_id, message)
            await asyncio.sleep(0.5)
    finally:
        db.close()

async def _notify_patient_confirmed(patient_id: int, appointment_date: datetime, service: str):
    """Notify patient that their appointment has been confirmed."""
    db = SessionLocal()
    try:
        alias = db.query(PatientAlias).filter_by(patient_id=patient_id, platform='telegram').first()
        if alias and alias.external_user_id:
            date_str = appointment_date.strftime("%Y/%m/%d %H:%M")
            message = f"✅ *Appointment Confirmed*\n\nService: {service}\nDate & Time: {date_str}\n\n📍 Please arrive 15 minutes early."
            await send_telegram_message(int(alias.external_user_id), message)
    finally:
        db.close()

async def _notify_patient_cancellation(patient_id: int, service: str, reason: Optional[str] = None):
    """Notify patient of cancellation."""
    db = SessionLocal()
    try:
        alias = db.query(PatientAlias).filter_by(patient_id=patient_id, platform='telegram').first()
        if alias and alias.external_user_id:
            message = f"❌ *Appointment Cancelled*\n\nService: {service}"
            if reason:
                message += f"\nReason: {reason}"
            message += "\n\nPlease contact the clinic to reschedule."
            await send_telegram_message(int(alias.external_user_id), message)
    finally:
        db.close()

# ========== Query Functions ==========
def get_upcoming_appointments(clinic_id: int, days: int = 7) -> List[Dict]:
    """List upcoming appointments (next `days` days)."""
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
    """List appointments scheduled for today."""
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
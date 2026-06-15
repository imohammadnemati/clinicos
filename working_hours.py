"""
Working Hours Manager – Controls auto‑reply behaviour based on clinic working hours.
Prevents disturbing patients during off‑hours while allowing active conversations to continue.
No LLM dependencies.
"""

from datetime import datetime, timedelta
from database import SessionLocal
from models import ClinicWorkingHours, Session
import logging

logger = logging.getLogger(__name__)


def get_clinic_working_hours(clinic_id: int):
    """Retrieve working hours configuration for a clinic."""
    db = SessionLocal()
    try:
        return db.query(ClinicWorkingHours).filter_by(clinic_id=clinic_id).first()
    finally:
        db.close()


def is_within_working_hours(clinic_id: int, current_time: datetime = None) -> bool:
    """Check if the given time falls within the clinic's configured working hours."""
    if current_time is None:
        current_time = datetime.utcnow()
    wh = get_clinic_working_hours(clinic_id)
    if not wh:
        # If no hours configured, assume always open
        return True

    start = wh.start_time
    end = wh.end_time
    now_time = current_time.time()

    # Support overnight ranges (e.g., 22:00 – 08:00)
    if start <= end:
        return start <= now_time <= end
    else:
        return now_time >= start or now_time <= end


def is_active_conversation(session_id: int, db, timeout_minutes: int = 30) -> bool:
    """
    Determine if a conversation is still active (recent message exchange).
    Used to allow replies during off‑hours if the user is still waiting.
    """
    session = db.query(Session).filter_by(id=session_id).first()
    if not session or not session.last_activity:
        return False
    now = datetime.utcnow()
    return (now - session.last_activity) < timedelta(minutes=timeout_minutes)


async def can_auto_reply(clinic_id: int, session_id: int, db) -> bool:
    """
    Main decision function:
    Returns True if the bot should automatically reply to the current message.
    Rules:
    - Always reply during working hours.
    - During off‑hours, reply only if the conversation is still active.
    """
    wh = get_clinic_working_hours(clinic_id)
    if not wh:
        # No working hours configured → always reply
        return True

    # Inside working hours → reply
    if is_within_working_hours(clinic_id):
        return True

    # Outside working hours → reply only if conversation is active
    if is_active_conversation(session_id, db, wh.active_timeout_minutes):
        return True

    return False


def set_clinic_working_hours(clinic_id: int, start_time, end_time, active_timeout_minutes: int = 30) -> bool:
    """
    Set or update working hours for a clinic.
    start_time and end_time are datetime.time objects.
    """
    db = SessionLocal()
    try:
        wh = db.query(ClinicWorkingHours).filter_by(clinic_id=clinic_id).first()
        if wh:
            wh.start_time = start_time
            wh.end_time = end_time
            wh.active_timeout_minutes = active_timeout_minutes
        else:
            wh = ClinicWorkingHours(
                clinic_id=clinic_id,
                start_time=start_time,
                end_time=end_time,
                active_timeout_minutes=active_timeout_minutes
            )
            db.add(wh)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to set working hours: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def get_default_working_hours():
    """Return default working hours (08:00 – 22:00)."""
    from datetime import time
    return time(8, 0), time(22, 0), 30
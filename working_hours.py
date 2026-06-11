from datetime import datetime, timedelta
from database import SessionLocal
from models import ClinicWorkingHours, Session
import logging

logger = logging.getLogger(__name__)

def get_clinic_working_hours(clinic_id):
    db = SessionLocal()
    try:
        return db.query(ClinicWorkingHours).filter_by(clinic_id=clinic_id).first()
    finally:
        db.close()

def is_within_working_hours(clinic_id, current_time=None):
    if current_time is None:
        current_time = datetime.utcnow()
    wh = get_clinic_working_hours(clinic_id)
    if not wh:
        return True
    start = wh.start_time
    end = wh.end_time
    now_time = current_time.time()
    if start <= end:
        return start <= now_time <= end
    else:
        return now_time >= start or now_time <= end

def is_active_conversation(session_id, db, timeout_minutes=30):
    session = db.query(Session).filter_by(id=session_id).first()
    if not session or not session.last_activity:
        return False
    now = datetime.utcnow()
    return (now - session.last_activity) < timedelta(minutes=timeout_minutes)

async def can_auto_reply(clinic_id, session_id, db):
    """فقط یک خروجی boolean برمی‌گرداند"""
    wh = get_clinic_working_hours(clinic_id)
    if not wh:
        return True
    if is_within_working_hours(clinic_id):
        return True
    if is_active_conversation(session_id, db, wh.active_timeout_minutes):
        return True
    return False
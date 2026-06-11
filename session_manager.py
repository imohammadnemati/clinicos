from datetime import datetime, timedelta
from database import SessionLocal
from models import Session
from config import SESSION_HOURS

def get_or_create_session(clinic_id, patient_id):
    db = SessionLocal()
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=SESSION_HOURS)
    active = db.query(Session).filter(
        Session.clinic_id == clinic_id,
        Session.patient_id == patient_id,
        Session.is_active == True,
        Session.start_time > cutoff
    ).first()
    if active:
        # update last_activity
        active.last_activity = now
        db.commit()
        db.close()
        return active.id
    # close old sessions
    db.query(Session).filter(
        Session.clinic_id == clinic_id,
        Session.patient_id == patient_id,
        Session.is_active == True
    ).update({"is_active": False, "end_time": now})
    new = Session(clinic_id=clinic_id, patient_id=patient_id, start_time=now, last_activity=now, is_active=True)
    db.add(new)
    db.commit()
    sid = new.id
    db.close()
    return sid
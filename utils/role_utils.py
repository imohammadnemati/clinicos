"""
Role utilities for Clinicos – shared between bot.py and handlers.
"""
from sqlalchemy.orm import Session
from models import Staff, Patient


def get_user_role(user_id: int, db: Session) -> str:
    """Get user role from database."""
    staff = db.query(Staff).filter_by(telegram_id=user_id).first()
    if staff:
        return staff.role
    return 'patient'


def get_user_language(user_id: int, db: Session) -> str:
    """Get user language from database."""
    staff = db.query(Staff).filter_by(telegram_id=user_id).first()
    if staff and hasattr(staff, 'language') and staff.language:
        return staff.language
    patient = db.query(Patient).filter_by(telegram_id=user_id).first()
    if patient and patient.preferred_language:
        return patient.preferred_language
    return 'fa'


def get_user_clinic_id(user_id: int, db: Session) -> int:
    """Get user's clinic ID from database."""
    staff = db.query(Staff).filter_by(telegram_id=user_id).first()
    if staff:
        return staff.clinic_id
    patient = db.query(Patient).filter_by(telegram_id=user_id).first()
    if patient and patient.clinic_id:
        return patient.clinic_id
    # Fallback to first clinic
    from models import Clinic
    clinic = db.query(Clinic).first()
    if not clinic:
        clinic = Clinic(name="Default Clinic", subdomain="default")
        db.add(clinic)
        db.commit()
    return clinic.id

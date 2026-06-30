"""
Role utilities for Clinicos – shared between bot.py and handlers.
Each function creates its own database session to avoid None errors.
"""

from database import SessionLocal
from models import Staff, Patient, Clinic


def get_user_role(user_id: int) -> str:
    """
    Get user role from database.
    Creates its own database session.
    Returns 'patient' if user is not found.
    """
    db = SessionLocal()
    try:
        staff = db.query(Staff).filter_by(telegram_id=user_id).first()
        if staff:
            return staff.role
        return 'patient'
    finally:
        db.close()


def get_user_language(user_id: int) -> str:
    """
    Get user's preferred language from database.
    Creates its own database session.
    Returns 'fa' if not found.
    """
    db = SessionLocal()
    try:
        staff = db.query(Staff).filter_by(telegram_id=user_id).first()
        if staff and hasattr(staff, 'language') and staff.language:
            return staff.language
        patient = db.query(Patient).filter_by(telegram_id=user_id).first()
        if patient and patient.preferred_language:
            return patient.preferred_language
        return 'fa'
    finally:
        db.close()


def get_user_clinic_id(user_id: int) -> int:
    """
    Get user's clinic ID from database.
    Creates its own database session.
    Falls back to the first available clinic or creates a default one.
    """
    db = SessionLocal()
    try:
        staff = db.query(Staff).filter_by(telegram_id=user_id).first()
        if staff:
            return staff.clinic_id
        patient = db.query(Patient).filter_by(telegram_id=user_id).first()
        if patient and patient.clinic_id:
            return patient.clinic_id
        # Fallback to first clinic
        clinic = db.query(Clinic).first()
        if not clinic:
            clinic = Clinic(name="Default Clinic", subdomain="default")
            db.add(clinic)
            db.commit()
        return clinic.id
    finally:
        db.close()

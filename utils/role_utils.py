"""
Role utilities for Clinicos – shared between bot.py and handlers.
Each function creates its own database session to avoid None errors.
"""

from typing import Optional
from database import SessionLocal
from models import Staff, Patient, PatientAlias


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
        patient_language = (
            db.query(Patient.preferred_language)
            .join(PatientAlias, PatientAlias.patient_id == Patient.id)
            .filter(
                PatientAlias.platform == "telegram",
                PatientAlias.external_user_id == str(user_id),
                Patient.preferred_language.isnot(None),
            )
            .first()
        )
        if patient_language and patient_language[0]:
            return patient_language[0]
        return 'fa'
    finally:
        db.close()


def get_user_clinic_id(user_id: int) -> Optional[int]:
    """
    Resolve the authenticated user's clinic without unsafe cross-tenant fallback.

    Staff membership is authoritative. For patients, the Telegram alias is the
    identity link; a patient is considered safely resolvable only when all
    matching aliases point to exactly one clinic. Ambiguous or missing tenant
    context returns None.
    """
    db = SessionLocal()
    try:
        staff = db.query(Staff).filter_by(telegram_id=user_id).first()
        if staff and staff.clinic_id:
            return staff.clinic_id

        clinic_ids = (
            db.query(Patient.clinic_id)
            .join(PatientAlias, PatientAlias.patient_id == Patient.id)
            .filter(
                PatientAlias.platform == "telegram",
                PatientAlias.external_user_id == str(user_id),
                Patient.clinic_id.isnot(None),
            )
            .distinct()
            .all()
        )
        resolved = {row[0] for row in clinic_ids if row[0] is not None}
        if len(resolved) == 1:
            return next(iter(resolved))
        return None
    finally:
        db.close()

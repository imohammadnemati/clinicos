""" 
Role utilities for Clinicos – shared between bot.py and handlers.
Each function creates its own database session to avoid None errors.
"""

from typing import Optional
from database import SessionLocal
from models import Staff, Patient, PatientAlias


def get_user_role(user_id: int) -> str:
    """Return the staff role, or patient when no staff record exists."""
    db = SessionLocal()
    try:
        staff = db.query(Staff).filter_by(telegram_id=user_id).first()
        if staff:
            return staff.role
        return "patient"
    finally:
        db.close()


def get_user_language(user_id: int) -> str:
    """
    Resolve preferred language from the authenticated identity.

    Staff Telegram IDs are globally unique and authoritative. For patients,
    language is accepted only when the Telegram alias resolves to exactly one
    clinic and exactly one non-null preferred language. Ambiguous identity
    fails closed to Persian.
    """
    db = SessionLocal()
    try:
        staff = db.query(Staff).filter_by(telegram_id=user_id).first()
        if staff and staff.language:
            return staff.language

        rows = (
            db.query(Patient.clinic_id, Patient.preferred_language)
            .join(PatientAlias, PatientAlias.patient_id == Patient.id)
            .filter(
                PatientAlias.platform == "telegram",
                PatientAlias.external_user_id == str(user_id),
                Patient.clinic_id.isnot(None),
                Patient.preferred_language.isnot(None),
            )
            .distinct()
            .all()
        )

        clinic_ids = {row[0] for row in rows if row[0] is not None}
        languages = {row[1] for row in rows if row[1]}

        if len(clinic_ids) == 1 and len(languages) == 1:
            return next(iter(languages))
        return "fa"
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

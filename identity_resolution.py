"""
Identity Resolution – Patient identification and alias management across platforms.
Supports Telegram, Instagram, WhatsApp, etc. Uses PatientAlias table.
No LLM dependencies.
"""

import logging
import re
from datetime import datetime
from typing import Optional

from database import SessionLocal
from models import Patient, PatientAlias

logger = logging.getLogger(__name__)


# ========== Extraction Helpers ==========
def extract_phone_number(text: str) -> Optional[str]:
    """Extract Iranian mobile phone number from text (11 digits starting with 09)."""
    if not text:
        return None
    match = re.search(r"09\d{9}", text)
    return match.group() if match else None


def extract_name(text: str) -> Optional[str]:
    """Extract a probable name from text (simplified heuristic)."""
    if not text:
        return None
    patterns = [
        r"نام من ([\w\u0600-\u06FF]+)",
        r"من ([\w\u0600-\u06FF]+) هستم",
        r"اسم من ([\w\u0600-\u06FF]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def extract_instagram_username(text: str) -> Optional[str]:
    """Extract Instagram username (with or without @)."""
    if not text:
        return None
    match = re.search(r"@?([a-zA-Z0-9_\.]{3,30})", text)
    return match.group(1) if match else None


def extract_telegram_username(text: str) -> Optional[str]:
    """Extract Telegram username (with or without @)."""
    if not text:
        return None
    match = re.search(r"@([a-zA-Z0-9_]{5,32})", text)
    return match.group(1) if match else None


# ========== Patient Lookup ==========
def find_patient_by_alias(
    clinic_id: int,
    platform: str,
    phone: Optional[str] = None,
    external_user_id: Optional[str] = None,
    username: Optional[str] = None,
    display_name: Optional[str] = None,
) -> Optional[int]:
    """Search for a patient alias inside the supplied clinic only."""
    db = SessionLocal()
    try:
        query = (
            db.query(PatientAlias)
            .join(Patient, Patient.id == PatientAlias.patient_id)
            .filter(
                PatientAlias.platform == platform,
                Patient.clinic_id == clinic_id,
            )
        )
        if phone:
            alias = query.filter_by(phone=phone).first()
            if alias:
                return alias.patient_id
        if external_user_id:
            alias = query.filter_by(external_user_id=external_user_id).first()
            if alias:
                return alias.patient_id
        if username:
            alias = query.filter_by(username=username).first()
            if alias:
                return alias.patient_id
        if display_name:
            alias = query.filter_by(display_name=display_name).first()
            if alias:
                return alias.patient_id
        return None
    finally:
        db.close()


def find_patient_by_any_platform(
    clinic_id: int,
    phone: Optional[str] = None,
    external_user_id: Optional[str] = None,
) -> Optional[int]:
    """Search aliases across platforms, but only inside the supplied clinic."""
    if not phone and not external_user_id:
        return None
    db = SessionLocal()
    try:
        query = (
            db.query(PatientAlias)
            .join(Patient, Patient.id == PatientAlias.patient_id)
            .filter(Patient.clinic_id == clinic_id)
        )
        if phone:
            alias = query.filter_by(phone=phone).first()
            if alias:
                return alias.patient_id
        if external_user_id:
            alias = query.filter_by(external_user_id=external_user_id).first()
            if alias:
                return alias.patient_id
        return None
    finally:
        db.close()


# ========== Patient Creation & Update ==========
def get_or_create_patient(
    clinic_id: int,
    platform: str,
    external_user_id: str,
    username: Optional[str] = None,
    display_name: Optional[str] = None,
    raw_text: Optional[str] = None,
) -> int:
    """Retrieve an existing patient or create one inside the supplied clinic."""
    if clinic_id is None:
        raise ValueError("clinic_id is required for patient identity resolution")
    if not platform:
        raise ValueError("platform is required for patient identity resolution")
    if not external_user_id:
        raise ValueError("external_user_id is required for patient identity resolution")

    phone = extract_phone_number(raw_text) if raw_text else None
    extracted_name = extract_name(raw_text) if raw_text else None
    final_name = extracted_name or display_name

    patient_id = find_patient_by_alias(
        clinic_id=clinic_id,
        platform=platform,
        phone=phone,
        external_user_id=external_user_id,
        username=username,
        display_name=final_name,
    )

    db = SessionLocal()
    try:
        if patient_id:
            patient = (
                db.query(Patient)
                .filter(Patient.id == patient_id, Patient.clinic_id == clinic_id)
                .first()
            )
            if not patient:
                raise ValueError("Resolved patient does not belong to the supplied clinic")

            patient.last_seen = datetime.utcnow()
            if not patient.name and final_name:
                patient.name = final_name
            if not patient.phone and phone:
                patient.phone = phone
            db.commit()
            _add_alias_if_missing(
                db, patient_id, platform, phone, external_user_id, username, final_name
            )
            return patient_id

        merged_id = find_patient_by_any_platform(
            clinic_id, phone=phone, external_user_id=external_user_id
        )
        if merged_id:
            patient = (
                db.query(Patient)
                .filter(Patient.id == merged_id, Patient.clinic_id == clinic_id)
                .first()
            )
            if not patient:
                raise ValueError("Resolved merge target does not belong to the supplied clinic")

            patient.last_seen = datetime.utcnow()
            if not patient.name and final_name:
                patient.name = final_name
            if not patient.phone and phone:
                patient.phone = phone
            alias = PatientAlias(
                patient_id=merged_id,
                platform=platform,
                external_user_id=external_user_id,
                username=username,
                display_name=final_name,
                phone=phone,
                confidence=0.9 if phone else 0.7,
                created_at=datetime.utcnow(),
            )
            db.add(alias)
            db.commit()
            return merged_id

        patient = Patient(
            clinic_id=clinic_id,
            name=final_name,
            phone=phone,
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            status="active",
            created_at=datetime.utcnow(),
        )
        db.add(patient)
        db.flush()

        alias = PatientAlias(
            patient_id=patient.id,
            platform=platform,
            external_user_id=external_user_id,
            username=username,
            display_name=final_name,
            phone=phone,
            confidence=0.9 if phone else 0.7,
            created_at=datetime.utcnow(),
        )
        db.add(alias)
        db.commit()
        logger.info("Created new patient %s from %s", patient.id, platform)
        return patient.id
    except Exception as e:
        logger.error("Error in get_or_create_patient: %s", e)
        db.rollback()
        raise
    finally:
        db.close()


def _add_alias_if_missing(
    db,
    patient_id: int,
    platform: str,
    phone: Optional[str],
    external_user_id: Optional[str],
    username: Optional[str],
    display_name: Optional[str],
):
    """Add missing aliases for a patient, avoiding exact duplicates."""
    if phone:
        existing = db.query(PatientAlias).filter_by(
            patient_id=patient_id, platform=platform, phone=phone
        ).first()
        if not existing:
            db.add(PatientAlias(
                patient_id=patient_id,
                platform=platform,
                phone=phone,
                confidence=0.9,
                created_at=datetime.utcnow(),
            ))
    if username:
        existing = db.query(PatientAlias).filter_by(
            patient_id=patient_id, platform=platform, username=username
        ).first()
        if not existing:
            db.add(PatientAlias(
                patient_id=patient_id,
                platform=platform,
                username=username,
                confidence=0.8,
                created_at=datetime.utcnow(),
            ))
    if external_user_id:
        existing = db.query(PatientAlias).filter_by(
            patient_id=patient_id, platform=platform, external_user_id=external_user_id
        ).first()
        if not existing:
            db.add(PatientAlias(
                patient_id=patient_id,
                platform=platform,
                external_user_id=external_user_id,
                confidence=0.85,
                created_at=datetime.utcnow(),
            ))
    if display_name:
        existing = db.query(PatientAlias).filter_by(
            patient_id=patient_id, platform=platform, display_name=display_name
        ).first()
        if not existing:
            db.add(PatientAlias(
                patient_id=patient_id,
                platform=platform,
                display_name=display_name,
                confidence=0.6,
                created_at=datetime.utcnow(),
            ))
    db.commit()


# ========== Utility Functions ==========
def get_patient_aliases(patient_id: int) -> list:
    """Return all aliases for a patient. Caller must enforce tenant authorization."""
    db = SessionLocal()
    try:
        aliases = db.query(PatientAlias).filter_by(patient_id=patient_id).all()
        return [
            {
                "platform": a.platform,
                "external_user_id": a.external_user_id,
                "username": a.username,
                "display_name": a.display_name,
                "phone": a.phone,
                "confidence": a.confidence,
            }
            for a in aliases
        ]
    finally:
        db.close()


def merge_patients(master_patient_id: int, slave_patient_id: int) -> bool:
    """
    Merge two patient records only when both patients belong to the same clinic.
    Cross-clinic merges fail closed.
    """
    if master_patient_id == slave_patient_id:
        return False

    db = SessionLocal()
    try:
        patients = (
            db.query(Patient)
            .filter(Patient.id.in_([master_patient_id, slave_patient_id]))
            .all()
        )
        if len(patients) != 2:
            logger.warning(
                "Merge refused: one or both patients do not exist (%s, %s)",
                master_patient_id,
                slave_patient_id,
            )
            return False

        by_id = {p.id: p for p in patients}
        master = by_id.get(master_patient_id)
        slave = by_id.get(slave_patient_id)
        if not master or not slave or master.clinic_id != slave.clinic_id:
            logger.warning(
                "Cross-clinic patient merge refused: master=%s clinic=%s, slave=%s clinic=%s",
                master_patient_id,
                getattr(master, "clinic_id", None),
                slave_patient_id,
                getattr(slave, "clinic_id", None),
            )
            return False

        db.query(PatientAlias).filter_by(patient_id=slave_patient_id).update(
            {"patient_id": master_patient_id}
        )
        db.query(Patient).filter_by(id=slave_patient_id).update(
            {"master_patient_id": master_patient_id}
        )
        db.commit()
        logger.info(
            "Merged patient %s into %s inside clinic %s",
            slave_patient_id,
            master_patient_id,
            master.clinic_id,
        )
        return True
    except Exception as e:
        logger.error("Merge patients error: %s", e)
        db.rollback()
        return False
    finally:
        db.close()

import re
from database import SessionLocal
from models import Patient, PatientAlias
from datetime import datetime

def extract_phone(text):
    if not text:
        return None
    match = re.search(r'09\d{9}', text)
    return match.group() if match else None

def extract_instagram_username(text):
    if not text:
        return None
    match = re.search(r'@?([a-zA-Z0-9_\.]{3,30})', text)
    return match.group(1) if match else None

def find_patient_by_alias(platform, phone=None, external_user_id=None, username=None, display_name=None):
    db = SessionLocal()
    query = db.query(PatientAlias).filter_by(platform=platform)
    if phone:
        alias = query.filter_by(phone=phone).first()
        if alias:
            db.close()
            return alias.patient_id
    if external_user_id:
        alias = query.filter_by(external_user_id=external_user_id).first()
        if alias:
            db.close()
            return alias.patient_id
    if username:
        alias = query.filter_by(username=username).first()
        if alias:
            db.close()
            return alias.patient_id
    if display_name:
        alias = query.filter_by(display_name=display_name).first()
        if alias:
            db.close()
            return alias.patient_id
    db.close()
    return None

def get_or_create_patient(clinic_id, platform, external_user_id, username=None, display_name=None, raw_text=None):
    phone = extract_phone(raw_text) if raw_text else None
    patient_id = find_patient_by_alias(platform, phone=phone, external_user_id=external_user_id, username=username, display_name=display_name)
    db = SessionLocal()
    if patient_id:
        # update existing patient's last_seen and maybe add new aliases
        patient = db.query(Patient).filter_by(id=patient_id).first()
        if patient:
            patient.last_seen = datetime.utcnow()
            if phone and not patient.phone:
                patient.phone = phone
            if display_name and not patient.name:
                patient.name = display_name
            db.commit()
        # add any missing alias
        if phone:
            existing = db.query(PatientAlias).filter_by(patient_id=patient_id, platform=platform, phone=phone).first()
            if not existing:
                alias = PatientAlias(patient_id=patient_id, platform=platform, phone=phone, confidence=0.9)
                db.add(alias)
        if username:
            existing = db.query(PatientAlias).filter_by(patient_id=patient_id, platform=platform, username=username).first()
            if not existing:
                alias = PatientAlias(patient_id=patient_id, platform=platform, username=username, confidence=0.8)
                db.add(alias)
        if external_user_id:
            existing = db.query(PatientAlias).filter_by(patient_id=patient_id, platform=platform, external_user_id=external_user_id).first()
            if not existing:
                alias = PatientAlias(patient_id=patient_id, platform=platform, external_user_id=external_user_id, confidence=0.8)
                db.add(alias)
        db.commit()
        db.close()
        return patient_id
    # create new patient
    patient = Patient(clinic_id=clinic_id, name=display_name, phone=phone, first_seen=datetime.utcnow(), last_seen=datetime.utcnow())
    db.add(patient)
    db.flush()
    alias = PatientAlias(
        patient_id=patient.id, platform=platform,
        external_user_id=external_user_id, username=username, display_name=display_name, phone=phone,
        confidence=0.9 if phone else 0.7
    )
    db.add(alias)
    db.commit()
    patient_id = patient.id
    db.close()
    return patient_id
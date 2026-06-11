import re
from database import SessionLocal
from models import Patient, PatientAlias
from datetime import datetime

def extract_phone(text):
    if not text: return None
    match = re.search(r'09\d{9}', text)
    return match.group() if match else None

def extract_name(text):
    if not text: return None
    patterns = [r'نام من ([\w\u0600-\u06FF]+)', r'من ([\w\u0600-\u06FF]+) هستم']
    for pat in patterns:
        m = re.search(pat, text)
        if m: return m.group(1)
    return None

def find_patient_by_alias(platform, phone=None, external_user_id=None, username=None, display_name=None):
    db = SessionLocal()
    query = db.query(PatientAlias).filter_by(platform=platform)
    if phone:
        alias = query.filter_by(phone=phone).first()
        if alias: db.close(); return alias.patient_id
    if external_user_id:
        alias = query.filter_by(external_user_id=external_user_id).first()
        if alias: db.close(); return alias.patient_id
    if username:
        alias = query.filter_by(username=username).first()
        if alias: db.close(); return alias.patient_id
    if display_name:
        alias = query.filter_by(display_name=display_name).first()
        if alias: db.close(); return alias.patient_id
    db.close()
    return None

def get_or_create_patient(clinic_id, platform, external_user_id, username=None, display_name=None, raw_text=None):
    phone = extract_phone(raw_text) if raw_text else None
    patient_id = find_patient_by_alias(platform, phone, external_user_id, username, display_name)
    db = SessionLocal()
    if patient_id:
        patient = db.query(Patient).filter_by(id=patient_id).first()
        if patient:
            patient.last_seen = datetime.utcnow()
            if not patient.name and (display_name or extract_name(raw_text)):
                patient.name = display_name or extract_name(raw_text)
            if not patient.phone and phone:
                patient.phone = phone
        db.commit()
        db.close()
        return patient_id
    # create new
    name = display_name or extract_name(raw_text)
    patient = Patient(clinic_id=clinic_id, name=name, phone=phone,
                      first_seen=datetime.utcnow(), last_seen=datetime.utcnow())
    db.add(patient)
    db.flush()
    alias = PatientAlias(patient_id=patient.id, platform=platform,
                         external_user_id=external_user_id, username=username,
                         display_name=display_name, phone=phone, confidence=0.9 if phone else 0.7)
    db.add(alias)
    db.commit()
    pid = patient.id
    db.close()
    return pid
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Index, Time
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Clinic(Base):
    __tablename__ = 'clinics'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    subdomain = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Staff(Base):
    __tablename__ = 'staff'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    telegram_id = Column(Integer, unique=True)
    name = Column(String(200))
    role = Column(String(50))
    invited_by = Column(Integer, ForeignKey('staff.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    master_patient_id = Column(Integer, ForeignKey('patients.id'), nullable=True)
    name = Column(String(200))
    phone = Column(String(50))
    status = Column(String(20), default='active')
    memory_purged = Column(Boolean, default=False)
    summary_data = Column(JSON, nullable=True)
    preferred_language = Column(String(10), default='fa')
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class PatientAlias(Base):
    __tablename__ = 'patient_aliases'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    platform = Column(String(50))
    external_user_id = Column(String(200), nullable=True)
    username = Column(String(200), nullable=True)
    display_name = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (
        Index('idx_platform_phone', 'platform', 'phone'),
        Index('idx_platform_uid', 'platform', 'external_user_id'),
        Index('idx_platform_username', 'platform', 'username'),
    )

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    requires_human = Column(Boolean, default=False)
    conversation_status = Column(String(20), default='active')
    last_activity = Column(DateTime, default=datetime.utcnow)

class RawMessage(Base):
    __tablename__ = 'raw_messages'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    session_id = Column(Integer, ForeignKey('sessions.id'))
    platform = Column(String(50))
    external_user_id = Column(String(200))
    message_text = Column(Text)
    media_url = Column(Text, nullable=True)
    media_type = Column(String(20), nullable=True)
    voice_duration = Column(Integer, nullable=True)
    transcript = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (
        Index('idx_raw_clinic_patient', 'clinic_id', 'patient_id'),
        Index('idx_raw_created_at', 'created_at'),
        Index('idx_raw_session', 'session_id'),
    )

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    raw_message_id = Column(Integer, ForeignKey('raw_messages.id'))
    session_id = Column(Integer, ForeignKey('sessions.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    intent_type = Column(String(50))
    objection_category = Column(String(50), nullable=True)
    service = Column(String(50))
    extracted_question = Column(Text)
    lead_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (
        Index('idx_event_clinic_patient', 'clinic_id', 'patient_id'),
        Index('idx_event_created', 'created_at'),
        Index('idx_event_session', 'session_id'),
    )

# سایر مدل‌ها (PatientProfile, PatientMemory, ConversationState, Lead, ...) بدون تغییر می‌مانند.
# (برای حفظ اختصار، بقیه مدل‌ها را از نسخه قبلی بگیرید – فقط دو جدول بالا تغییر کردند)
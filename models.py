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
    __table_args__ = (
        Index('idx_session_patient_active', 'patient_id', 'is_active'),
        Index('idx_session_last_activity', 'last_activity'),
    )


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
        Index('idx_raw_patient', 'patient_id'),
        Index('idx_raw_session', 'session_id'),
        Index('idx_raw_created', 'created_at'),
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
        Index('idx_event_patient', 'patient_id'),
        Index('idx_event_session', 'session_id'),
        Index('idx_event_created', 'created_at'),
    )


class PatientProfile(Base):
    __tablename__ = 'patient_profiles'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), unique=True)
    fear_level = Column(Integer, default=0)
    trust_level = Column(Integer, default=5)
    price_sensitivity = Column(Integer, default=5)
    moving_avg_fear = Column(Float, default=0.0)
    moving_avg_trust = Column(Float, default=5.0)
    moving_avg_price_sensitivity = Column(Float, default=5.0)
    conversation_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PatientMemory(Base):
    __tablename__ = 'patient_memories'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    memory_type = Column(String(50))
    memory_text = Column(Text)
    importance_score = Column(Integer, default=5)
    mention_count = Column(Integer, default=1)
    confidence = Column(Float, default=0.0)
    source = Column(String(50), default='llm')
    embedding_blob = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (
        Index('idx_memory_patient', 'patient_id'),
        Index('idx_memory_importance', 'importance_score'),
    )


class ConversationState(Base):
    __tablename__ = 'conversation_states'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    current_goal = Column(String(50))
    missing_information = Column(JSON)
    conversation_stage = Column(String(50))
    next_best_question = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    event_id = Column(Integer, ForeignKey('events.id'))
    service = Column(String(50))
    lead_score = Column(Float)
    pipeline_stage = Column(String(50), default='new')
    objection_category = Column(String(50), nullable=True)
    recovery_attempts = Column(Integer, default=0)
    last_followup = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (
        Index('idx_lead_patient', 'patient_id'),
        Index('idx_lead_stage', 'pipeline_stage'),
    )


class PipelineHistory(Base):
    __tablename__ = 'pipeline_history'
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    stage = Column(String(50))
    changed_at = Column(DateTime, default=datetime.utcnow)
    changed_by = Column(Integer, ForeignKey('staff.id'), nullable=True)


class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    lead_id = Column(Integer, ForeignKey('leads.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    service = Column(String(50))
    appointment_date = Column(DateTime)
    status = Column(String(50))
    revenue = Column(Float, nullable=True)
    reminder_sent = Column(Boolean, default=False)
    no_show = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (
        Index('idx_appointment_date', 'appointment_date'),
        Index('idx_appointment_status', 'status'),
    )


class AppointmentRequest(Base):
    __tablename__ = 'appointment_requests'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    lead_id = Column(Integer, ForeignKey('leads.id'))
    suggested_date = Column(DateTime)
    status = Column(String(20), default='pending')
    confirmed_date = Column(DateTime, nullable=True)
    confirmed_by = Column(Integer, ForeignKey('staff.id'), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ServicePrice(Base):
    __tablename__ = 'service_prices'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    service = Column(String(50))
    price = Column(Float)
    effective_date = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


class KnowledgeItem(Base):
    __tablename__ = 'knowledge_items'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    question_text = Column(Text)
    answer_text = Column(Text)
    service = Column(String(50))
    version = Column(Integer, default=1)
    effective_date = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_by = Column(Integer, ForeignKey('staff.id'), nullable=True)


class DoctorEdit(Base):
    __tablename__ = 'doctor_edits'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    original_answer = Column(Text)
    edited_answer = Column(Text)
    question_text = Column(Text)
    staff_id = Column(Integer, ForeignKey('staff.id'))
    created_at = Column(DateTime, default=datetime.utcnow)


class OutcomePattern(Base):
    __tablename__ = 'outcome_patterns'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    answer_pattern_hash = Column(String(64))
    booking_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)


class DailyKPI(Base):
    __tablename__ = 'daily_kpi'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    date = Column(DateTime)
    messages_count = Column(Integer, default=0)
    leads_count = Column(Integer, default=0)
    booked_count = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)
    lost_count = Column(Integer, default=0)
    no_show_count = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    lost_revenue = Column(Float, default=0.0)
    top_objections = Column(Text)
    top_services = Column(Text)
    conversion_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class EscalationLog(Base):
    __tablename__ = 'escalation_logs'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    session_id = Column(Integer, ForeignKey('sessions.id'))
    reason = Column(String(100))
    trigger = Column(String(200))
    message_id = Column(Integer, ForeignKey('raw_messages.id'), nullable=True)
    escalated_to = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class HumanCorrection(Base):
    __tablename__ = 'human_corrections'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    staff_id = Column(Integer, ForeignKey('staff.id'))
    field_name = Column(String(50))
    original_value = Column(Text)
    corrected_value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemMetric(Base):
    __tablename__ = 'system_metrics'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'), nullable=True)
    date = Column(DateTime)
    total_messages = Column(Integer, default=0)
    llm_calls = Column(Integer, default=0)
    llm_cost = Column(Float, default=0.0)
    human_handoffs = Column(Integer, default=0)
    medical_flags = Column(Integer, default=0)
    bookings = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ClinicWorkingHours(Base):
    __tablename__ = 'clinic_working_hours'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    start_time = Column(Time)
    end_time = Column(Time)
    active_timeout_minutes = Column(Integer, default=30)


class FollowupWindow(Base):
    __tablename__ = 'followup_windows'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    service = Column(String(50))
    days_after = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class RetentionPolicy(Base):
    __tablename__ = 'retention_policies'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    data_type = Column(String(50))
    retention_days = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class DataConsent(Base):
    __tablename__ = 'data_consents'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    consent_given = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class FeatureFlag(Base):
    __tablename__ = 'feature_flags'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    feature_name = Column(String(100))
    is_active = Column(Boolean, default=False)
    mode = Column(String(20), default='disabled')


class ClinicPersona(Base):
    __tablename__ = 'clinic_personas'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    tone = Column(String(50), default='friendly')
    emoji_level = Column(Integer, default=2)
    formality = Column(String(50), default='semi-formal')
    receptionist_name = Column(String(100), default='سارا')
    created_at = Column(DateTime, default=datetime.utcnow)


class ConversationStyle(Base):
    __tablename__ = 'conversation_styles'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    style_name = Column(String(50), default='friendly')
    created_at = Column(DateTime, default=datetime.utcnow)


class ObjectionLog(Base):
    __tablename__ = 'objection_logs'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


# ========== مدل‌های Content Brain (اختیاری) ==========
class ContentAsset(Base):
    __tablename__ = 'content_assets'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    asset_type = Column(String(50))
    source = Column(String(50))
    file_url = Column(Text)
    tags = Column(JSON)
    approved_by = Column(Integer, ForeignKey('staff.id'), nullable=True)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class BrandProfile(Base):
    __tablename__ = 'brand_profiles'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    tone = Column(String(50))
    cta_style = Column(String(50))
    emoji_usage = Column(String(20))
    formality = Column(Float)
    hook_style = Column(String(50))
    colors = Column(JSON)
    fonts = Column(JSON)
    trained_at = Column(DateTime)


class VisualMemory(Base):
    __tablename__ = 'visual_memory'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    image_url = Column(Text)
    image_embedding_blob = Column(Text)
    location_type = Column(String(50))
    tags = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class BeforeAfter(Base):
    __tablename__ = 'before_after'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    before_image_url = Column(Text)
    after_image_url = Column(Text)
    service = Column(String(50))
    is_simulation = Column(Boolean, default=False)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DoctorVoice(Base):
    __tablename__ = 'doctor_voice'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    video_url = Column(Text)
    transcript = Column(Text)
    voice_embedding_blob = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ContentIdea(Base):
    __tablename__ = 'content_ideas'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    topic = Column(String(200))
    content_type = Column(String(50))
    generated_text = Column(Text)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)


class ContentWorkflow(Base):
    __tablename__ = 'content_workflow'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    content_idea_id = Column(Integer, ForeignKey('content_ideas.id'))
    status = Column(String(20))
    reviewer_id = Column(Integer, ForeignKey('staff.id'), nullable=True)
    published_url = Column(Text)
    performance_notes = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)
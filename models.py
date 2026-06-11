"""
مدل‌های دیتابیس (Database Models)
این فایل شامل تمام مدل‌های SQLAlchemy برای ساخت جداول دیتابیس است.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Index, Time
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


# ========== مدل‌های اصلی کلینیک ==========

class Clinic(Base):
    """کلینیک اصلی"""
    __tablename__ = 'clinics'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    subdomain = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Staff(Base):
    """کارکنان کلینیک (مالک، پزشک، منشی)"""
    __tablename__ = 'staff'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    telegram_id = Column(Integer, unique=True)
    name = Column(String(200))
    role = Column(String(50))   # owner, doctor, secretary
    invited_by = Column(Integer, ForeignKey('staff.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Patient(Base):
    """بیماران کلینیک"""
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    master_patient_id = Column(Integer, ForeignKey('patients.id'), nullable=True)
    name = Column(String(200))
    phone = Column(String(50))
    status = Column(String(20), default='active')   # active, cold, dead, spam, customer, archived, archived_cold, archived_dead
    memory_purged = Column(Boolean, default=False)
    summary_data = Column(JSON, nullable=True)
    preferred_language = Column(String(10), default='fa')
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class PatientAlias(Base):
    """نام‌های مستعار بیمار در پلتفرم‌های مختلف"""
    __tablename__ = 'patient_aliases'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    platform = Column(String(50))                    # telegram, instagram, whatsapp, website
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


# ========== مدل‌های مکالمه و جلسه ==========

class Session(Base):
    """جلسه مکالمه با بیمار"""
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
    """پیام‌های خام دریافتی"""
    __tablename__ = 'raw_messages'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    session_id = Column(Integer, ForeignKey('sessions.id'))
    platform = Column(String(50))
    external_user_id = Column(String(200))
    message_text = Column(Text)
    media_url = Column(Text, nullable=True)
    media_type = Column(String(20), nullable=True)   # photo, video, voice, document
    voice_duration = Column(Integer, nullable=True)
    transcript = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Event(Base):
    """رویدادهای پردازش شده (با Intent و امتیاز)"""
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    raw_message_id = Column(Integer, ForeignKey('raw_messages.id'))
    session_id = Column(Integer, ForeignKey('sessions.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    intent_type = Column(String(50))                 # inquiry, booking_request, price_check, complaint, content_question, small_talk
    objection_category = Column(String(50), nullable=True)   # price, fear, family, time, trust
    service = Column(String(50))                     # botox, filler, laser, mesotherapy, surgery
    extracted_question = Column(Text)
    lead_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


# ========== مدل‌های پروفایل و حافظه بیمار ==========

class PatientProfile(Base):
    """پروفایل احساسی و رفتاری بیمار"""
    __tablename__ = 'patient_profiles'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), unique=True)
    fear_level = Column(Integer, default=0)                # 0-10
    trust_level = Column(Integer, default=5)               # 0-10
    price_sensitivity = Column(Integer, default=5)         # 0-10
    moving_avg_fear = Column(Float, default=0.0)
    moving_avg_trust = Column(Float, default=5.0)
    moving_avg_price_sensitivity = Column(Float, default=5.0)
    conversation_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)


class PatientMemory(Base):
    """حافظه بلندمدت بیمار (رویدادهای مهم زندگی)"""
    __tablename__ = 'patient_memories'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    memory_type = Column(String(50))               # wedding, husband_opposed, bad_experience, important_date
    memory_text = Column(Text)
    importance_score = Column(Integer, default=5)  # 1-10
    mention_count = Column(Integer, default=1)
    confidence = Column(Float, default=0.0)        # 0-1
    source = Column(String(50), default='llm')     # llm, patient_stated, doctor_entered
    embedding_blob = Column(Text, nullable=True)   # ذخیره embedding برای جستجو
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ConversationState(Base):
    """وضعیت مکالمه فعلی (برای هدایت گفتگو)"""
    __tablename__ = 'conversation_states'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    current_goal = Column(String(50))              # booking, inquiry, objection_handling
    missing_information = Column(JSON)             # ["service", "area", "date"]
    conversation_stage = Column(String(50))        # greeting, qualification, consultation, booking, closing
    next_best_question = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


# ========== مدل‌های لید و پیپلاین فروش ==========

class Lead(Base):
    """لیدهای فروش"""
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    event_id = Column(Integer, ForeignKey('events.id'))
    service = Column(String(50))
    lead_score = Column(Float)
    pipeline_stage = Column(String(50), default='new')   # new, contacted, consultation, booked, completed, lost, no_show
    objection_category = Column(String(50), nullable=True)
    recovery_attempts = Column(Integer, default=0)
    last_followup = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PipelineHistory(Base):
    """تاریخچه تغییرات پیپلاین لید"""
    __tablename__ = 'pipeline_history'
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    stage = Column(String(50))
    changed_at = Column(DateTime, default=datetime.utcnow)
    changed_by = Column(Integer, ForeignKey('staff.id'), nullable=True)


# ========== مدل‌های نوبت‌دهی ==========

class Appointment(Base):
    """نوبت‌های قطعی"""
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    lead_id = Column(Integer, ForeignKey('leads.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    service = Column(String(50))
    appointment_date = Column(DateTime)
    status = Column(String(50))           # scheduled, confirmed, completed, canceled, no_show
    revenue = Column(Float, nullable=True)
    reminder_sent = Column(Boolean, default=False)
    no_show = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AppointmentRequest(Base):
    """درخواست‌های نوبت (در انتظار تأیید)"""
    __tablename__ = 'appointment_requests'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    lead_id = Column(Integer, ForeignKey('leads.id'))
    suggested_date = Column(DateTime)
    status = Column(String(20), default='pending')   # pending, confirmed, canceled
    confirmed_date = Column(DateTime, nullable=True)
    confirmed_by = Column(Integer, ForeignKey('staff.id'), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ========== مدل‌های قیمت و دانش ==========

class ServicePrice(Base):
    """قیمت خدمات در طول زمان (با نسخه‌بندی)"""
    __tablename__ = 'service_prices'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    service = Column(String(50))
    price = Column(Float)
    effective_date = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


class KnowledgeItem(Base):
    """دانشنامه کلینیک (سوال و پاسخ تأیید شده توسط پزشک)"""
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
    """اصلاحات پزشک بر روی پاسخ‌های AI (برای یادگیری)"""
    __tablename__ = 'doctor_edits'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    original_answer = Column(Text)
    edited_answer = Column(Text)
    question_text = Column(Text)
    staff_id = Column(Integer, ForeignKey('staff.id'))
    created_at = Column(DateTime, default=datetime.utcnow)


class OutcomePattern(Base):
    """الگوهای پاسخ و نرخ تبدیل آنها (برای یادگیری)"""
    __tablename__ = 'outcome_patterns'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    answer_pattern_hash = Column(String(64))
    booking_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)


# ========== مدل‌های آمار و رصد ==========

class DailyKPI(Base):
    """شاخص‌های کلیدی عملکرد روزانه"""
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
    top_objections = Column(Text)          # JSON string
    top_services = Column(Text)            # JSON string
    conversion_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemMetric(Base):
    """آمار سیستمی (تعداد پیام‌ها، هزینه LLM، ...)"""
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


# ========== مدل‌های امنیت و لاگ ==========

class EscalationLog(Base):
    """لاگ ارجاع به انسان (Human Handoff)"""
    __tablename__ = 'escalation_logs'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    session_id = Column(Integer, ForeignKey('sessions.id'))
    reason = Column(String(100))           # medical_risk, human_request, system_fallback
    trigger = Column(String(200))          # keyword or detected intent
    message_id = Column(Integer, ForeignKey('raw_messages.id'))
    escalated_to = Column(String(50))      # doctor, secretary
    created_at = Column(DateTime, default=datetime.utcnow)


class HumanCorrection(Base):
    """اصلاحات دستی منشی/پزشک بر روی خروجی AI"""
    __tablename__ = 'human_corrections'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    staff_id = Column(Integer, ForeignKey('staff.id'))
    field_name = Column(String(50))        # intent, service, objection
    original_value = Column(Text)
    corrected_value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """لاگ کامل تمام تغییرات (برای انطباق پزشکی)"""
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=True)
    action_type = Column(String(50))       # lead_status_change, price_update, patient_merge
    old_value = Column(Text)
    new_value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# ========== مدل‌های تنظیمات و پیکربندی ==========

class ClinicWorkingHours(Base):
    """ساعات کاری کلینیک (برای Quiet Hours)"""
    __tablename__ = 'clinic_working_hours'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    start_time = Column(Time)
    end_time = Column(Time)
    active_timeout_minutes = Column(Integer, default=30)


class FollowupWindow(Base):
    """زمان پیگیری بر اساس نوع خدمت"""
    __tablename__ = 'followup_windows'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    service = Column(String(50))
    days_after = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class RetentionPolicy(Base):
    """سیاست نگهداری داده (برای GDPR/حریم خصوصی)"""
    __tablename__ = 'retention_policies'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    data_type = Column(String(50))         # memory, raw_message, event
    retention_days = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class DataConsent(Base):
    """رضایت بیمار برای نگهداری داده"""
    __tablename__ = 'data_consents'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    consent_given = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class FeatureFlag(Base):
    """فعال/غیرفعال کردن ویژگی‌ها (برای آزمایش تدریجی)"""
    __tablename__ = 'feature_flags'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    feature_name = Column(String(100))
    is_active = Column(Boolean, default=False)
    mode = Column(String(20), default='disabled')   # active, observation, disabled


# ========== مدل‌های شخصیت مکالمه ==========

class ClinicPersona(Base):
    """شخصیت مکالمه کلینیک (لحن، سبک، نام پذیرنده)"""
    __tablename__ = 'clinic_personas'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    tone = Column(String(50), default='friendly')
    emoji_level = Column(Integer, default=2)          # 0-3
    formality = Column(String(50), default='semi-formal')
    receptionist_name = Column(String(100), default='سارا')
    created_at = Column(DateTime, default=datetime.utcnow)


class ConversationStyle(Base):
    """سبک مکالمه قابل انتخاب توسط کلینیک"""
    __tablename__ = 'conversation_styles'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    style_name = Column(String(50), default='friendly')   # friendly, luxury, professional, vip
    created_at = Column(DateTime, default=datetime.utcnow)


class ObjectionLog(Base):
    """ثبت اعتراضات بیماران برای تحلیل"""
    __tablename__ = 'objection_logs'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    category = Column(String(50))               # price, fear, family, time, trust
    created_at = Column(DateTime, default=datetime.utcnow)


# ========== مدل‌های Content Brain (اختیاری) ==========

class ContentAsset(Base):
    """دارایی‌های محتوایی (تصاویر، ویدیوها، نمونه استوری‌ها)"""
    __tablename__ = 'content_assets'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    asset_type = Column(String(50))             # image, video, caption, story_sample
    source = Column(String(50))                 # upload, competitor, suggestion
    file_url = Column(Text)
    tags = Column(JSON)
    approved_by = Column(Integer, ForeignKey('staff.id'), nullable=True)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class BrandProfile(Base):
    """پروفایل برند کلینیک (برای تولید محتوا)"""
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
    """حافظه بصری (تصاویر محیط کلینیک)"""
    __tablename__ = 'visual_memory'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    image_url = Column(Text)
    image_embedding_blob = Column(Text)
    location_type = Column(String(50))          # reception, waiting_room, injection_room
    tags = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class BeforeAfter(Base):
    """تصاویر قبل و بعد (با تأیید پزشک)"""
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
    """صدای پزشک (برای Clone)"""
    __tablename__ = 'doctor_voice'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    video_url = Column(Text)
    transcript = Column(Text)
    voice_embedding_blob = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ContentIdea(Base):
    """ایده‌های محتوایی تولید شده"""
    __tablename__ = 'content_ideas'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    topic = Column(String(200))
    content_type = Column(String(50))           # story, reel, post, caption
    generated_text = Column(Text)
    status = Column(String(20), default='pending')   # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)


class ContentWorkflow(Base):
    """گردش کاری تأیید محتوا"""
    __tablename__ = 'content_workflow'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    content_idea_id = Column(Integer, ForeignKey('content_ideas.id'))
    status = Column(String(20))                 # draft, review, approved, published
    reviewer_id = Column(Integer, ForeignKey('staff.id'), nullable=True)
    published_url = Column(Text)
    performance_notes = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)
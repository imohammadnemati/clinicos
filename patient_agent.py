"""
ماژول عامل بیمار (Patient Agent)
این ماژول مسئول پردازش پیام‌های دریافتی از بیماران است:
- استخراج اطلاعات با LLM
- محاسبه امتیاز لید
- ذخیره رویدادها
- تولید پاسخ طبیعی
- مدیریت حافظه و وضعیت مکالمه
- تشخیص نیاز به مداخله انسانی
"""

import google.generativeai as genai
import json
import re
from config import GEMINI_API_KEY, LEAD_THRESHOLD
from database import SessionLocal
from models import (
    Session as SessionModel,
    RawMessage,
    Event,
    Lead,
    AppointmentRequest,
    PipelineHistory,
    KnowledgeItem,
    OutcomePattern,
    Patient,
    PatientProfile,
    PatientMemory,
    ConversationState,
    EscalationLog
)
from identity_resolution import get_or_create_patient
from session_manager import get_or_create_session, update_session_activity
from lead_scorer import calculate_lead_score
from language_detector import detect_language
from medical_safety import check_medical_risk
from working_hours import can_auto_reply
from prefilter import is_trivial_message
from datetime import datetime
import hashlib
import logging

# تنظیم لاگر
logger = logging.getLogger(__name__)

# تنظیم کلید API جمینای
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# پرامپت استخراج فکت (JSON خالص)
FACTS_PROMPT = """
You are an AI assistant for a cosmetic clinic. Extract structured facts from the patient message.
Return ONLY valid JSON, no extra text, no explanation.
{
  "intent": "inquiry|booking_request|price_check",
  "service": "botox|filler|laser|mesotherapy|surgery|none",
  "price_interest": true/false,
  "urgency": "low|medium|high",
  "appointment_request": true/false,
  "objection_category": "price|fear|family|time|trust|none",
  "extracted_question": "...",
  "requires_human": true/false,
  "fear_level": 0-10 or null,
  "trust_level": 0-10 or null,
  "price_sensitivity": 0-10 or null,
  "important_memory": {"type": "wedding|husband_opposed|bad_experience|other", "text": "...", "importance": 1-10} or null
}
Message: {message}
JSON:
"""


async def generate_reply(clinic_id: int, question: str, patient_id: int, lang: str) -> str:
    """
    تولید پاسخ طبیعی با استفاده از دانش قبلی یا LLM
    """
    db = SessionLocal()
    now = datetime.utcnow()
    try:
        # جستجو در دانش قبلی
        knowledge = db.query(KnowledgeItem).filter(
            KnowledgeItem.clinic_id == clinic_id,
            KnowledgeItem.effective_date <= now,
            (KnowledgeItem.expires_at.is_(None) | (KnowledgeItem.expires_at > now))
        ).order_by(KnowledgeItem.version.desc()).all()
        
        for k in knowledge:
            if k.question_text and k.question_text in question:
                logger.debug(f"پاسخ از دانش قبلی برای سوال: {question[:50]}...")
                return k.answer_text
    except Exception as e:
        logger.error(f"خطا در جستجوی دانش: {e}")
    finally:
        db.close()
    
    # پاسخ با Gemini
    prompt = f"You are a clinic receptionist. Reply in {lang} language, briefly, naturally, no medical advice: {question}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"خطا در تولید پاسخ با Gemini: {e}")
        return "متشکرم. پیام شما ثبت شد. به زودی پاسخگو خواهیم بود."


async def process_patient_message(
    update,
    context,
    clinic_id: int,
    platform: str,
    external_user_id: str,
    raw_text: str,
    media_url: str = None,
    media_type: str = None,
    transcript: str = None,
    db=None
):
    """
    تابع اصلی پردازش پیام بیمار
    """
    if db is None:
        db = SessionLocal()
    
    try:
        user = update.effective_user
        username = user.username
        display_name = user.full_name
        
        # تشخیص زبان
        lang = detect_language(raw_text)
        
        # دریافت یا ایجاد بیمار
        patient_id = get_or_create_patient(
            clinic_id, platform, external_user_id,
            username, display_name, raw_text
        )
        
        # به‌روزرسانی زبان و زمان آخرین فعالیت بیمار
        patient = db.query(Patient).filter_by(id=patient_id).first()
        if patient:
            patient.preferred_language = lang
            patient.last_seen = datetime.utcnow()
            db.commit()
        
        # ایجاد یا دریافت جلسه
        session_id = get_or_create_session(clinic_id, patient_id)
        update_session_activity(session_id)
        
        # بررسی ایمنی پزشکی
        is_risk, risk_level = await check_medical_risk(raw_text)
        if is_risk:
            # ثبت لاگ ارجاع
            esc = EscalationLog(
                clinic_id=clinic_id,
                patient_id=patient_id,
                session_id=session_id,
                reason="medical_risk",
                trigger=risk_level,
                escalated_to="doctor",
                created_at=datetime.utcnow()
            )
            db.add(esc)
            db.commit()
            await update.message.reply_text(
                "⚠️ برای پاسخ به این سوال نیاز به بررسی پزشک دارید. لطفاً با کلینیک تماس بگیرید."
            )
            return
        
        # بررسی ساعات کاری و پاسخگویی
        can_reply = await can_auto_reply(clinic_id, session_id, db)
        if not can_reply:
            await update.message.reply_text(
                "🌙 سلام.\nپیام شما ثبت شد. همکاران ما از ساعت ۸ صبح پاسخگوی شما خواهند بود و در اولین فرصت با شما ارتباط می‌گیرند.\nشب خوش 🌷"
            )
            return
        
        # ذخیره پیام خام
        raw = RawMessage(
            clinic_id=clinic_id,
            patient_id=patient_id,
            session_id=session_id,
            platform=platform,
            external_user_id=external_user_id,
            message_text=raw_text,
            media_url=media_url,
            media_type=media_type,
            transcript=transcript,
            created_at=datetime.utcnow()
        )
        db.add(raw)
        db.flush()
        
        # مرحله 1: استخراج فکت با LLM
        facts_prompt = FACTS_PROMPT.format(message=raw_text)
        response = model.generate_content(facts_prompt)
        raw_json = response.text.strip()
        raw_json = re.sub(r'```json\n?', '', raw_json)
        raw_json = re.sub(r'```', '', raw_json)
        
        try:
            facts = json.loads(raw_json)
        except json.JSONDecodeError:
            facts = {
                "intent": "inquiry",
                "service": "none",
                "price_interest": False,
                "urgency": "low",
                "appointment_request": False,
                "objection_category": "none",
                "extracted_question": raw_text,
                "requires_human": False,
                "fear_level": None,
                "trust_level": None,
                "price_sensitivity": None,
                "important_memory": None
            }
        
        # بررسی نیاز به مداخله انسانی
        if facts.get("requires_human"):
            db.query(SessionModel).filter_by(id=session_id).update({
                "requires_human": True,
                "conversation_status": "human_required"
            })
            db.commit()
            await update.message.reply_text(
                "درخواست شما به منشی منتقل شد. لطفاً صبر کنید."
            )
            return
        
        # به‌روزرسانی پروفایل احساسی بیمار
        profile = db.query(PatientProfile).filter_by(patient_id=patient_id).first()
        if not profile:
            profile = PatientProfile(patient_id=patient_id)
            db.add(profile)
            db.flush()
        
        if facts.get('fear_level') is not None:
            profile.moving_avg_fear = profile.moving_avg_fear * 0.8 + facts['fear_level'] * 0.2
        if facts.get('trust_level') is not None:
            profile.moving_avg_trust = profile.moving_avg_trust * 0.8 + facts['trust_level'] * 0.2
        if facts.get('price_sensitivity') is not None:
            profile.moving_avg_price_sensitivity = profile.moving_avg_price_sensitivity * 0.8 + facts['price_sensitivity'] * 0.2
        profile.conversation_count += 1
        db.commit()
        
        # ذخیره حافظه مهم
        if facts.get('important_memory'):
            mem_data = facts['important_memory']
            memory = PatientMemory(
                patient_id=patient_id,
                memory_type=mem_data.get('type'),
                memory_text=mem_data.get('text'),
                importance_score=mem_data.get('importance', 5),
                mention_count=1,
                confidence=0.8,
                source='llm',
                created_at=datetime.utcnow()
            )
            db.add(memory)
            db.commit()
        
        # محاسبه امتیاز لید (بدون patient_id)
        lead_score = calculate_lead_score(
            intent=facts["intent"],
            service_interest=(facts["service"] != "none"),
            price_interest=facts["price_interest"],
            urgency=facts["urgency"],
            appointment_request=facts["appointment_request"],
            conversation_depth=profile.conversation_count
        )
        
        # ذخیره رویداد
        event = Event(
            clinic_id=clinic_id,
            raw_message_id=raw.id,
            session_id=session_id,
            patient_id=patient_id,
            intent_type=facts["intent"],
            objection_category=facts["objection_category"],
            service=facts["service"],
            extracted_question=facts.get("extracted_question"),
            lead_score=lead_score,
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.flush()
        
        # ایجاد لید در صورت امتیاز کافی
        if lead_score >= LEAD_THRESHOLD:
            existing_lead = db.query(Lead).filter_by(
                patient_id=patient_id,
                pipeline_stage='new'
            ).first()
            if not existing_lead:
                lead = Lead(
                    clinic_id=clinic_id,
                    patient_id=patient_id,
                    event_id=event.id,
                    service=facts["service"],
                    lead_score=lead_score,
                    objection_category=facts["objection_category"],
                    pipeline_stage='new'
                )
                db.add(lead)
                db.flush()
                
                ph = PipelineHistory(
                    lead_id=lead.id,
                    stage='new',
                    changed_at=datetime.utcnow()
                )
                db.add(ph)
                
                if facts["appointment_request"]:
                    app_req = AppointmentRequest(
                        clinic_id=clinic_id,
                        lead_id=lead.id,
                        suggested_date=datetime.utcnow(),
                        status='pending'
                    )
                    db.add(app_req)
                db.commit()
        
        # تولید پاسخ
        answer = await generate_reply(
            clinic_id,
            facts.get("extracted_question") or raw_text,
            patient_id,
            lang
        )
        
        # به‌روزرسانی Outcome Pattern برای یادگیری آینده
        ans_hash = hashlib.sha256(answer.encode()).hexdigest()
        pattern = db.query(OutcomePattern).filter_by(
            clinic_id=clinic_id,
            answer_pattern_hash=ans_hash
        ).first()
        if pattern:
            pattern.total_count += 1
        else:
            pattern = OutcomePattern(
                clinic_id=clinic_id,
                answer_pattern_hash=ans_hash,
                total_count=1
            )
            db.add(pattern)
        db.commit()
        
        # ارسال پاسخ
        await update.message.reply_text(answer)
        
    except Exception as e:
        logger.error(f"خطا در پردازش پیام بیمار: {e}")
        await update.message.reply_text(
            "خطایی رخ داده است. لطفاً دقایقی دیگر تلاش کنید."
        )
    finally:
        if db:
            db.close()
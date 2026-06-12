import json
import re
import requests
import asyncio
import hashlib
import logging
from datetime import datetime
from config import GROQ_API_KEY, LEAD_THRESHOLD
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
    EscalationLog
)
from identity_resolution import get_or_create_patient
from session_manager import get_or_create_session, update_session_activity
from lead_scorer import calculate_lead_score
from language_detector import detect_language
from medical_safety import check_medical_risk
from working_hours import can_auto_reply

logger = logging.getLogger(__name__)

# ========== Groq API Configuration ==========
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"   # یا "mixtral-8x7b-32768" (همچنان رایگان)

async def call_groq(prompt: str, max_retries: int = 2) -> str:
    """فراخوانی Groq API با retry و timeout"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 500
    }
    for attempt in range(max_retries):
        try:
            # استفاده از asyncio.to_thread برای جلوگیری از بلاک شدن حلقه رویداد
            resp = await asyncio.to_thread(
                requests.post, GROQ_URL, headers=headers, json=data, timeout=10
            )
            if resp.status_code == 200:
                return resp.json()['choices'][0]['message']['content'].strip()
            else:
                logger.warning(f"Groq error {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Groq attempt {attempt+1} failed: {e}")
        await asyncio.sleep(1)
    return "متشکرم. پیام شما ثبت شد. به زودی پاسخگو خواهیم بود."

# ========== Prompts ==========
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
  "important_memory": null
}
Message: {message}
JSON:
"""

async def generate_reply(clinic_id: int, question: str, patient_id: int, lang: str) -> str:
    """تولید پاسخ با استفاده از دانش قبلی یا Groq"""
    # جستجو در دانش تأیید شده
    db = SessionLocal()
    try:
        knowledge = db.query(KnowledgeItem).filter(
            KnowledgeItem.clinic_id == clinic_id,
            KnowledgeItem.effective_date <= datetime.utcnow()
        ).order_by(KnowledgeItem.version.desc()).all()
        for k in knowledge:
            if k.question_text and k.question_text in question:
                return k.answer_text
    finally:
        db.close()
    # اگر دانش نبود، از Groq بخواه
    prompt = f"You are a clinic receptionist. Reply in {lang}, briefly, naturally, no medical advice: {question}"
    return await call_groq(prompt)

# ========== تابع اصلی پردازش پیام ==========
async def process_patient_message(
    update,
    context,
    clinic_id: int,
    platform: str,
    external_user_id: str,
    raw_text: str,
    media_url=None,
    media_type=None,
    transcript=None,
    db=None
):
    if db is None:
        db = SessionLocal()

    try:
        user = update.effective_user
        lang = detect_language(raw_text)
        patient_id = get_or_create_patient(
            clinic_id, platform, external_user_id,
            user.username, user.full_name, raw_text
        )

        patient = db.query(Patient).filter_by(id=patient_id).first()
        if patient:
            patient.preferred_language = lang
            patient.last_seen = datetime.utcnow()

        session_id = get_or_create_session(clinic_id, patient_id)
        update_session_activity(session_id)

        # ایمنی پزشکی
        is_risk, risk_level = await check_medical_risk(raw_text)
        if is_risk:
            esc = EscalationLog(
                clinic_id=clinic_id, patient_id=patient_id, session_id=session_id,
                reason="medical_risk", trigger=risk_level, escalated_to="doctor"
            )
            db.add(esc)
            db.commit()
            await update.message.reply_text("⚠️ برای پاسخ به این سوال نیاز به بررسی پزشک دارید. لطفاً با کلینیک تماس بگیرید.")
            return

        # بررسی ساعات کاری
        if not await can_auto_reply(clinic_id, session_id, db):
            await update.message.reply_text("🌙 پیام شما ثبت شد. همکاران ما از ساعت ۸ صبح پاسخگوی شما خواهند بود.")
            db.rollback()
            return

        # ذخیره پیام خام
        raw = RawMessage(
            clinic_id=clinic_id, patient_id=patient_id, session_id=session_id,
            platform=platform, external_user_id=external_user_id,
            message_text=raw_text, media_url=media_url, media_type=media_type,
            transcript=transcript, created_at=datetime.utcnow()
        )
        db.add(raw)
        db.flush()

        # استخراج فکت با Groq
        facts_json = await call_groq(FACTS_PROMPT.format(message=raw_text))
        facts_json = re.sub(r'```json\n?|```', '', facts_json.strip())
        try:
            facts = json.loads(facts_json)
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

        if facts.get("requires_human"):
            db.query(SessionModel).filter_by(id=session_id).update({"requires_human": True})
            db.commit()
            await update.message.reply_text("درخواست شما به منشی منتقل شد. لطفاً صبر کنید.")
            return

        # به‌روزرسانی پروفایل بیمار
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
        profile.conversation_count = (profile.conversation_count or 0) + 1

        # ذخیره حافظه مهم
        if facts.get('important_memory'):
            mem = facts['important_memory']
            memory = PatientMemory(
                patient_id=patient_id,
                memory_type=mem.get('type'),
                memory_text=mem.get('text'),
                importance_score=mem.get('importance', 5),
                mention_count=1,
                confidence=0.8,
                source='llm',
                created_at=datetime.utcnow()
            )
            db.add(memory)

        # محاسبه امتیاز لید
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
            clinic_id=clinic_id, raw_message_id=raw.id, session_id=session_id,
            patient_id=patient_id, intent_type=facts["intent"],
            objection_category=facts["objection_category"], service=facts["service"],
            extracted_question=facts.get("extracted_question"), lead_score=lead_score,
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.flush()

        # ایجاد لید در صورت نیاز
        if lead_score >= LEAD_THRESHOLD:
            existing_lead = db.query(Lead).filter_by(patient_id=patient_id, pipeline_stage='new').first()
            if not existing_lead:
                lead = Lead(
                    clinic_id=clinic_id, patient_id=patient_id, event_id=event.id,
                    service=facts["service"], lead_score=lead_score,
                    objection_category=facts["objection_category"], pipeline_stage='new',
                    created_at=datetime.utcnow()
                )
                db.add(lead)
                db.flush()
                db.add(PipelineHistory(lead_id=lead.id, stage='new', changed_at=datetime.utcnow()))
                if facts["appointment_request"]:
                    db.add(AppointmentRequest(
                        clinic_id=clinic_id, lead_id=lead.id,
                        suggested_date=datetime.utcnow(), status='pending'
                    ))

        # تولید پاسخ
        answer = await generate_reply(clinic_id, facts.get("extracted_question") or raw_text, patient_id, lang)

        # ثبت الگوی پاسخ
        ans_hash = hashlib.sha256(answer.encode()).hexdigest()
        pattern = db.query(OutcomePattern).filter_by(clinic_id=clinic_id, answer_pattern_hash=ans_hash).first()
        if pattern:
            pattern.total_count += 1
        else:
            pattern = OutcomePattern(
                clinic_id=clinic_id, answer_pattern_hash=ans_hash,
                total_count=1, conversion_rate=0.0, updated_at=datetime.utcnow()
            )
            db.add(pattern)
        db.commit()

        # ارسال پاسخ
        await update.message.reply_text(answer)

    except Exception as e:
        logger.error(f"خطا در پردازش پیام بیمار: {e}", exc_info=True)
        db.rollback()
        await update.message.reply_text("خطایی رخ داده است. لطفاً دقایقی دیگر تلاش کنید.")
    finally:
        if db:
            db.close()
import json
import re
import asyncio
import hashlib
import logging
from datetime import datetime
import requests
from config import CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID, LEAD_THRESHOLD
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

# Cloudflare Workers AI endpoint (مدل جدید)
CLOUDFLARE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/meta/llama-3.2-3b-instruct"

async def call_cloudflare(prompt: str, max_retries: int = 2) -> str:
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.7
    }
    for attempt in range(max_retries):
        try:
            resp = await asyncio.to_thread(requests.post, CLOUDFLARE_URL, headers=headers, json=data, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                # بررسی ساختار پاسخ Cloudflare
                if 'result' in result and 'response' in result['result']:
                    return result['result']['response'].strip()
                elif 'result' in result and isinstance(result['result'], str):
                    return result['result'].strip()
                else:
                    logger.warning(f"Unexpected Cloudflare response format: {result}")
                    return "متشکرم. پیام شما ثبت شد. به زودی پاسخگو خواهیم بود."
            else:
                logger.warning(f"Cloudflare error {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Cloudflare attempt {attempt+1} failed: {e}")
        await asyncio.sleep(1)
    return "متشکرم. پیام شما ثبت شد. به زودی پاسخگو خواهیم بود."

# پرامپت استخراج فکت
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
    prompt = f"You are a clinic receptionist. Reply in {lang}, briefly, naturally, no medical advice: {question}"
    return await call_cloudflare(prompt)

async def process_patient_message(update, context, clinic_id, platform, external_user_id, raw_text,
                                  media_url=None, media_type=None, transcript=None, db=None):
    if db is None:
        db = SessionLocal()
    try:
        user = update.effective_user
        lang = detect_language(raw_text)
        patient_id = get_or_create_patient(clinic_id, platform, external_user_id,
                                           user.username, user.full_name, raw_text)
        patient = db.query(Patient).filter_by(id=patient_id).first()
        if patient:
            patient.preferred_language = lang
            patient.last_seen = datetime.utcnow()
        session_id = get_or_create_session(clinic_id, patient_id)
        update_session_activity(session_id)

        # Medical safety
        is_risk, risk_level = await check_medical_risk(raw_text)
        if is_risk:
            db.add(EscalationLog(clinic_id=clinic_id, patient_id=patient_id, session_id=session_id,
                                 reason="medical_risk", trigger=risk_level, escalated_to="doctor"))
            db.commit()
            await update.message.reply_text("⚠️ برای پاسخ به این سوال نیاز به بررسی پزشک دارید. لطفاً با کلینیک تماس بگیرید.")
            return

        # Working hours
        if not await can_auto_reply(clinic_id, session_id, db):
            await update.message.reply_text("🌙 پیام شما ثبت شد. همکاران ما از ساعت ۸ صبح پاسخگوی شما خواهند بود.")
            db.rollback()
            return

        # Save raw message
        raw = RawMessage(
            clinic_id=clinic_id, patient_id=patient_id, session_id=session_id,
            platform=platform, external_user_id=external_user_id,
            message_text=raw_text, media_url=media_url, media_type=media_type,
            transcript=transcript, created_at=datetime.utcnow()
        )
        db.add(raw)
        db.flush()

        # Extract facts using Cloudflare
        prompt_text = FACTS_PROMPT.replace("{message}", raw_text)
        facts_json = await call_cloudflare(prompt_text)
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

        # Update patient profile
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

        # Save important memory
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

        # Lead score
        lead_score = calculate_lead_score(
            intent=facts["intent"],
            service_interest=(facts["service"] != "none"),
            price_interest=facts["price_interest"],
            urgency=facts["urgency"],
            appointment_request=facts["appointment_request"],
            conversation_depth=profile.conversation_count
        )

        # Save event
        event = Event(
            clinic_id=clinic_id, raw_message_id=raw.id, session_id=session_id, patient_id=patient_id,
            intent_type=facts["intent"], objection_category=facts["objection_category"],
            service=facts["service"], extracted_question=facts.get("extracted_question"),
            lead_score=lead_score, created_at=datetime.utcnow()
        )
        db.add(event)
        db.flush()

        # Create lead if high score
        if lead_score >= LEAD_THRESHOLD:
            existing_lead = db.query(Lead).filter_by(patient_id=patient_id, pipeline_stage='new').first()
            if not existing_lead:
                lead = Lead(
                    clinic_id=clinic_id, patient_id=patient_id, event_id=event.id,
                    service=facts["service"], lead_score=lead_score,
                    objection_category=facts["objection_category"], pipeline_stage='new'
                )
                db.add(lead)
                db.flush()
                db.add(PipelineHistory(lead_id=lead.id, stage='new'))
                if facts.get("appointment_request"):
                    db.add(AppointmentRequest(clinic_id=clinic_id, lead_id=lead.id, suggested_date=datetime.utcnow()))

        # Generate reply
        answer = await generate_reply(clinic_id, facts.get("extracted_question") or raw_text, patient_id, lang)

        # Update outcome pattern
        ans_hash = hashlib.sha256(answer.encode()).hexdigest()
        pattern = db.query(OutcomePattern).filter_by(clinic_id=clinic_id, answer_pattern_hash=ans_hash).first()
        if pattern:
            pattern.total_count += 1
        else:
            pattern = OutcomePattern(
                clinic_id=clinic_id, answer_pattern_hash=ans_hash,
                total_count=1, conversion_rate=0.0
            )
            db.add(pattern)

        db.commit()
        await update.message.reply_text(answer)

    except Exception as e:
        logger.error(f"خطا در پردازش پیام: {e}", exc_info=True)
        db.rollback()
        await update.message.reply_text("خطایی رخ داده است. لطفاً دقایقی دیگر تلاش کنید.")
    finally:
        if db:
            db.close()
import google.generativeai as genai
import json
import re
from config import GEMINI_API_KEY, LEAD_THRESHOLD
from database import SessionLocal
from models import Session as SessionModel, RawMessage, Event, Lead, AppointmentRequest, PipelineHistory, KnowledgeItem, OutcomePattern, Patient, PatientProfile, PatientMemory, ConversationState, ClinicPersona, ConversationStyle, EscalationLog
from identity_resolution import get_or_create_patient
from session_manager import get_or_create_session
from lead_scorer import calculate_lead_score
from language_detector import detect_language
from personality_engine import get_persona
from medical_safety import check_medical_risk
from working_hours import can_auto_reply
from prefilter import is_trivial_message
from datetime import datetime
import hashlib

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

FACTS_PROMPT = """
You are an AI assistant for a cosmetic clinic. Extract structured facts from the patient message.
Return ONLY valid JSON, no extra text.
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

async def generate_reply(clinic_id, question, patient_id, lang):
    db = SessionLocal()
    now = datetime.utcnow()
    knowledge = db.query(KnowledgeItem).filter(
        KnowledgeItem.clinic_id == clinic_id,
        KnowledgeItem.effective_date <= now,
        (KnowledgeItem.expires_at.is_(None) | (KnowledgeItem.expires_at > now))
    ).order_by(KnowledgeItem.version.desc()).all()
    for k in knowledge:
        if k.question_text and k.question_text in question:
            db.close()
            return k.answer_text
    db.close()
    # fallback to Gemini
    prompt = f"You are a clinic receptionist. Reply in {lang} language, briefly, naturally, no medical advice: {question}"
    response = model.generate_content(prompt)
    return response.text.strip()

async def process_patient_message(update, context, clinic_id, platform, external_user_id, raw_text,
                                  media_url=None, media_type=None, transcript=None, db=None):
    if db is None:
        from database import SessionLocal
        db = SessionLocal()
    try:
        user = update.effective_user
        username = user.username
        display_name = user.full_name
        lang = detect_language(raw_text)
        patient_id = get_or_create_patient(clinic_id, platform, external_user_id, username, display_name, raw_text)
        # update preferred language
        patient = db.query(Patient).filter_by(id=patient_id).first()
        if patient:
            patient.preferred_language = lang
            patient.last_seen = datetime.utcnow()
            db.commit()
        session_id = get_or_create_session(clinic_id, patient_id)
        # medical safety
        is_risk, risk_level = await check_medical_risk(raw_text)
        if is_risk:
            # log escalation
            esc = EscalationLog(
                clinic_id=clinic_id, patient_id=patient_id, session_id=session_id,
                reason="medical_risk", trigger=risk_level, escalated_to="doctor",
                created_at=datetime.utcnow()
            )
            db.add(esc)
            db.commit()
            await update.message.reply_text("برای پاسخ به این سوال نیاز به بررسی پزشک دارید. لطفاً با کلینیک تماس بگیرید.")
            return
        # quiet hours check
        if not await can_auto_reply(clinic_id, session_id, db):
            await update.message.reply_text("سلام 🌷\nپیام شما ثبت شد. همکاران ما از ساعت ۸ صبح پاسخگوی شما خواهند بود.")
            return
        # save raw message
        raw = RawMessage(
            clinic_id=clinic_id, patient_id=patient_id, session_id=session_id,
            platform=platform, external_user_id=external_user_id,
            message_text=raw_text, media_url=media_url, media_type=media_type,
            transcript=transcript, created_at=datetime.utcnow()
        )
        db.add(raw)
        db.flush()
        # extract facts
        facts_prompt = FACTS_PROMPT.format(message=raw_text)
        response = model.generate_content(facts_prompt)
        raw_json = response.text.strip()
        raw_json = re.sub(r'```json\n?', '', raw_json)
        raw_json = re.sub(r'```', '', raw_json)
        try:
            facts = json.loads(raw_json)
        except:
            facts = {"intent": "inquiry", "service": "none", "price_interest": False, "urgency": "low",
                     "appointment_request": False, "objection_category": "none", "extracted_question": raw_text,
                     "requires_human": False, "fear_level": None, "trust_level": None, "price_sensitivity": None,
                     "important_memory": None}
        if facts.get("requires_human"):
            sess = db.query(SessionModel).filter_by(id=session_id).first()
            if sess:
                sess.requires_human = True
                db.commit()
            await update.message.reply_text("درخواست شما به منشی منتقل شد. لطفاً صبر کنید.")
            return
        # update patient profile (moving average)
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
        # store important memory
        if facts.get('important_memory'):
            mem_data = facts['important_memory']
            mem = PatientMemory(
                patient_id=patient_id,
                memory_type=mem_data.get('type'),
                memory_text=mem_data.get('text'),
                importance_score=mem_data.get('importance', 5),
                mention_count=1,
                confidence=0.8,
                source='llm',
                created_at=datetime.utcnow()
            )
            db.add(mem)
            db.commit()
        # lead score
        lead_score = calculate_lead_score(
            intent=facts["intent"],
            service_interest=(facts["service"] != "none"),
            price_interest=facts["price_interest"],
            urgency=facts["urgency"],
            appointment_request=facts["appointment_request"],
            conversation_depth=profile.conversation_count
        )
        # save event
        event = Event(
            clinic_id=clinic_id, raw_message_id=raw.id, session_id=session_id, patient_id=patient_id,
            intent_type=facts["intent"], objection_category=facts["objection_category"],
            service=facts["service"], extracted_question=facts.get("extracted_question"),
            lead_score=lead_score, created_at=datetime.utcnow()
        )
        db.add(event)
        db.flush()
        # create lead if high score
        if lead_score >= LEAD_THRESHOLD:
            existing = db.query(Lead).filter_by(patient_id=patient_id, pipeline_stage='new').first()
            if not existing:
                lead = Lead(
                    clinic_id=clinic_id, patient_id=patient_id, event_id=event.id,
                    service=facts["service"], lead_score=lead_score,
                    objection_category=facts["objection_category"], pipeline_stage='new'
                )
                db.add(lead)
                db.flush()
                ph = PipelineHistory(lead_id=lead.id, stage='new', changed_at=datetime.utcnow())
                db.add(ph)
                if facts["appointment_request"]:
                    app_req = AppointmentRequest(clinic_id=clinic_id, lead_id=lead.id, suggested_date=datetime.utcnow())
                    db.add(app_req)
                db.commit()
        # generate reply
        answer = await generate_reply(clinic_id, facts.get("extracted_question") or raw_text, patient_id, lang)
        # update outcome pattern
        ans_hash = hashlib.sha256(answer.encode()).hexdigest()
        pattern = db.query(OutcomePattern).filter_by(clinic_id=clinic_id, answer_pattern_hash=ans_hash).first()
        if pattern:
            pattern.total_count += 1
        else:
            pattern = OutcomePattern(clinic_id=clinic_id, answer_pattern_hash=ans_hash, total_count=1)
            db.add(pattern)
        db.commit()
        await update.message.reply_text(answer)
    finally:
        if db:
            db.close()
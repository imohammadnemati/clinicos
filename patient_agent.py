import json
import re
import asyncio
import hashlib
import logging
from datetime import datetime
import requests
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
    EscalationLog,
    ConversationState
)
from identity_resolution import get_or_create_patient
from session_manager import get_or_create_session, update_session_activity
from lead_scorer import calculate_lead_score
from language_detector import detect_language
from medical_safety import check_medical_risk
from working_hours import can_auto_reply

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

async def call_groq(prompt: str, max_retries: int = 2) -> str:
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
            resp = await asyncio.to_thread(requests.post, GROQ_URL, headers=headers, json=data, timeout=15)
            if resp.status_code == 200:
                return resp.json()['choices'][0]['message']['content'].strip()
            else:
                logger.warning(f"Groq error {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Groq attempt {attempt+1} failed: {e}")
        await asyncio.sleep(1)
    return "An error occurred. Please try again later."

# پرامپت استخراج فکت (بدون آکولاد برای format - با جایگزینی دستی)
FACTS_PROMPT = """
You are an AI assistant for a cosmetic clinic. Extract structured facts from the patient message.
Consider the previous conversation context if provided.
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
Important: Only set "requires_human": true if the patient explicitly asks to speak to a human, complains, or mentions a serious medical emergency.
Context from previous conversation: {context}
Current message: {message}
JSON:
"""

REPLY_PROMPTS = {
    'en': """You are a professional, warm, and friendly receptionist at a cosmetic clinic.
You speak to clients in English, naturally and conversationally, as if you are a real human.
Never say "I am a robot" or "artificial intelligence". Keep responses short, polite, and helpful.
Use the conversation history to provide coherent answers.
If the user asks about prices, say: "The price depends on the area and number of units. Could you please tell me which area you're interested in?"
If the user asks medical questions that require a doctor, say: "For an accurate answer, you need to consult our doctor. Would you like to book a free consultation?"
If the user greets you (hello, hi, good morning), respond warmly and ask how you can help.
Only output the reply, nothing else.

Conversation history: {history}
Current question: {question}
Your reply:""",

    'fa': """تو یک منشی حرفه‌ای، گرم و صمیمی کلینیک زیبایی هستی. با مشتری‌ها به فارسی و کاملاً محاوره‌ای و طبیعی صحبت کن، طوری که انگار یک انسان واقعی است. هرگز نگو "ربات هستم" یا "هوش مصنوعی". از کلمات ساده و روان استفاده کن، کوتاه و مفید.
از تاریخچه گفتگو برای پاسخ‌های پیوسته استفاده کن. اگر درباره قیمت می‌پرسد بگو: "قیمت بستگی به ناحیه و شرایط داره، لطفاً ناحیه مد نظرتون رو بفرمایید." اگر سوال پزشکی است که نیاز به پزشک دارد بگو: "برای پاسخ دقیق نیاز به معاینه توسط پزشک داریم. می‌تونید وقت مشاوره بگیرید؟" اگر مشتری سلام کرد، گرم و دوستانه پاسخ بده.
لطفاً فقط پاسخ را بنویس، بدون توضیح اضافه.

تاریخچه گفتگو: {history}
سوال بیمار: {question}
پاسخ تو:""",

    'ar': """أنت موظف استقبال محترم و ودود في عيادة تجميل. تتحدث مع العملاء بالعربية، بشكل طبيعي ومحادث، كما لو كنت إنساناً حقيقياً. لا تقل أبداً "أنا روبوت" أو "ذكاء اصطناعي". استخدم كلمات بسيطة وسلسة، قصيرة ومفيدة.
استخدم تاريخ المحادثة للإجابة المستمرة. إذا سأل عن الأسعار قل: "السعر يعتمد على المنطقة وعدد الوحدات. هل تخبرني بالمنطقة التي تهتم بها؟" إذا سأل أسئلة طبية تحتاج إلى طبيب قل: "للحصول على إجابة دقيقة، تحتاج إلى استشارة طبيبنا. هل ترغب في حجز استشارة مجانية؟" إذا رحب بك المستخدم (مرحباً، أهلين)، رد بحرارة واسأل كيف يمكنك المساعدة. فقط أخرج الرد، لا شيء إضافي.

تاريخ المحادثة: {history}
سؤال المريض: {question}
ردك:"""
}

async def get_conversation_context(session_id: int, db) -> str:
    state = db.query(ConversationState).filter_by(session_id=session_id).first()
    if not state:
        return ""
    context = ""
    if state.current_goal:
        context += f"User is interested in: {state.current_goal}. "
    if state.missing_information:
        context += f"Missing info: {state.missing_information}. "
    return context

async def update_conversation_state(session_id: int, service: str, intent: str, db):
    state = db.query(ConversationState).filter_by(session_id=session_id).first()
    if not state:
        state = ConversationState(session_id=session_id)
        db.add(state)
    if service and service != "none":
        state.current_goal = service
    state.conversation_stage = intent
    state.updated_at = datetime.utcnow()
    db.commit()

async def generate_reply(clinic_id: int, question: str, patient_id: int, lang: str, history: str = "") -> str:
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
    prompt = REPLY_PROMPTS.get(lang, REPLY_PROMPTS['en']).format(history=history, question=question)
    return await call_groq(prompt)

async def process_patient_message(update, context, clinic_id, platform, external_user_id, raw_text,
                                  media_url=None, media_type=None, transcript=None, db=None):
    if db is None:
        db = SessionLocal()
    try:
        if raw_text.strip().startswith('/start'):
            await update.message.reply_text("Hello! 🌷 Welcome to our clinic. How can I assist you today?")
            return

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

        is_risk, risk_level = await check_medical_risk(raw_text)
        if is_risk:
            db.add(EscalationLog(clinic_id=clinic_id, patient_id=patient_id, session_id=session_id,
                                 reason="medical_risk", trigger=risk_level, escalated_to="doctor"))
            db.commit()
            risk_msg = {
                'fa': "⚠️ برای پاسخ به این سوال نیاز به بررسی پزشک دارید. لطفاً با کلینیک تماس بگیرید.",
                'en': "⚠️ This question requires a doctor's review. Please contact the clinic.",
                'ar': "⚠️ هذا السؤال يحتاج إلى مراجعة الطبيب. يرجى الاتصال بالعيادة."
            }.get(lang, "⚠️ This question requires a doctor's review. Please contact the clinic.")
            await update.message.reply_text(risk_msg)
            return

        if not await can_auto_reply(clinic_id, session_id, db):
            out_msg = {
                'fa': "🌙 پیام شما ثبت شد. همکاران ما از ساعت ۸ صبح پاسخگو خواهند بود.",
                'en': "🌙 Your message has been recorded. Our team will respond from 8 AM.",
                'ar': "🌙 تم تسجيل رسالتك. سيقوم فريقنا بالرد اعتباراً من الساعة 8 صباحاً."
            }.get(lang, "🌙 Your message has been recorded. Our team will respond from 8 AM.")
            await update.message.reply_text(out_msg)
            db.rollback()
            return

        raw = RawMessage(
            clinic_id=clinic_id, patient_id=patient_id, session_id=session_id,
            platform=platform, external_user_id=external_user_id,
            message_text=raw_text, media_url=media_url, media_type=media_type,
            transcript=transcript, created_at=datetime.utcnow()
        )
        db.add(raw)
        db.flush()

        conversation_context = await get_conversation_context(session_id, db)

        # اصلاح کلیدی: استفاده از replace به جای format
        prompt_text = FACTS_PROMPT.replace("{context}", conversation_context).replace("{message}", raw_text)
        facts_json = await call_groq(prompt_text)
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

        # Fallback برای service با context
        if facts.get("service") in ["none", None] and conversation_context:
            if "botox" in conversation_context.lower():
                facts["service"] = "botox"
            elif "filler" in conversation_context.lower():
                facts["service"] = "filler"

        await update_conversation_state(session_id, facts.get("service"), facts.get("intent"), db)

        if facts.get("requires_human"):
            db.query(SessionModel).filter_by(id=session_id).update({"requires_human": True})
            db.commit()
            human_msg = {
                'fa': "درخواست شما به منشی منتقل شد. لطفاً صبر کنید.",
                'en': "Your request has been forwarded to our secretary. Please wait.",
                'ar': "تم تحويل طلبك إلى السكرتير. يرجى الانتظار."
            }.get(lang, "Your request has been forwarded to our secretary. Please wait.")
            await update.message.reply_text(human_msg)
            return

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

        lead_score = calculate_lead_score(
            intent=facts["intent"],
            service_interest=(facts["service"] != "none"),
            price_interest=facts["price_interest"],
            urgency=facts["urgency"],
            appointment_request=facts["appointment_request"],
            conversation_depth=profile.conversation_count
        )

        event = Event(
            clinic_id=clinic_id, raw_message_id=raw.id, session_id=session_id, patient_id=patient_id,
            intent_type=facts["intent"], objection_category=facts["objection_category"],
            service=facts["service"], extracted_question=facts.get("extracted_question"),
            lead_score=lead_score, created_at=datetime.utcnow()
        )
        db.add(event)
        db.flush()

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

        recent_events = db.query(Event).filter(
            Event.session_id == session_id
        ).order_by(Event.created_at.desc()).limit(3).all()
        history_text = "\n".join([f"User: {e.extracted_question}" for e in reversed(recent_events) if e.extracted_question])

        answer = await generate_reply(clinic_id, facts.get("extracted_question") or raw_text, patient_id, lang, history_text)

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
        logger.error(f"Error in process_patient_message: {e}", exc_info=True)
        db.rollback()
        await update.message.reply_text("An error occurred. Please try again later.")
    finally:
        if db:
            db.close()
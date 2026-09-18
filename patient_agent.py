"""
ClinicOS – Patient Message Agent
Core business logic: processes incoming patient messages, manages conversation state,
patient memory, lead scoring, and invokes the LLM router for AI responses.

The configured FreeLLMAPI proxy is used as the LLM provider.
Automatically saves new Q&A pairs to KnowledgeItem for future use.
"""

import json
import re
import hashlib
import logging
from datetime import datetime
from typing import Optional

from config import (
    LEAD_THRESHOLD,
    FREELLMAPI_API_KEY,
)
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
    ConversationState,
)
from identity_resolution import get_or_create_patient
from session_manager import get_or_create_session, update_session_activity
from lead_scorer import calculate_lead_score
from language_detector import detect_language
from medical_safety import check_medical_risk
from working_hours import can_auto_reply

# Import the LLM router and its dependencies
from llm.provider_router import ProviderRouter
from llm.provider_manager import ProviderManager
from llm.state_store import StateStore
from llm.cost_manager import CostManager
# Use the configured FreeLLMAPI provider
from llm.providers.freellmapi_provider import FreeLLMAPIProvider

logger = logging.getLogger(__name__)

# ---------- Helper function to ensure facts keys ----------
def ensure_facts_keys(facts: dict) -> dict:
    """Ensure all required keys exist in facts dict with default values."""
    default = {
        "intent": "inquiry",
        "service": "none",
        "price_interest": False,
        "urgency": "low",
        "appointment_request": False,
        "objection_category": "none",
        "extracted_question": "",
        "requires_human": False,
        "fear_level": None,
        "trust_level": None,
        "price_sensitivity": None,
        "important_memory": None,
    }
    for key, value in default.items():
        if key not in facts:
            facts[key] = value
    return facts

# ---------- Initialize LLM Router (once at module load) ----------
_state_store = StateStore()
_cost_manager = CostManager()

 # Build provider instances – configured FreeLLMAPI proxy
providers = {}
if FREELLMAPI_API_KEY:
    providers["freellmapi"] = FreeLLMAPIProvider()
    logger.info("FreeLLMAPI provider enabled")
else:
    logger.critical("FREELLMAPI_API_KEY not set. No LLM provider available.")

_provider_manager = ProviderManager(
    providers=providers,
    state_store=_state_store,
    cost_manager=_cost_manager,
)

_router = ProviderRouter(provider_manager=_provider_manager)

# ---------- Prompts ----------
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
    "en": """You are a professional, warm, and friendly receptionist at a cosmetic clinic.
You are already in a conversation with the patient. Do NOT start with a greeting unless this is the very first message.
Continue the conversation naturally. Keep responses short, polite, and helpful.
Use the conversation history to provide coherent answers.
If the user asks about prices, say: "The price depends on the area and number of units. Could you please tell me which area you're interested in?"
If the user asks medical questions that require a doctor, say: "For an accurate answer, you need to consult our doctor. Would you like to book a free consultation?"
Only output the reply, nothing else.

Conversation history (last exchanges):
{history}

Current patient message: {question}
Your reply:""",

    "fa": """تو یک منشی حرفه‌ای، گرم و صمیمی کلینیک زیبایی هستی. هم‌اکنون در حال گفتگو با بیمار هستی. مگر اینکه این اولین پیام گفتگو باشد، هیچ‌گاه با "سلام" شروع نکن. مکالمه را طبیعی ادامه بده.
از تاریخچه گفتگو برای پاسخ‌های پیوسته استفاده کن. تاریخچه شامل پیام‌های قبلی بیمار است.
اگر بیمار درباره قیمت پرسید بگو: "قیمت بستگی به ناحیه و شرایط داره، لطفاً ناحیه مد نظرتون رو بفرمایید."
اگر سوال پزشکی است که نیاز به پزشک دارد بگو: "برای پاسخ دقیق نیاز به معاینه توسط پزشک داریم. می‌تونید وقت مشاوره بگیرید؟"
فقط پاسخ را بنویس، بدون توضیح اضافه.

تاریخچه گفتگو (چند پیام آخر):
{history}

پیام فعلی بیمار: {question}
پاسخ تو:""",

    "ar": """أنت موظف استقبال محترم و ودود في عيادة تجميل. أنت الآن في محادثة مع المريض. لا تبدأ بـ "مرحباً" إلا إذا كانت أول رسالة. استمر في المحادثة بشكل طبيعي.
استخدم تاريخ المحادثة للإجابة المستمرة.
إذا سأل عن الأسعار قل: "السعر يعتمد على المنطقة وعدد الوحدات. هل تخبرني بالمنطقة التي تهتم بها؟"
إذا سأل أسئلة طبية تحتاج إلى طبيب قل: "للحصول على إجابة دقيقة، تحتاج إلى استشارة طبيبنا. هل ترغب في حجز استشارة مجانية؟"
فقط أخرج الرد، لا شيء إضافي.

تاريخ المحادثة (آخر رسالتين):
{history}

رسالة المريض الحالية: {question}
ردك:""",

    "az": """Sən peşəkar, isti və mehriban kosmetik klinikada katibəsən.
Hal-hazırda xəstə ilə söhbət edirsən. Bu ilk mesaj deyilsə, heç vaxt "salam" ilə başlama.
Söhbəti təbii davam etdir. Cavabları qısa, nəzakətli və faydalı saxla.
Söhbət tarixçəsindən ardıcıl cavablar üçün istifadə et.
Əgər istifadəçi qiymətlər haqqında soruşsa: "Qiymət bölgəyə və vahidlərin sayına görə dəyişir. Hansı bölgə ilə maraqlandığınızı deyə bilərsiniz?" de.
Əgər istifadəçi həkim tələb edən tibbi suallar verərsə: "Dəqiq cavab üçün həkimimizlə məsləhətləşməlisiniz. Pulsuz məsləhət üçün qeydiyyatdan keçmək istərdiniz?" de.
Yalnız cavabı yaz, başqa heç nə.

Söhbət tarixçəsi (son mesajlar):
{history}

Hazırkı xəstə mesajı: {question}
Cavabın:""",

    "tr": """Profesyonel, sıcak ve samimi bir güzellik kliniğinde resepsiyonistsin.
Şu anda bir hasta ile konuşuyorsun. Bu ilk mesaj değilse, asla "Merhaba" ile başlama.
Konuşmayı doğal bir şekilde sürdür. Cevapları kısa, nazik ve yardımsever tut.
Konuşma geçmişini tutarlı cevaplar için kullan.
Kullanıcı fiyatlar hakkında sorarsa: "Fiyat bölgeye ve ünite sayısına göre değişir. Hangi bölgeyle ilgilendiğinizi söyleyebilir misiniz?" de.
Kullanıcı doktor gerektiren tıbbi sorular sorarsa: "Doğru cevap için doktorumuza danışmanız gerekir. Ücretsiz danışmanlık için randevu almak ister misiniz?" de.
Sadece cevabı yaz, başka bir şey değil.

Konuşma geçmişi (son mesajlar):
{history}

Mevcut hasta mesajı: {question}
Cevabın:""",
}

# ---------- Helper Functions ----------
async def get_conversation_history(session_id: int, db, limit: int = 6) -> str:
    events = db.query(Event).filter(Event.session_id == session_id).order_by(Event.created_at.desc()).limit(limit).all()
    history_list = []
    for ev in reversed(events):
        if ev.extracted_question:
            history_list.append(f"Patient: {ev.extracted_question}")
    return "\n".join(history_list)


async def update_conversation_state(session_id: int, service: str, intent: str, objection: str, db):
    state = db.query(ConversationState).filter_by(session_id=session_id).first()
    if not state:
        state = ConversationState(session_id=session_id)
        db.add(state)
    if service and service != "none":
        state.current_goal = service
    state.conversation_stage = intent
    if objection and objection != "none":
        state.missing_information = {"fear_topic": objection}
    state.updated_at = datetime.utcnow()
    db.commit()


# ========== Auto-save knowledge ==========
async def save_to_knowledge(clinic_id: int, question: str, answer: str, db):
    """Save Q&A pair to KnowledgeItem for future reuse."""
    try:
        existing = db.query(KnowledgeItem).filter(
            KnowledgeItem.clinic_id == clinic_id,
            KnowledgeItem.question_text == question,
            KnowledgeItem.effective_date <= datetime.utcnow()
        ).first()
        if not existing:
            new_knowledge = KnowledgeItem(
                clinic_id=clinic_id,
                question_text=question[:500],
                answer_text=answer[:2000],
                service="general",
                version=1,
                effective_date=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            db.add(new_knowledge)
            db.commit()
            logger.info(f"✅ New knowledge saved: {question[:50]}...")
        else:
            # Update usage count or success rate if needed
            existing.usage_count += 1
            db.commit()
    except Exception as e:
        logger.warning(f"Failed to save knowledge: {e}")


async def generate_reply(clinic_id: int, question: str, patient_id: int, lang: str, history: str, db) -> str:
    """
    Generate a reply using knowledge base if available, otherwise use LLM.
    Automatically saves new Q&A pairs.
    """
    # First, check knowledge base
    try:
        knowledge = db.query(KnowledgeItem).filter(
            KnowledgeItem.clinic_id == clinic_id,
            KnowledgeItem.effective_date <= datetime.utcnow(),
        ).order_by(KnowledgeItem.version.desc()).all()
        for k in knowledge:
            if k.question_text and k.question_text in question:
                logger.info(f"📚 Answer from database: {k.question_text[:30]}...")
                return k.answer_text
    except Exception as e:
        logger.warning(f"Knowledge base query failed: {e}")

    # Not found, use LLM
    prompt = REPLY_PROMPTS.get(lang, REPLY_PROMPTS["en"]).format(history=history, question=question)
    try:
        answer = await _router.generate(prompt, task="conversation")
        # Save for future
        await save_to_knowledge(clinic_id, question, answer, db)
        return answer
    except Exception as e:
        logger.error(f"Router generate failed: {e}")
        return "⚠️ خطا در ارتباط با هوش مصنوعی. لطفاً دوباره تلاش کنید."


# ---------- Main Processing Function ----------
async def process_patient_message(
    update,
    context,
    clinic_id,
    platform,
    external_user_id,
    raw_text,
    media_url=None,
    media_type=None,
    transcript=None,
    db=None,
    lang: Optional[str] = None,
):
    if db is None:
        db = SessionLocal()
    try:
        if raw_text.strip().startswith("/start"):
            await update.message.reply_text("Hello! 🌷 Welcome to our clinic. How can I assist you today?")
            return

        user = update.effective_user
        if lang is None:
            lang = detect_language(raw_text)

        patient_id = get_or_create_patient(
            clinic_id, platform, external_user_id, user.username, user.full_name, raw_text
        )
        patient = db.query(Patient).filter_by(id=patient_id).first()
        if patient:
            patient.preferred_language = lang
            patient.last_seen = datetime.utcnow()
        session_id = get_or_create_session(clinic_id, patient_id)
        update_session_activity(session_id)

        # Medical safety (keyword-based only)
        is_risk, risk_level = await check_medical_risk(raw_text)
        if is_risk:
            db.add(
                EscalationLog(
                    clinic_id=clinic_id,
                    patient_id=patient_id,
                    session_id=session_id,
                    reason="medical_risk",
                    trigger=risk_level,
                    escalated_to="doctor",
                )
            )
            db.commit()
            risk_msg = {
                "fa": "⚠️ برای پاسخ به این سوال نیاز به بررسی پزشک دارید. لطفاً با کلینیک تماس بگیرید.",
                "en": "⚠️ This question requires a doctor's review. Please contact the clinic.",
                "ar": "⚠️ هذا السؤال يحتاج إلى مراجعة الطبيب. يرجى الاتصال بالعيادة.",
                "az": "⚠️ Bu suala cavab vermək üçün həkim nəzərindən keçirməlidir. Klinika ilə əlaqə saxlayın.",
                "tr": "⚠️ Bu soru doktorun değerlendirmesini gerektirir. Lütfen klinikle iletişime geçin.",
            }.get(lang, "⚠️ This question requires a doctor's review. Please contact the clinic.")
            await update.message.reply_text(risk_msg)
            return

        # Working hours
        if not await can_auto_reply(clinic_id, session_id, db):
            out_msg = {
                "fa": "🌙 پیام شما ثبت شد. همکاران ما از ساعت ۸ صبح پاسخگو خواهند بود.",
                "en": "🌙 Your message has been recorded. Our team will respond from 8 AM.",
                "ar": "🌙 تم تسجيل رسالتك. سيقوم فريقنا بالرد اعتباراً من الساعة 8 صباحاً.",
                "az": "🌙 Mesajınız qeydə alındı. Komandamız səhər 8-dən cavab verəcək.",
                "tr": "🌙 Mesajınız kaydedildi. Ekibimiz sabah 8'den itibaren yanıt verecektir.",
            }.get(lang, "🌙 Your message has been recorded. Our team will respond from 8 AM.")
            await update.message.reply_text(out_msg)
            db.rollback()
            return

        # Save raw message
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
            created_at=datetime.utcnow(),
        )
        db.add(raw)
        db.flush()

        # Get conversation context
        conversation_history = await get_conversation_history(session_id, db, limit=6)
        prev_state = db.query(ConversationState).filter_by(session_id=session_id).first()
        context_str = ""
        if prev_state and prev_state.current_goal:
            context_str = f"User previously asked about {prev_state.current_goal}. "
        if prev_state and prev_state.missing_information and "fear_topic" in prev_state.missing_information:
            context_str += f"User previously expressed fear: {prev_state.missing_information['fear_topic']}. "

        # Extract facts
        prompt_text = FACTS_PROMPT.replace("{context}", context_str).replace("{message}", raw_text)
        try:
            facts_json = await _router.generate(prompt_text, task="facts_extraction")
        except Exception as e:
            logger.error(f"Router facts extraction failed: {e}")
            facts_json = "{}"
        facts_json = re.sub(r"```json\n?|```", "", facts_json.strip())
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
                "important_memory": None,
            }

        # Ensure all keys exist
        facts = ensure_facts_keys(facts)

        if facts.get("service") in ["none", None] and prev_state and prev_state.current_goal:
            facts["service"] = prev_state.current_goal

        await update_conversation_state(
            session_id, facts.get("service"), facts.get("intent"), facts.get("objection_category"), db
        )

        if facts.get("requires_human"):
            db.query(SessionModel).filter_by(id=session_id).update({"requires_human": True})
            db.commit()
            human_msg = {
                "fa": "درخواست شما به منشی منتقل شد. لطفاً صبر کنید.",
                "en": "Your request has been forwarded to our secretary. Please wait.",
                "ar": "تم تحويل طلبك إلى السكرتير. يرجى الانتظار.",
                "az": "Sorğunuz katibə göndərildi. Gözləyin.",
                "tr": "Talebiniz sekretere yönlendirildi. Lütfen bekleyin.",
            }.get(lang, "Your request has been forwarded to our secretary. Please wait.")
            await update.message.reply_text(human_msg)
            return

        # Update patient profile
        profile = db.query(PatientProfile).filter_by(patient_id=patient_id).first()
        if not profile:
            profile = PatientProfile(patient_id=patient_id)
            db.add(profile)
            db.flush()
        if facts.get("fear_level") is not None:
            profile.moving_avg_fear = profile.moving_avg_fear * 0.8 + facts["fear_level"] * 0.2
        if facts.get("trust_level") is not None:
            profile.moving_avg_trust = profile.moving_avg_trust * 0.8 + facts["trust_level"] * 0.2
        if facts.get("price_sensitivity") is not None:
            profile.moving_avg_price_sensitivity = profile.moving_avg_price_sensitivity * 0.8 + facts["price_sensitivity"] * 0.2
        profile.conversation_count = (profile.conversation_count or 0) + 1

        if facts.get("important_memory") and isinstance(facts["important_memory"], dict):
            mem = facts["important_memory"]
            memory = PatientMemory(
                patient_id=patient_id,
                memory_type=mem.get("type", "other"),
                memory_text=mem.get("text", ""),
                importance_score=mem.get("importance", 5),
                mention_count=1,
                confidence=0.8,
                source="llm",
                created_at=datetime.utcnow(),
            )
            db.add(memory)

        # Lead score
        lead_score = calculate_lead_score(
            intent=facts["intent"],
            service_interest=(facts["service"] != "none"),
            price_interest=facts["price_interest"],
            urgency=facts["urgency"],
            appointment_request=facts["appointment_request"],
            conversation_depth=profile.conversation_count,
        )

        # Save event
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
            created_at=datetime.utcnow(),
        )
        db.add(event)
        db.flush()

        if lead_score >= LEAD_THRESHOLD:
            existing_lead = db.query(Lead).filter_by(patient_id=patient_id, pipeline_stage="new").first()
            if not existing_lead:
                lead = Lead(
                    clinic_id=clinic_id,
                    patient_id=patient_id,
                    event_id=event.id,
                    service=facts["service"],
                    lead_score=lead_score,
                    objection_category=facts["objection_category"],
                    pipeline_stage="new",
                    created_at=datetime.utcnow(),
                )
                db.add(lead)
                db.flush()
                db.add(PipelineHistory(lead_id=lead.id, stage="new"))
                if facts.get("appointment_request"):
                    db.add(
                        AppointmentRequest(
                            clinic_id=clinic_id,
                            lead_id=lead.id,
                            suggested_date=datetime.utcnow(),
                            status="pending",
                        )
                    )

        # Generate reply
        answer = await generate_reply(
            clinic_id,
            facts.get("extracted_question") or raw_text,
            patient_id,
            lang,
            conversation_history,
            db  # pass db for knowledge saving
        )

        # Update outcome pattern
        ans_hash = hashlib.sha256(answer.encode()).hexdigest()
        pattern = db.query(OutcomePattern).filter_by(
            clinic_id=clinic_id, answer_pattern_hash=ans_hash
        ).first()
        if pattern:
            pattern.total_count += 1
        else:
            pattern = OutcomePattern(
                clinic_id=clinic_id,
                answer_pattern_hash=ans_hash,
                total_count=1,
                conversion_rate=0.0,
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

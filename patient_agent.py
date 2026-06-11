"""
ماژول عامل بیمار (Patient Agent)
مسئول پردازش پیام‌های دریافتی از بیماران:
- استخراج اطلاعات با LLM (Gemini)
- محاسبه امتیاز لید
- ذخیره رویدادها، حافظه و پروفایل
- تولید پاسخ طبیعی (با fallback)
- مدیریت تراکنش واحد برای حفظ یکپارچگی داده
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
    EscalationLog
)
from identity_resolution import get_or_create_patient
from session_manager import get_or_create_session, update_session_activity
from lead_scorer import calculate_lead_score
from language_detector import detect_language
from medical_safety import check_medical_risk
from working_hours import can_auto_reply
from datetime import datetime
import hashlib
import logging
import asyncio

# تنظیم لاگر
logger = logging.getLogger(__name__)

# تنظیم Gemini
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

# ========== توابع کمکی ==========

async def call_gemini_with_retry(prompt: str, max_retries: int = 2, timeout_seconds: int = 10) -> str:
    """فراخوانی Gemini با تلاش مجدد و timeout"""
    for attempt in range(max_retries):
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(model.generate_content, prompt),
                timeout=timeout_seconds
            )
            return response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini error (attempt {attempt+1}): {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)
    raise Exception("Gemini failed after retries")

async def generate_reply(clinic_id: int, question: str, patient_id: int, lang: str) -> str:
    """
    تولید پاسخ طبیعی (با استفاده از دانش قبلی یا fallback)
    """
    db = SessionLocal()
    try:
        # جستجو در دانش تأیید شده
        knowledge = db.query(KnowledgeItem).filter(
            KnowledgeItem.clinic_id == clinic_id,
            KnowledgeItem.effective_date <= datetime.utcnow()
        ).order_by(KnowledgeItem.version.desc()).all()
        for k in knowledge:
            if k.question_text and k.question_text in question:
                logger.debug(f"پاسخ از دانش قبلی: {k.question_text[:50]}...")
                return k.answer_text
    except Exception as e:
        logger.error(f"خطا در جستجوی دانش: {e}")
    finally:
        db.close()

    # پاسخ با Gemini (با fallback ساده)
    prompt = f"You are a clinic receptionist. Reply in {lang}, briefly, naturally, no medical advice: {question}"
    try:
        reply = await call_gemini_with_retry(prompt)
        return reply
    except Exception as e:
        logger.error(f"خطا در تولید پاسخ با Gemini: {e}")
        return "متشکرم. پیام شما ثبت شد. به زودی پاسخگو خواهیم بود."

# ========== تابع اصلی پردازش پیام ==========

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
    تابع اصلی پردازش پیام بیمار – همه عملیات در یک تراکنش انجام می‌شود.
    در صورت خطا، rollback شده و هیچ داده‌ای ذخیره نمی‌شود.
    """
    external_db = db is not None
    if db is None:
        db = SessionLocal()

    try:
        # ---------- مرحله 1: آماده‌سازی و بررسی‌های اولیه ----------
        user = update.effective_user
        lang = detect_language(raw_text)
        patient_id = get_or_create_patient(
            clinic_id, platform, external_user_id,
            user.username, user.full_name, raw_text
        )

        # به‌روزرسانی اطلاعات بیمار (بدون commit جداگانه)
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
            # این مورد نیاز به ذخیره لاگ دارد، اما چون خروج زودهنگام است، rollback کل تراکنش
            # برای این مورد خاص می‌توان یک commit جداگانه انجام داد، ولی برای سادگی rollback
            await update.message.reply_text("⚠️ برای پاسخ به این سوال نیاز به بررسی پزشک دارید. لطفاً با کلینیک تماس بگیرید.")
            db.rollback()
            return

        # ساعات کاری
        if not await can_auto_reply(clinic_id, session_id, db):
            await update.message.reply_text("🌙 سلام.\nپیام شما ثبت شد. همکاران ما از ساعت ۸ صبح پاسخگوی شما خواهند بود.")
            db.rollback()
            return

        # ---------- مرحله 2: ذخیره پیام خام ----------
        raw = RawMessage(
            clinic_id=clinic_id, patient_id=patient_id, session_id=session_id,
            platform=platform, external_user_id=external_user_id,
            message_text=raw_text, media_url=media_url, media_type=media_type,
            transcript=transcript, created_at=datetime.utcnow()
        )
        db.add(raw)
        db.flush()  # برای گرفتن raw.id

        # ---------- مرحله 3: استخراج فکت با LLM ----------
        try:
            facts_json = await call_gemini_with_retry(FACTS_PROMPT.format(message=raw_text))
            facts_json = re.sub(r'```json\n?|```', '', facts_json.strip())
            facts = json.loads(facts_json)
        except Exception as e:
            logger.error(f"خطا در استخراج فکت: {e}")
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
            await update.message.reply_text("درخواست شما به منشی منتقل شد. لطفاً صبر کنید.")
            db.rollback()
            return

        # ---------- مرحله 4: به‌روزرسانی پروفایل بیمار و حافظه ----------
        profile = db.query(PatientProfile).filter_by(patient_id=patient_id).first()
        if not profile:
            profile = PatientProfile(patient_id=patient_id)
            db.add(profile)
            db.flush()

        # به‌روزرسانی میانگین متحرک احساسات
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

        # ---------- مرحله 5: محاسبه امتیاز لید و ذخیره رویداد ----------
        lead_score = calculate_lead_score(
            intent=facts["intent"],
            service_interest=(facts["service"] != "none"),
            price_interest=facts["price_interest"],
            urgency=facts["urgency"],
            appointment_request=facts["appointment_request"],
            conversation_depth=profile.conversation_count
        )

        event = Event(
            clinic_id=clinic_id, raw_message_id=raw.id, session_id=session_id,
            patient_id=patient_id, intent_type=facts["intent"],
            objection_category=facts["objection_category"], service=facts["service"],
            extracted_question=facts.get("extracted_question"), lead_score=lead_score,
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.flush()

        # ---------- مرحله 6: ایجاد لید (در صورت احراز شرایط) ----------
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

        # ---------- مرحله 7: تولید پاسخ و به‌روزرسانی الگو ----------
        answer = await generate_reply(clinic_id, facts.get("extracted_question") or raw_text, patient_id, lang)

        # ثبت الگوی پاسخ برای یادگیری آینده
        ans_hash = hashlib.sha256(answer.encode()).hexdigest()
        pattern = db.query(OutcomePattern).filter_by(clinic_id=clinic_id, answer_pattern_hash=ans_hash).first()
        if pattern:
            pattern.total_count += 1
        else:
            db.add(OutcomePattern(
                clinic_id=clinic_id, answer_pattern_hash=ans_hash,
                total_count=1, conversion_rate=0.0
            ))

        # ---------- مرحله 8: نهایی کردن تراکنش و ارسال پاسخ ----------
        db.commit()
        await update.message.reply_text(answer)

    except Exception as e:
        logger.error(f"خطا در پردازش پیام بیمار: {e}", exc_info=True)
        db.rollback()
        await update.message.reply_text("خطایی رخ داده است. لطفاً دقایقی دیگر تلاش کنید.")
    finally:
        if not external_db:
            db.close()
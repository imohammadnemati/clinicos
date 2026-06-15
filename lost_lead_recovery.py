"""
Lost Lead Recovery – Automatic follow‑up for leads that have gone cold.
Uses configured follow‑up windows per service and sends recovery messages
via Telegram. No LLM calls, only rule‑based logic.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from database import SessionLocal
from models import Lead, PatientAlias, Patient, FollowupWindow
from config import BOT_TOKEN, DEFAULT_FOLLOWUP_DAYS, SECOND_FOLLOWUP_DAYS, THIRD_FOLLOWUP_DAYS, MAX_RECOVERY_ATTEMPTS
import requests
import asyncio
import logging
import random

logger = logging.getLogger(__name__)


# ========== Telegram Sender ==========
async def send_telegram_message(chat_id: int, text: str) -> bool:
    """Send a message to a Telegram user."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        resp = await asyncio.to_thread(
            requests.post, url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10
        )
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Failed to send recovery message to {chat_id}: {e}")
        return False


# ========== Recovery Message Templates ==========
def get_recovery_message_template(objection_category: str, service: str, lang: str = 'fa') -> str:
    """Return a recovery message based on the objection category (price, fear, trust, etc.)."""
    templates = {
        'price': {
            'fa': [
                "سلام 🌷\nچند روز پیش درباره {service} سوال داشتید.\nاگر نگران هزینه هستید، می‌توانید شرایط اقساط یا مشاوره رایگان را بررسی کنیم.\nآیا همچنان تمایل دارید وقت بگیرید؟",
                "سلام مجدد 🌷\nهزینه {service} بسته به شرایط متفاوت است.\nبرای اطلاع دقیق، پیشنهاد می‌کنم یک مشاوره رایگان داشته باشید.\nچه روزی برای شما مناسبه؟"
            ],
            'en': [
                "Hello 🌷\nYou recently asked about {service}. If cost is a concern, we offer free consultation and payment plans.\nWould you still like to book an appointment?",
                "Hi again 🌷\nThe price of {service} depends on several factors. I recommend a free consultation to give you an accurate estimate.\nWhat day works for you?"
            ],
            'ar': [
                "مرحباً 🌷\nسألت مؤخراً عن {service}. إذا كانت التكلفة مصدر قلق، نقدم استشارة مجانية وخطط تقسيط.\nهل لا تزال ترغب في حجز موعد؟",
                "أهلاً مجدداً 🌷\nسعر {service} يعتمد على عوامل مختلفة. أنصح باستشارة مجانية لإعطائك تقديراً دقيقاً.\nأي يوم يناسبك؟"
            ]
        },
        'fear': {
            'fa': [
                "سلام 🌷\nنگرانی شما درباره {service} کاملاً طبیعی است.\nبسیاری از بیماران همین احساس را دارند.\nمی‌توانیم یک جلسه مشاوره رایگان برای رفع نگرانی‌تان ترتیب بدیم.\nنظر شما چیه؟",
                "🌷 درک می‌کنم که نگران هستید.\nپزشک ما با حوصله تمام مراحل رو توضیح میده.\nمی‌تونید یک جلسه مشاوره داشته باشید.\nموافقید؟"
            ],
            'en': [
                "Hello 🌷\nYour concern about {service} is completely normal. Many of our patients feel the same way.\nWould you like a free consultation to address your worries?",
                "🌷 I understand you're concerned. Our doctor explains every step carefully.\nHow about a free consultation?"
            ],
            'ar': [
                "مرحباً 🌷\nقلقك بشأن {service} طبيعي تماماً. العديد من مرضانا يشعرون بنفس الشيء.\nهل ترغب في استشارة مجانية لمعالجة مخاوفك؟",
                "🌷 أفهم أنك قلق. طبيبنا يشرح كل خطوة بعناية.\nماذا عن استشارة مجانية؟"
            ]
        },
        'trust': {
            'fa': [
                "سلام 🌷\nمی‌تونم نمونه کارها و نظرات بیماران قبلی رو براتون بفرستم.\nکیفیت کار و تجربه بیماران می‌تونه به تصمیم‌گیری شما کمک کنه.\nآیا مایلید اطلاعات بیشتری بفرستم؟",
                "🌷 اعتماد مهمترین چیزه.\nپزشک ما سال‌ها سابقه و تخصص در {service} داره.\nمی‌تونید یک مشاوره بدون تعهد داشته باشید."
            ],
            'en': [
                "Hello 🌷\nI can send you before/after photos and patient reviews.\nWould you like to see more information?",
                "🌷 Trust is everything. Our doctor has years of experience in {service}.\nYou can have a no‑obligation consultation."
            ],
            'ar': [
                "مرحباً 🌷\nيمكنني إرسال صور قبل/بعد وتقييمات المرضى.\nهل ترغب في رؤية المزيد من المعلومات؟",
                "🌷 الثقة هي كل شيء. طبيبنا لديه سنوات من الخبرة في {service}.\nيمكنك الحصول على استشارة بدون التزام."
            ]
        },
        'general': {
            'fa': [
                "سلام 🌷\nچند روز پیش درباره {service} سوال داشتید.\nآیا هنوز نیاز به راهنمایی دارید؟\nخوشحال میشم کمک کنم.",
                "سلام مجدد 🌷\nامیدوارم حالتون خوب باشه.\nفقط یادآوری کنم که اگر هنوز سوالی دارید، در خدمتم."
            ],
            'en': [
                "Hello 🌷\nYou recently asked about {service}. Do you still need assistance? I'm happy to help.",
                "Hi again 🌷\nJust a reminder that I'm here if you have any further questions."
            ],
            'ar': [
                "مرحباً 🌷\nسألت مؤخراً عن {service}. هل لا تزال بحاجة إلى مساعدة؟ يسعدني مساعدتك.",
                "أهلاً مجدداً 🌷\nمجرد تذكير بأنني هنا إذا كان لديك أي أسئلة أخرى."
            ]
        }
    }

    # Fallback to general if objection category not found
    category_templates = templates.get(objection_category, templates['general'])
    lang_templates = category_templates.get(lang, category_templates['fa'])
    return random.choice(lang_templates).format(service=service)


# ========== Follow‑up Window Helper ==========
def get_followup_days_for_service(service: str, clinic_id: int) -> int:
    """Get configured follow‑up days for a given service, falling back to defaults."""
    db = SessionLocal()
    try:
        window = db.query(FollowupWindow).filter_by(clinic_id=clinic_id, service=service).first()
        if window:
            return window.days_after
    except Exception as e:
        logger.error(f"Error fetching followup window: {e}")
    finally:
        db.close()
    # Fallback to global defaults based on service type
    defaults = {
        'botox': 5,
        'filler': 7,
        'laser': 10,
        'mesotherapy': 14,
        'surgery': 21,
        'none': DEFAULT_FOLLOWUP_DAYS
    }
    return defaults.get(service, DEFAULT_FOLLOWUP_DAYS)


# ========== Main Recovery Logic ==========
async def recover_lost_leads():
    """Scan for leads that need follow‑up and send recovery messages."""
    logger.info("🔄 Starting lost lead recovery scan...")
    db = SessionLocal()
    now = datetime.utcnow()

    try:
        # Get all leads that are still 'new' and haven't reached max attempts
        leads = db.query(Lead).filter(
            Lead.pipeline_stage == 'new',
            Lead.recovery_attempts < MAX_RECOVERY_ATTEMPTS
        ).all()

        recovered_count = 0
        skipped_count = 0

        for lead in leads:
            # Calculate next follow‑up date based on attempts
            followup_days = get_followup_days_for_service(lead.service, lead.clinic_id)
            if lead.recovery_attempts == 0:
                next_date = lead.created_at + timedelta(days=followup_days)
            elif lead.recovery_attempts == 1:
                next_date = lead.last_followup + timedelta(days=SECOND_FOLLOWUP_DAYS)
            else:
                next_date = lead.last_followup + timedelta(days=THIRD_FOLLOWUP_DAYS)

            if now < next_date:
                skipped_count += 1
                continue

            # Find patient alias (telegram)
            alias = db.query(PatientAlias).filter_by(
                patient_id=lead.patient_id, platform='telegram'
            ).first()
            if not alias or not alias.external_user_id:
                logger.warning(f"No telegram alias for lead {lead.id}")
                continue

            # Get patient preferred language
            patient = db.query(Patient).filter_by(id=lead.patient_id).first()
            lang = patient.preferred_language if patient else 'fa'

            # Select template based on objection category
            objection = lead.objection_category or 'general'
            message = get_recovery_message_template(objection, lead.service, lang)

            # Add attempt number context (optional)
            if lead.recovery_attempts == 0:
                message += "\n\n(Just a friendly reminder 🌷)"
            elif lead.recovery_attempts == 1:
                message += "\n\n(Still here to help if you need anything 🌷)"
            else:
                message += "\n\n(If you're no longer interested, just let me know – no problem 🌷)"

            # Send message
            success = await send_telegram_message(int(alias.external_user_id), message)
            if success:
                lead.recovery_attempts += 1
                lead.last_followup = now
                recovered_count += 1
                logger.info(f"Sent recovery message for lead {lead.id} (attempt {lead.recovery_attempts})")
                # Mark as lost if max attempts reached
                if lead.recovery_attempts >= MAX_RECOVERY_ATTEMPTS:
                    lead.pipeline_stage = 'lost'
                    logger.info(f"Lead {lead.id} marked as lost after {MAX_RECOVERY_ATTEMPTS} attempts")
                db.commit()
            await asyncio.sleep(0.5)  # rate limit

        logger.info(f"✅ Recovery scan finished: {recovered_count} messages sent, {skipped_count} skipped.")
    except Exception as e:
        logger.error(f"Error in recover_lost_leads: {e}")
        db.rollback()
    finally:
        db.close()


# ========== Manual Recovery (for admin commands) ==========
async def recover_specific_lead(lead_id: int, custom_message: Optional[str] = None) -> bool:
    """Manually trigger recovery for a specific lead (e.g., from admin panel)."""
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter_by(id=lead_id).first()
        if not lead:
            logger.error(f"Lead {lead_id} not found")
            return False

        alias = db.query(PatientAlias).filter_by(patient_id=lead.patient_id, platform='telegram').first()
        if not alias or not alias.external_user_id:
            logger.error(f"No telegram alias for lead {lead_id}")
            return False

        if custom_message:
            message = custom_message
        else:
            objection = lead.objection_category or 'general'
            patient = db.query(Patient).filter_by(id=lead.patient_id).first()
            lang = patient.preferred_language if patient else 'fa'
            message = get_recovery_message_template(objection, lead.service, lang)

        success = await send_telegram_message(int(alias.external_user_id), message)
        if success:
            lead.recovery_attempts += 1
            lead.last_followup = datetime.utcnow()
            db.commit()
            logger.info(f"Manual recovery for lead {lead_id} sent")
        return success
    except Exception as e:
        logger.error(f"Manual recovery error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


# ========== Utility Functions ==========
def get_leads_needing_recovery(clinic_id: int, days: int = 7) -> List[Dict]:
    """Return a list of leads that should be considered for recovery (for admin dashboard)."""
    db = SessionLocal()
    now = datetime.utcnow()
    cutoff = now - timedelta(days=days)
    try:
        leads = db.query(Lead, Patient).join(Patient).filter(
            Lead.clinic_id == clinic_id,
            Lead.pipeline_stage == 'new',
            Lead.recovery_attempts < MAX_RECOVERY_ATTEMPTS,
            Lead.created_at < cutoff
        ).all()
        result = []
        for lead, patient in leads:
            result.append({
                "id": lead.id,
                "patient_name": patient.name or "Unknown",
                "service": lead.service,
                "lead_score": lead.lead_score,
                "objection": lead.objection_category,
                "attempts": lead.recovery_attempts,
                "days_passed": (now - lead.created_at).days
            })
        return result
    finally:
        db.close()


def reset_recovery_attempts(lead_id: int) -> bool:
    """Reset recovery attempts (e.g., if patient responded)."""
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter_by(id=lead_id).first()
        if lead:
            lead.recovery_attempts = 0
            lead.pipeline_stage = 'new'
            db.commit()
            return True
        return False
    except Exception as e:
        logger.error(f"Reset attempts error: {e}")
        db.rollback()
        return False
    finally:
        db.close()
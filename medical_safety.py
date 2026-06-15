"""
ماژول ایمنی پزشکی (Medical Safety Layer) متصل به LLM Router
تشخیص سطح ریسک بر اساس متن پیام بیمار
"""

import logging
from typing import Tuple, Optional
from llm.router import get_llm_router

logger = logging.getLogger(__name__)

RISK_PROMPT = """
You are a medical safety classifier for a cosmetic clinic. Analyze the patient message and return ONLY the risk level (one word) from the following options:
- emergency: life-threatening symptoms (difficulty breathing, fainting, severe allergic reaction)
- high: pregnancy, breastfeeding, diabetes, epilepsy, blood thinners, serious conditions
- medium: medications, mild allergies, chronic stable conditions
- low: minor side effects (bruising, mild swelling, itching)
- none: no medical risk (general questions about prices, appointments, etc.)

Patient message: {message}

Risk level (emergency/high/medium/low/none):
"""

async def check_medical_risk(text: str, use_llm: bool = True) -> Tuple[bool, Optional[str]]:
    if not text or not use_llm:
        return False, None

    prompt = RISK_PROMPT.format(message=text)
    router = get_llm_router()
    
    try:
        # استفاده از روتر به جای اتصال مستقیم به جمینای
        risk_level = await router.generate(prompt, max_tokens=10)
        risk_level = risk_level.strip().lower()
        
        valid_levels = ['emergency', 'high', 'medium', 'low', 'none']
        if risk_level not in valid_levels:
            logger.warning(f"خروجی نامعتبر از LLM Router: {risk_level}")
            risk_level = 'none'
            
        if risk_level == 'none':
            return False, None
            
        return True, risk_level
        
    except Exception as e:
        logger.error(f"خطا در تشخیص ریسک پزشکی (همه Providerها قطع هستند): {e}")
        return False, None

def get_risk_message(risk_level: str, lang: str = 'fa') -> str:
    messages = {
        'emergency': {
            'fa': "🚨 این وضعیت نیاز به اقدام فوری پزشکی دارد. لطفاً فوراً با اورژانس تماس بگیرید یا به نزدیک‌ترین مرکز درمانی مراجعه کنید.",
            'en': "🚨 This situation requires immediate medical attention. Please call emergency services or go to the nearest hospital."
        },
        'high': {
            'fa': "⚠️ برای پاسخ به این سوال، نیاز به بررسی پزشک دارید. لطفاً با کلینیک تماس بگیرید یا از منشی بخواهید پیام شما را به پزشک منتقل کند.",
            'en': "⚠️ This question requires a doctor's review. Please contact the clinic or ask the secretary to forward your message."
        },
        'medium': {
            'fa': "ℹ️ این سوال نیاز به بررسی دقیق‌تری دارد. پیشنهاد می‌کنم با پزشک خود مشورت کنید یا از طریق تماس تلفنی با کلینیک پیگیری نمایید.",
            'en': "ℹ️ This question needs more careful review. I suggest consulting your doctor or following up with the clinic by phone."
        },
        'low': {
            'fa': "✨ عوارض خفیف معمولاً طبیعی هستند. اما اگر شدت گرفت یا طولانی شد، حتماً با پزشک مشورت کنید.",
            'en': "✨ Mild side effects are usually normal. But if they become severe or prolonged, consult your doctor."
        }
    }
    return messages.get(risk_level, {}).get(lang, messages['high']['fa'])
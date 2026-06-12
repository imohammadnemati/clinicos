import asyncio
import logging
from typing import Tuple, Optional
import requests
from config import GROQ_API_KEY

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # همان مدل اصلی

RISK_PROMPT = """
You are a medical safety classifier for a cosmetic clinic. Analyze the patient message and return ONLY the risk level (one word) from the following options:
- emergency: life-threatening symptoms (difficulty breathing, fainting, severe allergic reaction)
- high: pregnancy, breastfeeding, diabetes, epilepsy, blood thinners, serious conditions
- medium: medications, mild allergies, chronic stable conditions
- low: minor side effects (bruising, mild swelling, itching)
- none: no medical risk (general questions)

Patient message: {message}

Risk level (emergency/high/medium/low/none):
"""

async def call_groq_risk(prompt: str, max_retries: int = 2) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 20
    }
    for attempt in range(max_retries):
        try:
            resp = await asyncio.to_thread(requests.post, GROQ_URL, headers=headers, json=data, timeout=10)
            if resp.status_code == 200:
                return resp.json()['choices'][0]['message']['content'].strip().lower()
            else:
                logger.warning(f"Groq risk error {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Groq risk attempt {attempt+1} failed: {e}")
        await asyncio.sleep(1)
    return "none"

async def check_medical_risk(text: str, use_llm: bool = True) -> Tuple[bool, Optional[str]]:
    if not text or not use_llm:
        return False, None
    prompt = RISK_PROMPT.format(message=text)
    risk_level = await call_groq_risk(prompt)
    valid = ['emergency', 'high', 'medium', 'low', 'none']
    if risk_level not in valid:
        risk_level = 'none'
    if risk_level == 'none':
        return False, None
    return True, risk_level

def get_risk_message(risk_level: str, lang: str = 'fa') -> str:
    messages = {
        'emergency': {
            'fa': "🚨 شرایط اورژانسی! لطفاً فوراً به پزشک مراجعه کنید.",
            'en': "🚨 Emergency! Please see a doctor immediately.",
            'ar': "🚨 حالة طارئة! يرجى مراجعة الطبيب فوراً."
        },
        'high': {
            'fa': "⚠️ برای پاسخ به این سوال نیاز به بررسی پزشک دارید. لطفاً با کلینیک تماس بگیرید.",
            'en': "⚠️ This question requires a doctor's review. Please contact the clinic.",
            'ar': "⚠️ هذا السؤال يحتاج إلى مراجعة الطبيب. يرجى الاتصال بالعيادة."
        },
        'medium': {
            'fa': "ℹ️ بهتر است با پزشک خود مشورت کنید.",
            'en': "ℹ️ It's better to consult your doctor.",
            'ar': "ℹ️ من الأفضل استشارة طبيبك."
        },
        'low': {
            'fa': "✨ عوارض خفیف معمولاً طبیعی هستند، اما اگر شدید شدند با پزشک تماس بگیرید.",
            'en': "✨ Mild side effects are usually normal, but contact your doctor if severe.",
            'ar': "✨ الآثار الجانبية الخفيفة طبيعية، لكن اتصل بطبيبك إذا تفاقمت."
        }
    }
    return messages.get(risk_level, {}).get(lang, messages['high']['fa'])
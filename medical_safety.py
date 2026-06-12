import json
import re
import asyncio
import logging
from typing import Tuple, Optional
import requests
from config import CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID

logger = logging.getLogger(__name__)

# استفاده از مدل جدید (غیر منقضی)
CLOUDFLARE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/meta/llama-3.2-3b-instruct"

RISK_PROMPT = """
You are a medical safety classifier for a cosmetic clinic. Analyze the patient message and return ONLY the risk level (one word) from the following options:
- emergency: life-threatening symptoms (difficulty breathing, fainting, severe allergic reaction, anaphylaxis)
- high: pregnancy, breastfeeding, diabetes, epilepsy, blood thinners, serious medical conditions
- medium: medications, mild allergies, chronic but stable conditions
- low: minor side effects (bruising, mild swelling, itching)
- none: no medical risk (general questions about prices, appointments, etc.)

Patient message: {message}

Risk level (emergency/high/medium/low/none):
"""

async def call_cloudflare_risk(prompt: str, max_retries: int = 2) -> str:
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 20,
        "temperature": 0.1
    }
    for attempt in range(max_retries):
        try:
            resp = await asyncio.to_thread(requests.post, CLOUDFLARE_URL, headers=headers, json=data, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                return result['result']['response'].strip().lower()
            else:
                logger.warning(f"Cloudflare risk API error {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Cloudflare risk attempt {attempt+1} failed: {e}")
        await asyncio.sleep(1)
    return "none"

async def check_medical_risk(text: str, use_llm: bool = True) -> Tuple[bool, Optional[str]]:
    if not text or not use_llm:
        return False, None
    prompt = RISK_PROMPT.format(message=text)
    risk_level = await call_cloudflare_risk(prompt)
    valid_levels = ['emergency', 'high', 'medium', 'low', 'none']
    if risk_level not in valid_levels:
        logger.warning(f"Invalid risk output: {risk_level}")
        risk_level = 'none'
    if risk_level == 'none':
        return False, None
    return True, risk_level

def get_risk_message(risk_level: str, lang: str = 'fa') -> str:
    messages = {
        'emergency': {
            'fa': "🚨 این وضعیت نیاز به اقدام فوری پزشکی دارد. لطفاً فوراً با اورژانس تماس بگیرید یا به نزدیک‌ترین مرکز درمانی مراجعه کنید.",
            'en': "🚨 This situation requires immediate medical attention. Please call emergency services or go to the nearest hospital.",
            'ar': "🚨 هذه الحالة تتطلب عناية طبية فورية. يرجى الاتصال بخدمات الطوارئ أو الذهاب إلى أقرب مستشفى."
        },
        'high': {
            'fa': "⚠️ برای پاسخ به این سوال، نیاز به بررسی پزشک دارید. لطفاً با کلینیک تماس بگیرید یا از منشی بخواهید پیام شما را به پزشک منتقل کند.",
            'en': "⚠️ This question requires a doctor's review. Please contact the clinic or ask the secretary to forward your message.",
            'ar': "⚠️ هذا السؤال يحتاج إلى مراجعة الطبيب. يرجى الاتصال بالعيادة أو طلب من السكرتير نقل رسالتك."
        },
        'medium': {
            'fa': "ℹ️ این سوال نیاز به بررسی دقیق‌تری دارد. پیشنهاد می‌کنم با پزشک خود مشورت کنید یا از طریق تماس تلفنی با کلینیک پیگیری نمایید.",
            'en': "ℹ️ This question needs more careful review. I suggest consulting your doctor or following up with the clinic by phone.",
            'ar': "ℹ️ هذا السؤال يحتاج إلى مراجعة أكثر دقة. أقترح استشارة طبيبك أو متابعة العيادة عبر الهاتف."
        },
        'low': {
            'fa': "✨ عوارض خفیف معمولاً طبیعی هستند. اما اگر شدت گرفت یا طولانی شد، حتماً با پزشک مشورت کنید.",
            'en': "✨ Mild side effects are usually normal. But if they become severe or prolonged, consult your doctor.",
            'ar': "✨ الآثار الجانبية الخفيفة عادة ما تكون طبيعية. ولكن إذا أصبحت شديدة أو طويلة، استشر طبيبك."
        }
    }
    return messages.get(risk_level, {}).get(lang, messages['high']['fa'])
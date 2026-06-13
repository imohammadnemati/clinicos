"""
ماژول ایمنی پزشکی (Medical Safety Layer) با استفاده از Gemini Client
تشخیص سطح ریسک بر اساس متن پیام بیمار با مدل Gemini
"""

import logging
from typing import Tuple, Optional
from gemini_client import get_gemini_client

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
    """
    تشخیص ریسک پزشکی با استفاده از Gemini Client
    پارامترها:
        text: متن پیام بیمار
        use_llm: آیا از مدل استفاده شود (همیشه True برای Gemini)
    خروجی:
        (آیا ریسک وجود دارد؟, سطح ریسک)
        سطوح: 'emergency', 'high', 'medium', 'low', None
    """
    if not text or not use_llm:
        return False, None

    prompt = RISK_PROMPT.format(message=text)
    client = get_gemini_client()
    try:
        risk_level = await client.generate_content(prompt, temperature=0.0, max_tokens=10)
        risk_level = risk_level.strip().lower()
        valid_levels = ['emergency', 'high', 'medium', 'low', 'none']
        if risk_level not in valid_levels:
            logger.warning(f"خروجی نامعتبر از Gemini: {risk_level}")
            risk_level = 'none'
        if risk_level == 'none':
            return False, None
        return True, risk_level
    except Exception as e:
        logger.error(f"خطا در تشخیص ریسک پزشکی: {e}")
        return False, None

def get_risk_message(risk_level: str, lang: str = 'fa') -> str:
    """
    دریافت پیام مناسب برای هر سطح ریسک به زبان‌های فارسی، انگلیسی، عربی
    """
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


# برای تست در صورت اجرای مستقیم
if __name__ == "__main__":
    import asyncio
    async def test():
        test_messages = [
            "قیمت بوتاکس چنده؟",
            "من باردارم میتونم بوتاکس انجام بدم؟",
            "بعد از تزریق صورتم خیلی داغ شده و ورم کرده",
            "تنگی نفس دارم",
            "قرص آسپرین مصرف می‌کنم"
        ]
        for msg in test_messages:
            has_risk, level = await check_medical_risk(msg)
            print(f"متن: {msg}\nریسک: {level if has_risk else 'none'}\n{'-'*40}")

    asyncio.run(test())

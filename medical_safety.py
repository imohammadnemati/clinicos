"""
Medical Safety Module – Keyword‑based risk detection.
No LLM calls, no external API dependencies.
Used to flag potentially dangerous medical questions before they reach the LLM router.
"""

import re
from typing import Tuple, Optional

# ========== Risk Keyword Lists ==========
# High risk – immediate medical attention required
HIGH_RISK_KEYWORDS = [
    'بارداری', 'باردار', 'حامله', 'شیردهی',
    'دیابت', 'فشار خون', 'صرع', 'میگرن شدید',
    'خونریزی', 'عفونت شدید', 'تب بالا', 'تشنج',
    'بیهوشی', 'حساسیت شدید', 'واکنش آلرژیک',
    'تنگی نفس', 'ایست قلبی', 'شوک آنافیلاکتیک'
]

# Medium risk – requires doctor review, but not emergency
MEDIUM_RISK_KEYWORDS = [
    'دارو', 'قرص', 'آسپرین', 'وارفارین', 'رقیق کننده خون',
    'واکسین', 'واکسن', 'حساسیت', 'آلرژی',
    'بیماری خودایمنی', 'کم کاری تیروئید', 'پرکاری تیروئید'
]

# Low risk – minor side effects, informational
LOW_RISK_KEYWORDS = [
    'کبودی', 'قرمزی', 'تورم خفیف', 'درد خفیف',
    'خارش', 'پوسته پوسته شدن'
]

# ========== Core Functions ==========
def keyword_risk(text: str) -> str:
    """
    Detect risk level based on keywords.
    Returns: 'emergency', 'high', 'medium', 'low', or 'none'
    """
    if not text:
        return 'none'
    text_lower = text.lower()
    
    # Emergency keywords (immediate life‑threatening)
    emergency_keywords = ['تنگی نفس', 'بیهوش', 'ایست قلبی', 'شوک آنافیلاکتیک', 'خونریزی شدید']
    for kw in emergency_keywords:
        if kw in text_lower:
            return 'emergency'
    
    for kw in HIGH_RISK_KEYWORDS:
        if kw in text_lower:
            return 'high'
    
    for kw in MEDIUM_RISK_KEYWORDS:
        if kw in text_lower:
            return 'medium'
    
    for kw in LOW_RISK_KEYWORDS:
        if kw in text_lower:
            return 'low'
    
    return 'none'


async def check_medical_risk(text: str, use_llm: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Main risk detection function (synchronous, keyword‑only).
    Args:
        text: Patient message
        use_llm: Ignored, kept for compatibility with previous code.
    Returns:
        (risk_detected, risk_level) where risk_level is one of:
        'emergency', 'high', 'medium', 'low', or None if no risk.
    """
    risk = keyword_risk(text)
    if risk == 'none':
        return False, None
    return True, risk


def get_risk_message(risk_level: str, lang: str = 'fa') -> str:
    """
    Return a user‑friendly message based on risk level and language.
    """
    messages = {
        'emergency': {
            'fa': "🚨 شرایط اورژانسی! لطفاً فوراً با اورژانس تماس بگیرید یا به نزدیک‌ترین مرکز درمانی مراجعه کنید.",
            'en': "🚨 Emergency situation! Please call emergency services or go to the nearest hospital immediately.",
            'ar': "🚨 حالة طارئة! يرجى الاتصال بخدمات الطوارئ أو الذهاب إلى أقرب مستشفى فوراً."
        },
        'high': {
            'fa': "⚠️ برای پاسخ به این سوال نیاز به بررسی پزشک دارید. لطفاً با کلینیک تماس بگیرید یا از منشی بخواهید پیام شما را به پزشک منتقل کند.",
            'en': "⚠️ This question requires a doctor's review. Please contact the clinic or ask the secretary to forward your message.",
            'ar': "⚠️ هذا السؤال يحتاج إلى مراجعة الطبيب. يرجى الاتصال بالعيادة أو طلب من السكرتير نقل رسالتك."
        },
        'medium': {
            'fa': "ℹ️ بهتر است با پزشک خود مشورت کنید. می‌توانید یک وقت مشاوره رایگان بگیرید.",
            'en': "ℹ️ It's better to consult your doctor. You can book a free consultation.",
            'ar': "ℹ️ من الأفضل استشارة طبيبك. يمكنك حجز استشارة مجانية."
        },
        'low': {
            'fa': "✨ عوارض خفیف معمولاً طبیعی هستند. اما اگر شدت گرفت یا طولانی شد، حتماً با پزشک مشورت کنید.",
            'en': "✨ Mild side effects are usually normal. But if they become severe or prolonged, consult your doctor.",
            'ar': "✨ الآثار الجانبية الخفيفة طبيعية عادة. ولكن إذا أصبحت شديدة أو طويلة، استشر طبيبك."
        }
    }
    return messages.get(risk_level, {}).get(lang, messages.get('high', {}).get('fa', "Please consult a doctor."))


# Optional test function (not used in production)
if __name__ == "__main__":
    import asyncio
    async def test():
        test_texts = [
            "قیمت بوتاکس چنده؟",
            "من باردارم، می‌تونم فیلر بزنم؟",
            "بعد از تزریق صورتم داغ شده",
            "تنگی نفس دارم",
            "قرص آسپرین مصرف می‌کنم"
        ]
        for t in test_texts:
            has, level = await check_medical_risk(t)
            print(f"Text: {t}\nRisk: {level if has else 'none'}\n{'-'*40}")
    
    asyncio.run(test())
import re
from typing import Tuple, Optional

# فقط کلمات کلیدی واقعاً خطرناک (نه ترس معمولی)
HIGH_RISK_KEYWORDS = [
    'بارداری', 'باردار', 'حامله', 'شیردهی',
    'دیابت', 'فشار خون', 'صرع', 'میگرن شدید',
    'خونریزی', 'عفونت شدید', 'تب بالا', 'تشنج',
    'بیهوشی', 'حساسیت شدید', 'واکنش آلرژیک'
]

MEDIUM_RISK_KEYWORDS = [
    'دارو', 'قرص', 'آسپرین', 'وارفارین', 'رقیق کننده خون',
    'واکسین', 'واکسن', 'حساسیت', 'آلرژی'
]

def keyword_risk(text: str) -> str:
    text_lower = text.lower()
    for kw in HIGH_RISK_KEYWORDS:
        if kw in text_lower:
            return 'high'
    for kw in MEDIUM_RISK_KEYWORDS:
        if kw in text_lower:
            return 'medium'
    return 'none'

async def check_medical_risk(text: str, use_llm: bool = False) -> Tuple[bool, Optional[str]]:
    risk = keyword_risk(text)
    if risk != 'none':
        return True, risk
    return False, None

def get_risk_message(risk_level: str, lang: str = 'fa') -> str:
    messages = {
        'high': {
            'fa': "⚠️ برای پاسخ به این سوال نیاز به بررسی پزشک دارید. لطفاً با کلینیک تماس بگیرید.",
            'en': "⚠️ This question requires a doctor's review. Please contact the clinic.",
            'ar': "⚠️ هذا السؤال يحتاج إلى مراجعة الطبيب. يرجى الاتصال بالعيادة."
        },
        'medium': {
            'fa': "ℹ️ بهتر است با پزشک خود مشورت کنید.",
            'en': "ℹ️ It's better to consult your doctor.",
            'ar': "ℹ️ من الأفضل استشارة طبيبك."
        }
    }
    return messages.get(risk_level, {}).get(lang, messages['high']['fa'])
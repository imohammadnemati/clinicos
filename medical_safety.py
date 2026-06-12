"""
ماژول ایمنی پزشکی (Medical Safety Layer) – نسخه ساده بدون LLM
فقط با کلمات کلیدی کار می‌کند و نیاز به Gemini یا سایر APIها ندارد.
برای استفاده در Railway و Cloudflare AI (بدون وابستگی خارجی)
"""

import re
from typing import Tuple, Optional

# کلمات کلیدی اورژانسی – نیاز به اقدام فوری پزشک
EMERGENCY_KEYWORDS = [
    'تنگی نفس', 'بیهوش', 'ایست قلبی', 'شوک آنافیلاکتیک',
    'ادم حنجره', 'افت فشار ناگهانی'
]

# کلمات کلیدی پرخطر (high risk) – نیاز به مداخله پزشک
HIGH_RISK_KEYWORDS = [
    'بارداری', 'باردار', 'حامله', 'شیردهی',
    'دیابت', 'فشار خون', 'صرع', 'میگرن شدید',
    'خونریزی', 'عفونت شدید', 'تب بالا', 'تشنج',
    'بیهوشی', 'حساسیت شدید', 'واکنش آلرژیک'
]

# کلمات کلیدی با خطر متوسط (medium risk) – نیاز به بررسی پزشک
MEDIUM_RISK_KEYWORDS = [
    'دارو', 'قرص', 'آسپرین', 'وارفارین', 'رقیق کننده خون',
    'واکسین', 'واکسن', 'حساسیت', 'آلرژی',
    'بیماری خودایمنی', 'کم کاری تیروئید', 'پرکاری تیروئید'
]

# کلمات کلیدی کم خطر (low risk) – فقط آگاه‌سازی
LOW_RISK_KEYWORDS = [
    'کبودی', 'قرمزی', 'تورم خفیف', 'درد خفیف',
    'خارش', 'پوسته پوسته شدن'
]

def keyword_risk(text: str) -> str:
    """
    تشخیص ریسک بر اساس کلمات کلیدی
    خروجی: 'emergency', 'high', 'medium', 'low', 'none'
    """
    if not text:
        return 'none'
    text_lower = text.lower()
    
    for kw in EMERGENCY_KEYWORDS:
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
    تابع اصلی بررسی ریسک پزشکی (بدون LLM)
    پارامتر use_llm صرفاً برای سازگاری با کد قدیمی است و تأثیری ندارد.
    
    خروجی:
        (آیا ریسک وجود دارد؟, سطح ریسک)
        سطوح: 'emergency', 'high', 'medium', 'low', None
    """
    risk = keyword_risk(text)
    if risk != 'none':
        return True, risk
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


# در صورت اجرای مستقیم فایل (برای تست)
if __name__ == "__main__":
    test_texts = [
        "قیمت بوتاکس چنده؟",
        "من باردارم میتونم بوتاکس انجام بدم؟",
        "بعد از تزریق صورتم داغ شده",
        "تنگی نفس دارم",
        "قرص آسپرین مصرف می‌کنم"
    ]
    for t in test_texts:
        risk = keyword_risk(t)
        print(f"متن: {t}\nریسک: {risk}\n{'-'*40}")
"""
ماژول ایمنی پزشکی (Medical Safety Layer)
این ماژول مسئول تشخیص خطرات پزشکی در پیام‌های بیماران است.
از دو مرحله استفاده می‌کند:
1. تشخیص با کلمات کلیدی (سریع و کم‌هزینه)
2. در صورت نیاز، تشخیص دقیق‌تر با LLM (Gemini)
"""

import re
from typing import Tuple, Optional
import google.generativeai as genai
from config import GEMINI_API_KEY

# تنظیم کلید API جمینای (در صورت وجود)
if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_key":
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None
    print("⚠️ هشدار: GEMINI_API_KEY تنظیم نشده است. سطح LLM غیرفعال خواهد شد.")

# کلمات کلیدی پرخطر (high risk) - نیاز به مداخله فوری پزشک
HIGH_RISK_KEYWORDS = [
    'بارداری', 'باردار', 'حامله', 'شیردهی',
    'دیابت', 'فشار خون', 'صرع', 'میگرن شدید',
    'خونریزی', 'عفونت شدید', 'تب بالا', 'تشنج',
    'بیهوشی', 'حساسیت شدید', 'واکنش آلرژیک'
]

# کلمات کلیدی با خطر متوسط (medium risk) - نیاز به بررسی پزشک
MEDIUM_RISK_KEYWORDS = [
    'دارو', 'قرص', 'آسپرین', 'وارفارین', 'رقیق کننده خون',
    'واکسین', 'واکسن', 'حساسیت', 'آلرژی',
    'بیماری خودایمنی', 'کم کاری تیروئید', 'پرکاری تیروئید'
]

# کلمات کلیدی کم خطر (low risk) - فقط آگاه‌سازی
LOW_RISK_KEYWORDS = [
    'کبودی', 'قرمزی', 'تورم خفیف', 'درد خفیف',
    'خارش', 'پوسته پوسته شدن'
]


def keyword_risk(text: str) -> str:
    """
    تشخیص ریسک بر اساس کلمات کلیدی
    پارامترها:
        text: متن پیام بیمار
    خروجی:
        'emergency', 'high', 'medium', 'low', 'none'
    """
    text_lower = text.lower()
    
    # کلمات اورژانسی (نیاز به اقدام فوری)
    emergency_keywords = ['تنگی نفس', 'بیهوش', 'ایست قلبی', 'شوک آنافیلاکتیک']
    for kw in emergency_keywords:
        if kw in text_lower:
            return 'emergency'
    
    # ریسک بالا
    for kw in HIGH_RISK_KEYWORDS:
        if kw in text_lower:
            return 'high'
    
    # ریسک متوسط
    for kw in MEDIUM_RISK_KEYWORDS:
        if kw in text_lower:
            return 'medium'
    
    # ریسک کم
    for kw in LOW_RISK_KEYWORDS:
        if kw in text_lower:
            return 'low'
    
    return 'none'


async def llm_risk_classify(text: str) -> str:
    """
    تشخیص ریسک با استفاده از LLM (جمینای) - دقیق‌تر ولی پرهزینه‌تر
    پارامترها:
        text: متن پیام بیمار
    خروجی:
        'emergency', 'high', 'medium', 'low', 'none'
    """
    if not model:
        return 'none'
    
    prompt = f"""You are a medical safety classifier for a cosmetic clinic.
Analyze the following patient message and classify its medical risk level.
Return ONLY one word: emergency, high, medium, low, or none.

Guidelines:
- emergency: life-threatening symptoms like difficulty breathing, fainting, severe allergic reaction
- high: pregnancy, breastfeeding, diabetes, epilepsy, blood thinners, serious medical conditions
- medium: medications, mild allergies, chronic but stable conditions
- low: minor side effects like bruising, mild swelling, itching
- none: no medical risk, just general questions about prices, appointments, etc.

Patient message: {text}

Risk level:"""
    
    try:
        response = model.generate_content(prompt)
        level = response.text.strip().lower()
        if level in ['emergency', 'high', 'medium', 'low', 'none']:
            return level
    except Exception as e:
        print(f"خطا در LLM risk classification: {e}")
    
    return 'none'


async def check_medical_risk(text: str, use_llm: bool = True) -> Tuple[bool, Optional[str]]:
    """
    تابع اصلی بررسی ریسک پزشکی
    پارامترها:
        text: متن پیام بیمار
        use_llm: آیا از LLM برای تأیید استفاده شود؟
    خروجی:
        (آیا ریسک وجود دارد؟, سطح ریسک)
    """
    # مرحله 1: کلمات کلیدی
    kw_risk = keyword_risk(text)
    
    # اگر اورژانسی باشد، بدون نیاز به LLM برگردان
    if kw_risk == 'emergency':
        return True, 'emergency'
    
    # اگر ریسک بالا باشد و LLM فعال باشد، تأیید کنیم
    if kw_risk in ['high', 'medium'] and use_llm and model:
        llm_risk = await llm_risk_classify(text)
        # اگر LLM ریسک بالاتری تشخیص داد، آن را بپذیر
        risk_levels = {'emergency': 5, 'high': 4, 'medium': 3, 'low': 2, 'none': 1}
        if risk_levels.get(llm_risk, 0) > risk_levels.get(kw_risk, 0):
            final_risk = llm_risk
        else:
            final_risk = kw_risk
        if final_risk != 'none':
            return True, final_risk
        else:
            return False, None
    
    # اگر ریسک متوسط یا بالا بود بدون LLM
    if kw_risk in ['high', 'medium']:
        return True, kw_risk
    
    # اگر ریسک کم بود، فقط آگاه‌سازی (اختیاری، می‌توان پاسخ داد)
    if kw_risk == 'low':
        return True, 'low'
    
    return False, None


def get_risk_message(risk_level: str, lang: str = 'fa') -> str:
    """
    دریافت پیام متناسب با سطح ریسک
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
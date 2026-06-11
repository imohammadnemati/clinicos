"""
ماژول پیش‌فیلتر (Pre-filter)
این ماژول مسئول فیلتر کردن پیام‌های ساده و بی‌ارزش قبل از ارسال به LLM است.
هدف: کاهش هزینه‌های API و جلوگیری از پردازش پیام‌های غیرضروری
"""

import re
from typing import Tuple, Optional


# الگوهای پیام‌های بسیار ساده (بدون نیاز به AI)
SIMPLE_GREETINGS = [
    r'^(سلام|سلام|سلامم|سلامی|درود|درود|خوبی|چطوری|چطورید|چطورین)$',
    r'^(hi|hello|hey|hy|salam|dorood)$',
    r'^(صبح بخیر|ظهر بخیر|عصر بخیر|شب بخیر|روز بخیر)$',
    r'^(good morning|good afternoon|good evening|good night)$',
]

SIMPLE_THANKS = [
    r'^(مرسی|ممنون|تشکر|سپاس|متشکرم|دمت گرم|دستت درد نکنه)$',
    r'^(thanks|thank you|tnx|thx|ty)$',
    r'^(سپاسگزارم|ممنونم|تشکر می‌کنم)$',
]

SIMPLE_GOODBYE = [
    r'^(خداحافظ|خدانگهدار|بای|بای بای|فعلا|خدافظ|خداحافظی)$',
    r'^(bye|goodbye|bai|خدافظ|خداحافظ|خدانگهدار|خدانگهدار)$',
]

SIMPLE_AFFIRM = [
    r'^(بله|آره|اره|حتما|اوکی|ok|باشه|باشد|چشم|خوب|عالی)$',
    r'^(yes|yeah|yep|okay|sure|alright|fine|great)$',
]

SIMPLE_NEGATE = [
    r'^(نه|نخیر|خیر|نه ممنون|نه مرسی|نه تشکر)$',
    r'^(no|nope|not|nah|no thanks|no thank you)$',
]

SIMPLE_QUESTION_SHORT = [
    r'^(\?|\؟)$',  # فقط علامت سوال
    r'^(چی؟|چه؟|کجا؟|کی؟|چرا؟|چطور؟|چگونه؟|چند؟)$',
    r'^(what|why|when|where|how|who|which)$',
]

# الگوهای پیام‌های اسپم یا بی‌ارزش
SPAM_PATTERNS = [
    r'^(test|تست|ازمایش|آزمایش)$',
    r'^(\.|\.\.\.|,|!|;|:)$',  # فقط علائم نگارشی
    r'^[\d\s]+$',  # فقط اعداد و فاصله
    r'^[a-zA-Z]{1,3}$',  # 1 تا 3 حرف انگلیسی (مثل 'asd', 'test')
    r'^[\u0600-\u06FF]{1,2}$',  # 1 تا 2 حرف عربی/فارسی
    r'(www\.|http|https|@|#)',  # لینک یا هشتگ
    r'(سایت|پیج|کانال|چنل|ادمین|مدیر)',  # کلمات تبلیغاتی رایج
]


def is_trivial_message(text: str) -> bool:
    """
    بررسی آیا پیام بسیار ساده است و نیازی به AI ندارد
    پارامترها:
        text: متن پیام
    خروجی:
        True اگر پیام ساده باشد، False در غیر این صورت
    """
    if not text or not text.strip():
        return True
    
    cleaned = text.strip().lower()
    
    # بررسی الگوهای ساده
    all_patterns = (SIMPLE_GREETINGS + SIMPLE_THANKS + SIMPLE_GOODBYE + 
                    SIMPLE_AFFIRM + SIMPLE_NEGATE + SIMPLE_QUESTION_SHORT)
    
    for pattern in all_patterns:
        if re.match(pattern, cleaned, re.IGNORECASE):
            return True
    
    return False


def is_spam(text: str) -> bool:
    """
    بررسی آیا پیام اسپم یا بی‌ارزش است
    پارامترها:
        text: متن پیام
    خروجی:
        True اگر اسپم باشد، False در غیر این صورت
    """
    if not text or not text.strip():
        return True
    
    cleaned = text.strip().lower()
    
    for pattern in SPAM_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return True
    
    # پیام‌های خیلی کوتاه (کمتر از 2 کاراکتر)
    if len(cleaned) < 2:
        return True
    
    return False


def needs_llm(text: str) -> bool:
    """
    بررسی آیا پیام نیاز به پردازش با LLM دارد
    پارامترها:
        text: متن پیام
    خروجی:
        True اگر نیاز به LLM باشد، False در غیر این صورت
    """
    if is_spam(text):
        return False
    
    if is_trivial_message(text):
        return False
    
    # پیام‌های خیلی کوتاه (2-3 کاراکتر) بدون محتوای مشخص
    if len(text.strip()) <= 3:
        return False
    
    return True


def get_simple_response(text: str, lang: str = 'fa') -> Optional[str]:
    """
    دریافت پاسخ ساده برای پیام‌های پیش‌فیلتر شده
    پارامترها:
        text: متن پیام
        lang: زبان ('fa', 'en', 'ar')
    خروجی:
        متن پاسخ یا None اگر پاسخ پیش‌فرض وجود نداشته باشد
    """
    if not text:
        return None
    
    cleaned = text.strip().lower()
    
    # احوالپرسی
    for pattern in SIMPLE_GREETINGS:
        if re.match(pattern, cleaned, re.IGNORECASE):
            if lang == 'fa':
                return "سلام 🌷\nچطور می‌توانم به شما کمک کنم؟"
            elif lang == 'en':
                return "Hello 🌷\nHow can I help you?"
            else:
                return "مرحباً 🌷\nكيف يمكنني مساعدتك؟"
    
    # تشکر
    for pattern in SIMPLE_THANKS:
        if re.match(pattern, cleaned, re.IGNORECASE):
            if lang == 'fa':
                return "خواهش می‌کنم 🌷\nخوشحالم که توانستم کمک کنم."
            elif lang == 'en':
                return "You're welcome 🌷\nHappy to help."
            else:
                return "عفواً 🌷\nيسعدني مساعدتك."
    
    # خداحافظی
    for pattern in SIMPLE_GOODBYE:
        if re.match(pattern, cleaned, re.IGNORECASE):
            if lang == 'fa':
                return "خدانگهدار 🌷\nروز خوبی داشته باشید."
            elif lang == 'en':
                return "Goodbye 🌷\nHave a great day."
            else:
                return "مع السلامة 🌷\nأتمنى لك يوماً سعيداً."
    
    # تأیید
    for pattern in SIMPLE_AFFIRM:
        if re.match(pattern, cleaned, re.IGNORECASE):
            if lang == 'fa':
                return "خیلی خب 🌷\nاگر سوالی دارید، در خدمتم."
            elif lang == 'en':
                return "Alright 🌷\nLet me know if you have any questions."
            else:
                return "حسناً 🌷\nأخبرني إذا كان لديك أي أسئلة."
    
    # انکار
    for pattern in SIMPLE_NEGATE:
        if re.match(pattern, cleaned, re.IGNORECASE):
            if lang == 'fa':
                return "متوجه شدم 🌷\nهر زمان که نیاز داشتید، در خدمتم."
            elif lang == 'en':
                return "I understand 🌷\nI'm here whenever you need me."
            else:
                return "فهمتك 🌷\nأنا هنا كلما احتجتني."
    
    return None


def extract_medical_keywords(text: str) -> list:
    """
    استخراج کلمات کلیدی پزشکی از متن
    برای استفاده در پیش‌فیلتر و تشخیص اهمیت پیام
    """
    medical_terms = [
        'بوتاکس', 'فیلر', 'ژل', 'لیزر', 'مزوتراپی', 'هیالورونیک',
        'تزریق', 'پوست', 'لب', 'چروک', 'جوانسازی', 'لک', 'اسکار',
        'مو', 'ریزش مو', 'کاشت مو', 'پلک', 'گونه', 'چانه', 'خط خنده'
    ]
    
    found = []
    text_lower = text.lower()
    for term in medical_terms:
        if term in text_lower:
            found.append(term)
    
    return found


def is_medical_inquiry(text: str) -> bool:
    """
    بررسی آیا پیام مرتبط با مسائل پزشکی/کلینیک است
    """
    keywords = extract_medical_keywords(text)
    if keywords:
        return True
    
    # سوالات پزشکی عمومی
    medical_question_patterns = [
        r'(قیمت|هزینه|قیمتش|هزینه‌اش)',
        r'(درد|عوارض|خطر|عارضه|مشکل)',
        r'(مدت|زمان|چند جلسه|چند وقت)',
        r'(نتیجه|موفقیت|بهبود|تاثیر)',
    ]
    
    for pattern in medical_question_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False


def should_escalate_to_human(text: str) -> bool:
    """
    بررسی آیا پیام نیاز به ارجاع فوری به انسان دارد
    """
    escalation_keywords = [
        'شکایت', 'راضی نیستم', 'ناراضی', 'مشکل دارم',
        'با مسئول', 'با مدیر', 'با پزشک', 'با دکتر',
        'حرف بزنم', 'صحبت کنم', 'تماس بگیرم'
    ]
    
    text_lower = text.lower()
    for kw in escalation_keywords:
        if kw in text_lower:
            return True
    
    return False
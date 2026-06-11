"""
ماژول تشخیص زبان (Language Detector)
این ماژول مسئول تشخیص زبان متن ورودی کاربر است.
از سه روش ترکیبی استفاده می‌کند:
1. تشخیص با Regex (سریع برای فارسی، عربی، انگلیسی)
2. تشخیص با کتابخانه langdetect (برای موارد نامشخص)
3. بازگشت به زبان پیش‌فرض (فارسی) در صورت عدم تشخیص
"""

import re
from typing import Optional
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# برای ثابت بودن نتایج langdetect
DetectorFactory.seed = 0


def detect_language_regex(text: str) -> Optional[str]:
    """
    تشخیص زبان با استفاده از regex (سریع و کم‌هزینه)
    پارامترها:
        text: متن ورودی
    خروجی:
        'fa', 'en', 'ar' یا None در صورت عدم تشخیص قطعی
    """
    if not text or not text.strip():
        return None
    
    # محاسبه تعداد کاراکترهای هر الفبا
    arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\u0870-\u089F\uFB50-\uFDFF\uFE70-\uFEFF]', text))
    persian_chars = len(re.findall(r'[\u0600-\u06FF\uFB50-\uFDFF]', text))
    english_chars = len(re.findall(r'[A-Za-z]', text))
    
    # حروف خاص فارسی (پ, چ, ژ, گ)
    persian_specific = len(re.findall(r'[پچژگ]', text))
    
    # تشخیص فارسی: وجود حروف خاص فارسی یا غلبه حروف فارسی بر عربی
    if persian_specific > 0 or (persian_chars > english_chars and persian_chars > arabic_chars * 0.7):
        return 'fa'
    
    # تشخیص عربی: وجود علامت سوال عربی یا غلبه حروف عربی
    if '؟' in text and arabic_chars > 10:
        return 'ar'
    
    if arabic_chars > english_chars and arabic_chars > 5:
        return 'ar'
    
    # تشخیص انگلیسی: غلبه حروف انگلیسی
    if english_chars > arabic_chars and english_chars > 3:
        return 'en'
    
    return None


def detect_language_langdetect(text: str) -> Optional[str]:
    """
    تشخیص زبان با استفاده از کتابخانه langdetect (دقیق‌تر ولی کندتر)
    پارامترها:
        text: متن ورودی
    خروجی:
        'fa', 'en', 'ar' یا None در صورت خطا
    """
    if not text or len(text.strip()) < 10:
        return None
    
    try:
        lang = detect(text)
        if lang in ['fa', 'en', 'ar']:
            return lang
        elif lang.startswith('fa'):
            return 'fa'
        elif lang.startswith('ar'):
            return 'ar'
        elif lang.startswith('en'):
            return 'en'
    except LangDetectException:
        pass
    except Exception:
        pass
    
    return None


def detect_language(text: str, use_langdetect: bool = True, default: str = 'fa') -> str:
    """
    تابع اصلی تشخیص زبان
    پارامترها:
        text: متن ورودی
        use_langdetect: آیا از langdetect استفاده شود؟ (برای صرفه‌جویی در هزینه، می‌توان False کرد)
        default: زبان پیش‌فرض در صورت عدم تشخیص
    خروجی:
        'fa', 'en' یا 'ar'
    """
    if not text or not text.strip():
        return default
    
    # مرحله 1: تشخیص سریع با Regex
    lang = detect_language_regex(text)
    if lang:
        return lang
    
    # مرحله 2: تشخیص با langdetect (در صورت فعال بودن و متن طولانی)
    if use_langdetect and len(text) > 20:
        lang = detect_language_langdetect(text)
        if lang:
            return lang
    
    # مرحله 3: بازگشت به زبان پیش‌فرض
    return default


def get_language_name(lang_code: str) -> str:
    """
    دریافت نام کامل زبان از روی کد
    پارامترها:
        lang_code: 'fa', 'en', 'ar'
    خروجی:
        نام زبان به فارسی
    """
    names = {
        'fa': 'فارسی',
        'en': 'انگلیسی',
        'ar': 'عربی'
    }
    return names.get(lang_code, 'ناشناس')


def get_language_direction(lang_code: str) -> str:
    """
    دریافت جهت نوشتار زبان
    پارامترها:
        lang_code: 'fa', 'en', 'ar'
    خروجی:
        'rtl' (راست به چپ) یا 'ltr' (چپ به راست)
    """
    rtl_languages = ['fa', 'ar']
    return 'rtl' if lang_code in rtl_languages else 'ltr'


def is_rtl(lang_code: str) -> bool:
    """
    بررسی آیا زبان راست به چپ است
    """
    return lang_code in ['fa', 'ar']


def get_language_emoji(lang_code: str) -> str:
    """
    دریافت ایموجی مربوط به زبان
    """
    emojis = {
        'fa': '🇮🇷',
        'en': '🇬🇧',
        'ar': '🇸🇦'
    }
    return emojis.get(lang_code, '🌐')


def detect_language_batch(texts: list, use_langdetect: bool = True, default: str = 'fa') -> list:
    """
    تشخیص زبان برای چندین متن به صورت دسته‌ای
    پارامترها:
        texts: لیست متون
        use_langdetect: آیا از langdetect استفاده شود؟
        default: زبان پیش‌فرض
    خروجی:
        لیستی از زبان‌ها به همان ترتیب
    """
    return [detect_language(t, use_langdetect, default) for t in texts]


def get_most_frequent_language(texts: list, use_langdetect: bool = True, default: str = 'fa') -> str:
    """
    پیدا کردن زبان غالب در یک لیست از متون
    پارامترها:
        texts: لیست متون
        use_langdetect: آیا از langdetect استفاده شود؟
        default: زبان پیش‌فرض
    خروجی:
        زبان غالب ('fa', 'en', 'ar')
    """
    if not texts:
        return default
    
    from collections import Counter
    languages = detect_language_batch(texts, use_langdetect, default)
    counter = Counter(languages)
    return counter.most_common(1)[0][0]


def is_persian_text(text: str) -> bool:
    """
    بررسی سریع اینکه آیا متن به نظر فارسی است
    """
    return detect_language(text, use_langdetect=False, default='fa') == 'fa'


def is_english_text(text: str) -> bool:
    """
    بررسی سریع اینکه آیا متن به نظر انگلیسی است
    """
    return detect_language(text, use_langdetect=False, default='en') == 'en'


def is_arabic_text(text: str) -> bool:
    """
    بررسی سریع اینکه آیا متن به نظر عربی است
    """
    return detect_language(text, use_langdetect=False, default='ar') == 'ar'
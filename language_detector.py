"""
Language Detector – Detects the language of user input (Persian, English, Arabic).
Used by patient_agent.py to select the appropriate response language.
No external API calls, only regex and optional langdetect library.
"""

import re
from typing import Optional
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Ensure consistent results from langdetect
DetectorFactory.seed = 0


def detect_language_regex(text: str) -> Optional[str]:
    """
    Quick language detection using regex (Persian, Arabic, English).
    Returns 'fa', 'en', 'ar', or None.
    """
    if not text or not text.strip():
        return None

    # Count characters in different scripts
    arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\u0870-\u089F\uFB50-\uFDFF\uFE70-\uFEFF]', text))
    persian_chars = len(re.findall(r'[\u0600-\u06FF\uFB50-\uFDFF]', text))
    english_chars = len(re.findall(r'[A-Za-z]', text))
    persian_specific = len(re.findall(r'[پچژگ]', text))

    # Persian specific characters present
    if persian_specific > 0 or (persian_chars > english_chars and persian_chars > arabic_chars * 0.7):
        return 'fa'

    # Arabic question mark or strong Arabic dominance
    if '؟' in text and arabic_chars > 10:
        return 'ar'
    if arabic_chars > english_chars and arabic_chars > 5:
        return 'ar'

    # English dominance
    if english_chars > arabic_chars and english_chars > 3:
        return 'en'

    return None


def detect_language_langdetect(text: str) -> Optional[str]:
    """
    More accurate language detection using langdetect library.
    Returns 'fa', 'en', 'ar', or None if fails.
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
    Main function to detect language of the input text.
    Args:
        text: Input string
        use_langdetect: Whether to use langdetect (more accurate but slower)
        default: Default language if detection fails
    Returns:
        'fa', 'en', or 'ar'
    """
    if not text or not text.strip():
        return default

    # Step 1: quick regex
    lang = detect_language_regex(text)
    if lang:
        return lang

    # Step 2: fallback to langdetect (if enabled and text long enough)
    if use_langdetect and len(text) > 20:
        lang = detect_language_langdetect(text)
        if lang:
            return lang

    return default


def get_language_name(lang_code: str) -> str:
    """Return full language name in Persian."""
    names = {'fa': 'فارسی', 'en': 'انگلیسی', 'ar': 'عربی'}
    return names.get(lang_code, 'ناشناس')


def get_language_direction(lang_code: str) -> str:
    """Return text direction ('rtl' for Persian/Arabic, 'ltr' for English)."""
    rtl_langs = ['fa', 'ar']
    return 'rtl' if lang_code in rtl_langs else 'ltr'


def is_rtl(lang_code: str) -> bool:
    """Check if the language is right‑to‑left."""
    return lang_code in ['fa', 'ar']


def get_language_emoji(lang_code: str) -> str:
    """Return an emoji flag for the language."""
    emojis = {'fa': '🇮🇷', 'en': '🇬🇧', 'ar': '🇸🇦'}
    return emojis.get(lang_code, '🌐')


def detect_language_batch(texts: list, use_langdetect: bool = True, default: str = 'fa') -> list:
    """Detect language for a list of texts."""
    return [detect_language(t, use_langdetect, default) for t in texts]


def get_most_frequent_language(texts: list, use_langdetect: bool = True, default: str = 'fa') -> str:
    """Return the most frequent language among a list of texts."""
    if not texts:
        return default
    from collections import Counter
    langs = detect_language_batch(texts, use_langdetect, default)
    return Counter(langs).most_common(1)[0][0]


def is_persian_text(text: str) -> bool:
    """Quick check if text is Persian."""
    return detect_language(text, use_langdetect=False, default='fa') == 'fa'


def is_english_text(text: str) -> bool:
    """Quick check if text is English."""
    return detect_language(text, use_langdetect=False, default='en') == 'en'


def is_arabic_text(text: str) -> bool:
    """Quick check if text is Arabic."""
    return detect_language(text, use_langdetect=False, default='ar') == 'ar'
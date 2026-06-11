"""
ماژول شناسایی هویت بیمار (Identity Resolution)
این ماژول مسئول شناسایی و اتصال بیماران از پلتفرم‌های مختلف است.
قابلیت‌ها:
- استخراج شماره تلفن و نام از متن
- جستجوی بیمار بر اساس شماره، یوزرنیم، external_user_id
- ایجاد بیمار جدید و ذخیره aliasها
- به‌روزرسانی اطلاعات تماس بیمار
- پشتیبانی از پلتفرم‌های مختلف (تلگرام، اینستاگرام، واتساپ، وب‌سایت)
"""

import re
from typing import Optional, Tuple
from database import SessionLocal
from models import Patient, PatientAlias
from datetime import datetime
import logging

# تنظیم لاگر
logger = logging.getLogger(__name__)


# ========== توابع استخراج اطلاعات از متن ==========
def extract_phone_number(text: str) -> Optional[str]:
    """
    استخراج شماره تلفن همراه از متن
    پشتیبانی از فرمت‌های:
    - 09121234567
    - 0912 123 4567
    - 0912-123-4567
    - +989121234567
    """
    if not text:
        return None
    
    # الگوی شماره ایران (شروع با 09 یا +989)
    patterns = [
        r'(\+98|0)?9\d{9}',           # 09121234567 یا +989121234567
        r'09\d{2}[- ]?\d{3}[- ]?\d{4}', # با خط تیره یا فاصله
        r'09\d{9}'                     # ساده
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            phone = match.group()
            # استانداردسازی شماره (حذف فاصله و خط تیره)
            phone = re.sub(r'[- ]', '', phone)
            # اگر با +98 شروع می‌شود، به 0 تبدیل کن
            if phone.startswith('+98'):
                phone = '0' + phone[3:]
            return phone
    
    return None


def extract_name(text: str) -> Optional[str]:
    """
    استخراج نام از متن
    الگوهای پشتیبانی شده:
    - نام من [نام] است
    - من [نام] هستم
    - [نام] عزیز
    - سلام [نام]
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    patterns = [
        r'نام من ([\w\u0600-\u06FF]+)',
        r'من ([\w\u0600-\u06FF]+) هستم',
        r'سلام ([\w\u0600-\u06FF]+)[\s،]',
        r'([\w\u0600-\u06FF]+) عزیز',
        r'من ([\w\u0600-\u06FF]+) هستم',
        r'اسم من ([\w\u0600-\u06FF]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def extract_instagram_username(text: str) -> Optional[str]:
    """
    استخراج یوزرنیم اینستاگرام از متن
    الگوهای پشتیبانی شده:
    - @username
    - instagram.com/username
    - username (با حروف و اعداد و زیرخط)
    """
    if not text:
        return None
    
    patterns = [
        r'@([a-zA-Z0-9_\.]{3,30})',
        r'instagram\.com/([a-zA-Z0-9_\.]{3,30})',
        r'اینستاگرام[:]?\s*@?([a-zA-Z0-9_\.]{3,30})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def extract_telegram_username(text: str) -> Optional[str]:
    """
    استخراج یوزرنیم تلگرام از متن
    الگوهای پشتیبانی شده:
    - @username
    - t.me/username
    - telegram.me/username
    """
    if not text:
        return None
    
    patterns = [
        r'@([a-zA-Z0-9_]{5,32})',
        r't\.me/([a-zA-Z0-9_]{5,32})',
        r'telegram\.me/([a-zA-Z0-9_]{5,32})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


# ========== توابع جستجو در دیتابیس ==========
def find_patient_by_alias(
    platform: str,
    phone: Optional[str] = None,
    external_user_id: Optional[str] = None,
    username: Optional[str] = None,
    display_name: Optional[str] = None
) -> Optional[int]:
    """
    جستجوی بیمار با استفاده از aliasها
    اولویت جستجو: شماره تلفن > external_user_id > یوزرنیم > display_name
    """
    db = SessionLocal()
    try:
        query = db.query(PatientAlias).filter_by(platform=platform)
        
        # اولویت 1: شماره تلفن (قوی‌ترین)
        if phone:
            alias = query.filter_by(phone=phone).first()
            if alias:
                logger.debug(f"بیمار با شماره تلفن {phone} پیدا شد. patient_id={alias.patient_id}")
                return alias.patient_id
        
        # اولویت 2: external_user_id (معمولاً شناسه دائمی پلتفرم)
        if external_user_id:
            alias = query.filter_by(external_user_id=external_user_id).first()
            if alias:
                logger.debug(f"بیمار با external_user_id {external_user_id} پیدا شد. patient_id={alias.patient_id}")
                return alias.patient_id
        
        # اولویت 3: یوزرنیم
        if username:
            alias = query.filter_by(username=username).first()
            if alias:
                logger.debug(f"بیمار با یوزرنیم {username} پیدا شد. patient_id={alias.patient_id}")
                return alias.patient_id
        
        # اولویت 4: display_name (ضعیف‌ترین)
        if display_name:
            alias = query.filter_by(display_name=display_name).first()
            if alias:
                logger.debug(f"بیمار با display_name {display_name} پیدا شد. patient_id={alias.patient_id}")
                return alias.patient_id
        
        return None
    finally:
        db.close()


def find_patient_by_any_platform(
    phone: Optional[str] = None,
    external_user_id: Optional[str] = None
) -> Optional[int]:
    """
    جستجوی بیمار در تمام پلتفرم‌ها با شماره یا external_user_id
    مفید برای ادغام بیماران بین پلتفرم‌ها
    """
    if not phone and not external_user_id:
        return None
    
    db = SessionLocal()
    try:
        query = db.query(PatientAlias)
        
        if phone:
            alias = query.filter_by(phone=phone).first()
            if alias:
                return alias.patient_id
        
        if external_user_id:
            alias = query.filter_by(external_user_id=external_user_id).first()
            if alias:
                return alias.patient_id
        
        return None
    finally:
        db.close()


# ========== توابع اصلی ایجاد و به‌روزرسانی بیمار ==========
def get_or_create_patient(
    clinic_id: int,
    platform: str,
    external_user_id: str,
    username: Optional[str] = None,
    display_name: Optional[str] = None,
    raw_text: Optional[str] = None
) -> int:
    """
    دریافت یا ایجاد بیمار جدید
    پارامترها:
        clinic_id: شناسه کلینیک
        platform: پلتفرم (telegram, instagram, whatsapp, website)
        external_user_id: شناسه یکتا در پلتفرم
        username: یوزرنیم (اختیاری)
        display_name: نام نمایشی (اختیاری)
        raw_text: متن خام برای استخراج اطلاعات اضافی
    خروجی:
        شناسه بیمار
    """
    # استخراج اطلاعات از متن خام
    phone = extract_phone_number(raw_text) if raw_text else None
    extracted_name = extract_name(raw_text) if raw_text else None
    
    # استفاده از نام استخراج شده یا display_name
    patient_name = extracted_name or display_name
    
    # جستجوی بیمار در همین پلتفرم
    patient_id = find_patient_by_alias(
        platform=platform,
        phone=phone,
        external_user_id=external_user_id,
        username=username,
        display_name=patient_name
    )
    
    db = SessionLocal()
    try:
        if patient_id:
            # بیمار وجود دارد - به‌روزرسانی اطلاعات
            patient = db.query(Patient).filter_by(id=patient_id).first()
            if patient:
                # به‌روزرسانی last_seen
                patient.last_seen = datetime.utcnow()
                
                # به‌روزرسانی نام اگر خالی بود
                if not patient.name and patient_name:
                    patient.name = patient_name
                
                # به‌روزرسانی شماره اگر خالی بود
                if not patient.phone and phone:
                    patient.phone = phone
                db.commit()
            
            # اضافه کردن aliasهای جدید (اگر وجود نداشته باشند)
            add_missing_alias(db, patient_id, platform, phone, username, external_user_id, patient_name)
            
            logger.info(f"بیمار موجود با شناسه {patient_id} به‌روزرسانی شد. پلتفرم: {platform}")
            return patient_id
        
        # بیمار جدید - ایجاد
        # ابتدا بررسی کن آیا با شماره یا external_user_id در پلتفرم دیگر وجود دارد
        merged_patient_id = find_patient_by_any_platform(phone=phone, external_user_id=external_user_id)
        
        if merged_patient_id:
            # ادغام با بیمار موجود از پلتفرم دیگر
            patient = db.query(Patient).filter_by(id=merged_patient_id).first()
            if patient:
                patient.last_seen = datetime.utcnow()
                if not patient.name and patient_name:
                    patient.name = patient_name
                if not patient.phone and phone:
                    patient.phone = phone
                db.commit()
            
            # اضافه کردن alias جدید برای پلتفرم فعلی
            alias = PatientAlias(
                patient_id=merged_patient_id,
                platform=platform,
                external_user_id=external_user_id,
                username=username,
                display_name=patient_name,
                phone=phone,
                confidence=0.9 if phone else 0.7,
                created_at=datetime.utcnow()
            )
            db.add(alias)
            db.commit()
            
            logger.info(f"بیمار ادغام شده با شناسه {merged_patient_id} از پلتفرم {platform} اضافه شد.")
            return merged_patient_id
        
        # ایجاد بیمار کاملاً جدید
        patient = Patient(
            clinic_id=clinic_id,
            name=patient_name,
            phone=phone,
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            status='active',
            created_at=datetime.utcnow()
        )
        db.add(patient)
        db.flush()
        
        # ایجاد alias اصلی
        alias = PatientAlias(
            patient_id=patient.id,
            platform=platform,
            external_user_id=external_user_id,
            username=username,
            display_name=patient_name,
            phone=phone,
            confidence=0.9 if phone else 0.7,
            created_at=datetime.utcnow()
        )
        db.add(alias)
        db.commit()
        
        logger.info(f"بیمار جدید با شناسه {patient.id} ایجاد شد. پلتفرم: {platform}")
        return patient.id
        
    except Exception as e:
        logger.error(f"خطا در get_or_create_patient: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def add_missing_alias(db, patient_id: int, platform: str, phone: Optional[str],
                      username: Optional[str], external_user_id: Optional[str],
                      display_name: Optional[str]):
    """
    اضافه کردن aliasهای جدید برای بیمار (در صورت عدم وجود)
    """
    # بررسی و اضافه کردن alias شماره تلفن
    if phone:
        existing = db.query(PatientAlias).filter_by(
            patient_id=patient_id, platform=platform, phone=phone
        ).first()
        if not existing:
            alias = PatientAlias(
                patient_id=patient_id,
                platform=platform,
                phone=phone,
                confidence=0.9,
                created_at=datetime.utcnow()
            )
            db.add(alias)
    
    # بررسی و اضافه کردن alias یوزرنیم
    if username:
        existing = db.query(PatientAlias).filter_by(
            patient_id=patient_id, platform=platform, username=username
        ).first()
        if not existing:
            alias = PatientAlias(
                patient_id=patient_id,
                platform=platform,
                username=username,
                confidence=0.8,
                created_at=datetime.utcnow()
            )
            db.add(alias)
    
    # بررسی و اضافه کردن alias external_user_id
    if external_user_id:
        existing = db.query(PatientAlias).filter_by(
            patient_id=patient_id, platform=platform, external_user_id=external_user_id
        ).first()
        if not existing:
            alias = PatientAlias(
                patient_id=patient_id,
                platform=platform,
                external_user_id=external_user_id,
                confidence=0.85,
                created_at=datetime.utcnow()
            )
            db.add(alias)
    
    # بررسی و اضافه کردن alias display_name
    if display_name:
        existing = db.query(PatientAlias).filter_by(
            patient_id=patient_id, platform=platform, display_name=display_name
        ).first()
        if not existing:
            alias = PatientAlias(
                patient_id=patient_id,
                platform=platform,
                display_name=display_name,
                confidence=0.6,
                created_at=datetime.utcnow()
            )
            db.add(alias)
    
    db.commit()


# ========== توابع کمکی ==========
def get_patient_aliases(patient_id: int) -> list:
    """
    دریافت تمام aliasهای یک بیمار
    """
    db = SessionLocal()
    try:
        aliases = db.query(PatientAlias).filter_by(patient_id=patient_id).all()
        return [
            {
                "platform": a.platform,
                "external_user_id": a.external_user_id,
                "username": a.username,
                "display_name": a.display_name,
                "phone": a.phone,
                "confidence": a.confidence
            }
            for a in aliases
        ]
    finally:
        db.close()


def merge_patients(master_patient_id: int, slave_patient_id: int) -> bool:
    """
    ادغام دو بیمار (انتقال تمام aliasها به بیمار اصلی)
    """
    db = SessionLocal()
    try:
        # به‌روزرسانی master_patient_id در aliasهای بیمار slave
        db.query(PatientAlias).filter_by(patient_id=slave_patient_id).update(
            {"patient_id": master_patient_id}
        )
        
        # علامت‌گذاری بیمار slave به عنوان ادغام شده
        db.query(Patient).filter_by(id=slave_patient_id).update(
            {"master_patient_id": master_patient_id}
        )
        
        db.commit()
        logger.info(f"بیمار {slave_patient_id} با بیمار {master_patient_id} ادغام شد.")
        return True
    except Exception as e:
        logger.error(f"خطا در ادغام بیماران: {e}")
        db.rollback()
        return False
    finally:
        db.close()
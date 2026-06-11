"""
ماژول بازیابی لیدهای از دست رفته (Lost Lead Recovery)
این ماژول مسئول پیگیری و بازگرداندن لیدهایی است که:
- بیش از مدت مشخصی بدون پاسخ مانده‌اند
- درخواست نوبت داده‌اند اما پیگیری نشده‌اند
- اعتراض خاصی داشته‌اند (قیمت، ترس، اعتماد و...)

استراتژی‌های پیگیری:
1. پیگیری عمومی: برای لیدهای بدون اعتراض خاص
2. پیگیری تخصصی: بر اساس نوع اعتراض (قیمت، ترس، اعتماد، زمان، خانواده)
3. پیگیری مرحله‌ای: حداکثر 3 مرحله با فواصل زمانی متفاوت
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from database import SessionLocal
from models import Lead, PatientAlias, Patient, FollowupWindow, Clinic, Event
from config import BOT_TOKEN, OWNER_TELEGRAM_ID
import requests
import asyncio
import random
import logging

# تنظیم لاگر
logger = logging.getLogger(__name__)

# تنظیمات پیش‌فرض
DEFAULT_FOLLOWUP_DAYS = 3           # روز اول پیگیری
SECOND_FOLLOWUP_DAYS = 7            # روز دوم پیگیری
THIRD_FOLLOWUP_DAYS = 14            # روز سوم پیگیری
MAX_RECOVERY_ATTEMPTS = 3           # حداکثر تعداد پیگیری
RECOVERY_COOLDOWN_HOURS = 48        # فاصله زمانی بین پیگیری‌ها (ساعت)


async def send_telegram_message(chat_id: int, text: str) -> bool:
    """
    ارسال پیام به تلگرام
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info(f"پیام بازیابی با موفقیت به {chat_id} ارسال شد.")
            return True
        else:
            logger.warning(f"خطا در ارسال پیام به {chat_id}: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"خطا در ارسال پیام به تلگرام: {e}")
        return False


def get_followup_days_for_service(service: str, clinic_id: int) -> int:
    """
    دریافت فاصله زمانی پیگیری بر اساس نوع خدمت
    """
    db = SessionLocal()
    try:
        window = db.query(FollowupWindow).filter_by(
            clinic_id=clinic_id, 
            service=service
        ).first()
        if window:
            return window.days_after
    except Exception as e:
        logger.error(f"خطا در دریافت FollowupWindow: {e}")
    finally:
        db.close()
    
    # مقادیر پیش‌فرض بر اساس نوع خدمت
    defaults = {
        'botox': 5,
        'filler': 7,
        'laser': 10,
        'mesotherapy': 14,
        'surgery': 21,
        'none': DEFAULT_FOLLOWUP_DAYS
    }
    return defaults.get(service, DEFAULT_FOLLOWUP_DAYS)


def get_recovery_message_template(objection_category: str, service: str, lang: str = 'fa') -> str:
    """
    دریافت الگوی پیام بر اساس نوع اعتراض
    """
    templates = {
        'price': {
            'fa': [
                "سلام 🌷\nچند روز پیش درباره {service} سوال داشتید.\nاگر نگران هزینه هستید، می‌توانید شرایط اقساط یا مشاوره رایگان را بررسی کنیم.\nآیا همچنان تمایل دارید وقت بگیرید؟",
                "سلام مجدد 🌷\nهزینه {service} بسته به شرایط متفاوت است.\nبرای اطلاع دقیق، پیشنهاد می‌کنم یک مشاوره رایگان داشته باشید.\nچه روزی برای شما مناسبه؟",
                "🌷 در خدمتم.\nاگر هزینه {service} دغدغه شماست، خوشحال میشم گزینه‌های مختلف رو براتون توضیح بدم.\nزمانی براتون مناسب هست صحبت کنیم؟",
                "سلام 🌷\nمی‌دونم قیمت‌ها مهمه.\nپیشنهاد می‌کنم یک جلسه مشاوره رایگان داشته باشید تا همه چیز رو کامل توضیح بدیم.\nموافقید؟"
            ]
        },
        'fear': {
            'fa': [
                "سلام 🌷\nنگرانی شما درباره {service} کاملاً طبیعی است.\nبسیاری از بیماران همین احساس را دارند.\nاگر مایلید، می‌توانیم یک جلسه مشاوره رایگان برای رفع نگرانی‌تان ترتیب بدیم.\nنظر شما چیه؟",
                "🌷 درک می‌کنم که نگران هستید.\nپزشک ما با حوصله تمام مراحل رو توضیح میده و به سوالات شما پاسخ میده.\nمی‌تونید یک جلسه مشاوره داشته باشید تا خیالتون راحت بشه.\nموافقید؟",
                "سلام 🌷\nترس از ناشناخته‌ها طبیعیه.\nبهتون پیشنهاد می‌کنم قبل از هر تصمیمی، یک مشاوره رایگان با پزشک داشته باشید.\nآماده هماهنگی هستم 🌷"
            ]
        },
        'trust': {
            'fa': [
                "سلام 🌷\nمی‌تونم نمونه کارها و نظرات بیماران قبلی رو براتون بفرستم.\nکیفیت کار و تجربه بیماران می‌تونه به تصمیم‌گیری شما کمک کنه.\nآیا مایلید اطلاعات بیشتری بفرستم؟",
                "🌷 اعتماد مهمترین چیزه.\nپزشک ما سال‌ها سابقه و تخصص در {service} داره.\nمی‌تونید قبل از تصمیم، یک مشاوره بدون تعهد داشته باشید.\nموافقید؟",
                "سلام 🌷\nمی‌تونم براتون نمونه کارهای واقعی رو نمایش بدم.\nبیماران قبلی ما رضایت بالایی داشتن.\nخوشحال میشم بیشتر توضیح بدم 🌷"
            ]
        },
        'family': {
            'fa': [
                "سلام 🌷\nدرک می‌کنم که نظر خانواده مهمه.\nاگر خانواده شما هم مایل باشند، می‌تونیم یک جلسه مشاوره گروهی داشته باشیم تا همه سوالاتشون پاسخ داده بشه.\nچطوره؟",
                "🌷 می‌تونیم با خانواده شما هم صحبت کنیم تا اطلاعات کامل رو دریافت کنن.\nبسیاری از خانواده‌ها بعد از مشاوره نظر مثبت پیدا می‌کنن.\nخواهش می‌کنم اگه مناسب هست، هماهنگ کنیم.",
                "سلام 🌷\nکاملاً درک می‌کنم.\nپیشنهاد می‌کنم خانواده شما هم در مشاوره حضور داشته باشن.\nهماهنگ کنم؟ 🌷"
            ]
        },
        'time': {
            'fa': [
                "سلام 🌷\nمی‌دونم وقت گیره.\nما ساعات کاری منعطفی داریم و می‌تونیم نوبت رو در زمان دلخواه شما تنظیم کنیم.\nچه روزها و ساعتی براتون مناسبه؟",
                "🌷 برای راحتی شما، می‌تونیم نوبت رو عصرها یا آخر هفته هم تنظیم کنیم.\nفقط ۳۰ دقیقه زمان نیاز دارید.\nچه روزی می‌تونید بیاید؟",
                "سلام 🌷\nفقط ۲۰ دقیقه از وقت شما رو می‌گیره.\nمیشه براتون نوبت سریع تنظیم کنم.\nکی براتون مناسبه؟ 🌷"
            ]
        },
        'general': {
            'fa': [
                "سلام 🌷\nچند روز پیش درباره {service} سوال داشتید.\nآیا هنوز نیاز به راهنمایی دارید؟\nخوشحال میشم کمک کنم.",
                "🌍 در خدمتم.\nاگر درباره {service} سوالی دارید، بپرسید.\nهمچنین می‌تونید یک مشاوره رایگان داشته باشید.\nنظر شما چیه؟",
                "سلام مجدد 🌷\nامیدوارم حالتون خوب باشه.\nفقط یادآوری کنم که اگر هنوز درباره {service} سوالی دارید، در خدمتم.\nموفق باشید 🌷",
                "سلام 🌷\nچند روزی از پیام قبلی شما گذشت.\nاگر هنوز سوالی دارید، خوشحال میشم کمک کنم.\nدر غیر این صورت، براتون آرزوی موفقیت دارم 🌷"
            ]
        }
    }
    
    # انتخاب تصادفی از بین چند الگو (برای طبیعی‌تر شدن)
    messages = templates.get(objection_category, templates['general'])
    if isinstance(messages, dict):
        messages = messages.get(lang, messages['fa'])
    
    if messages:
        template = random.choice(messages)
        return template.format(service=service)
    
    return templates['general']['fa'][0].format(service=service)


async def send_recovery_message(
    lead_id: int, 
    patient_id: int, 
    objection_category: str, 
    service: str,
    attempt: int
) -> bool:
    """
    ارسال پیام بازیابی به بیمار
    """
    db = SessionLocal()
    try:
        # دریافت اطلاعات بیمار (شماره تلگرام)
        alias = db.query(PatientAlias).filter_by(
            patient_id=patient_id, 
            platform='telegram'
        ).first()
        
        if not alias or not alias.external_user_id:
            logger.warning(f"شماره تلگرام برای بیمار {patient_id} یافت نشد.")
            return False
        
        # دریافت زبان ترجیحی بیمار
        patient = db.query(Patient).filter_by(id=patient_id).first()
        lang = patient.preferred_language if patient and patient.preferred_language else 'fa'
        
        # دریافت الگوی پیام مناسب
        message = get_recovery_message_template(objection_category, service, lang)
        
        # اضافه کردن مرحله پیگیری (برای شفافیت)
        if attempt == 1:
            message += "\n\n(این آخرین یادآوری نیست، فقط یک پیگیری دوستانه است 🌷)"
        elif attempt == 2:
            message += "\n\n(هنوز فرصت هست، خوشحال میشم بتونم کمکتون کنم 🌷)"
        elif attempt == 3:
            message += "\n\n(اگر علاقه‌ای ندارید، لطفاً بگید تا مزاحمتون نشم 🌷)"
        
        # ارسال پیام
        success = await send_telegram_message(int(alias.external_user_id), message)
        
        # به‌روزرسانی زمان آخرین پیگیری
        if success:
            lead = db.query(Lead).filter_by(id=lead_id).first()
            if lead:
                lead.last_followup = datetime.utcnow()
                db.commit()
                logger.info(f"پیام بازیابی برای لید {lead_id} (تلاش {attempt}) ارسال شد.")
        
        return success
    except Exception as e:
        logger.error(f"خطا در ارسال پیام بازیابی برای لید {lead_id}: {e}")
        return False
    finally:
        db.close()


async def recover_lost_leads():
    """
    بازیابی لیدهای از دست رفته
    این تابع توسط scheduler هر روز اجرا می‌شود
    """
    logger.info("🔄 شروع بازیابی لیدهای از دست رفته...")
    db = SessionLocal()
    now = datetime.utcnow()
    
    try:
        # دریافت همه لیدهای فعال که نیاز به پیگیری دارند
        leads = db.query(Lead).filter(
            Lead.pipeline_stage == 'new',  # فقط لیدهای جدید
            Lead.recovery_attempts < MAX_RECOVERY_ATTEMPTS,  # کمتر از حداکثر تلاش
        ).all()
        
        recovered_count = 0
        skipped_count = 0
        
        for lead in leads:
            # محاسبه زمان مناسب برای پیگیری بر اساس نوع خدمت
            followup_days = get_followup_days_for_service(lead.service, lead.clinic_id)
            
            # تعیین زمان پیگیری بعدی بر اساس تلاش‌های قبلی
            if lead.recovery_attempts == 0:
                # اولین پیگیری: بعد از followup_days روز
                next_followup_date = lead.created_at + timedelta(days=followup_days)
            elif lead.recovery_attempts == 1:
                # دومین پیگیری: بعد از SECOND_FOLLOWUP_DAYS روز از اولین پیگیری
                next_followup_date = lead.last_followup + timedelta(days=SECOND_FOLLOWUP_DAYS)
            else:
                # سومین پیگیری: بعد از THIRD_FOLLOWUP_DAYS روز از دومین پیگیری
                next_followup_date = lead.last_followup + timedelta(days=THIRD_FOLLOWUP_DAYS)
            
            # اگر زمان پیگیری نرسیده، skip
            if now < next_followup_date:
                skipped_count += 1
                continue
            
            # ارسال پیام بازیابی
            objection = lead.objection_category or 'general'
            success = await send_recovery_message(
                lead.id, 
                lead.patient_id, 
                objection, 
                lead.service, 
                lead.recovery_attempts + 1
            )
            
            if success:
                lead.recovery_attempts += 1
                recovered_count += 1
                logger.info(f"✅ پیگیری لید {lead.id} - تلاش {lead.recovery_attempts}")
                
                # اگر به حداکثر تلاش رسید، وضعیت لید به lost تغییر یابد
                if lead.recovery_attempts >= MAX_RECOVERY_ATTEMPTS:
                    lead.pipeline_stage = 'lost'
                    logger.info(f"⚠️ لید {lead.id} پس از {MAX_RECOVERY_ATTEMPTS} تلاش بی‌نتیجه به lost تغییر یافت.")
                
                db.commit()
            
            # جلوگیری از rate limit
            await asyncio.sleep(0.5)
        
        db.commit()
        logger.info(f"✅ بازیابی لیدها: {recovered_count} پیام ارسال شد، {skipped_count} لید نیاز به پیگیری نداشتند.")
        return recovered_count
        
    except Exception as e:
        logger.error(f"خطا در بازیابی لیدها: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


async def recover_specific_lead(lead_id: int, custom_message: Optional[str] = None) -> bool:
    """
    بازیابی دستی یک لید خاص (برای استفاده منشی)
    """
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter_by(id=lead_id).first()
        if not lead:
            logger.warning(f"لید {lead_id} یافت نشد.")
            return False
        
        if custom_message:
            message = custom_message
        else:
            objection = lead.objection_category or 'general'
            message = get_recovery_message_template(objection, lead.service, 'fa')
        
        alias = db.query(PatientAlias).filter_by(patient_id=lead.patient_id, platform='telegram').first()
        if alias and alias.external_user_id:
            success = await send_telegram_message(int(alias.external_user_id), message)
            if success:
                lead.last_followup = datetime.utcnow()
                lead.recovery_attempts += 1
                db.commit()
                logger.info(f"پیگیری دستی لید {lead_id} انجام شد.")
                return True
        
        return False
    except Exception as e:
        logger.error(f"خطا در بازیابی دستی لید {lead_id}: {e}")
        return False
    finally:
        db.close()


def get_leads_needing_recovery(clinic_id: int, days: int = 7) -> List[Dict]:
    """
    دریافت لیست لیدهایی که نیاز به پیگیری دارند (برای نمایش در داشبورد)
    """
    db = SessionLocal()
    now = datetime.utcnow()
    cutoff = now - timedelta(days=days)
    
    try:
        leads = db.query(Lead, Patient).join(Patient).filter(
            Lead.clinic_id == clinic_id,
            Lead.pipeline_stage == 'new',
            Lead.recovery_attempts < MAX_RECOVERY_ATTEMPTS,
            Lead.created_at < cutoff
        ).all()
        
        result = []
        for lead, patient in leads:
            result.append({
                'id': lead.id,
                'patient_name': patient.name or 'نامشخص',
                'patient_phone': patient.phone or 'ندارد',
                'service': lead.service or 'نامشخص',
                'lead_score': lead.lead_score,
                'objection': lead.objection_category or 'general',
                'attempts': lead.recovery_attempts,
                'created_at': lead.created_at.isoformat(),
                'days_passed': (now - lead.created_at).days
            })
        
        return result
    except Exception as e:
        logger.error(f"خطا در دریافت لیدهای نیازمند پیگیری: {e}")
        return []
    finally:
        db.close()


def reset_recovery_attempts(lead_id: int) -> bool:
    """
    بازنشانی شمارش تلاش‌های پیگیری (زمانی که بیمار پاسخ داد)
    """
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter_by(id=lead_id).first()
        if lead:
            lead.recovery_attempts = 0
            if lead.pipeline_stage == 'lost':
                lead.pipeline_stage = 'new'
            db.commit()
            logger.info(f"تلاش‌های پیگیری لید {lead_id} بازنشانی شد.")
            return True
        return False
    except Exception as e:
        logger.error(f"خطا در بازنشانی تلاش‌های لید {lead_id}: {e}")
        return False
    finally:
        db.close()


def get_recovery_statistics(clinic_id: int, days: int = 30) -> Dict:
    """
    دریافت آمار بازیابی لیدها برای یک دوره مشخص
    """
    db = SessionLocal()
    now = datetime.utcnow()
    cutoff = now - timedelta(days=days)
    
    try:
        # لیدهایی که حداقل یک بار پیگیری شده‌اند
        recovered_leads = db.query(Lead).filter(
            Lead.clinic_id == clinic_id,
            Lead.recovery_attempts > 0,
            Lead.created_at >= cutoff
        ).all()
        
        total = len(recovered_leads)
        successful = sum(1 for l in recovered_leads if l.pipeline_stage == 'booked')
        failed = sum(1 for l in recovered_leads if l.pipeline_stage == 'lost')
        pending = total - successful - failed
        
        # میانگین تلاش‌ها
        avg_attempts = sum(l.recovery_attempts for l in recovered_leads) / total if total > 0 else 0
        
        # توزیع اعتراضات
        objections = {}
        for lead in recovered_leads:
            obj = lead.objection_category or 'general'
            objections[obj] = objections.get(obj, 0) + 1
        
        return {
            "period_days": days,
            "total_leads_recovered": total,
            "successful_conversions": successful,
            "failed_conversions": failed,
            "pending": pending,
            "success_rate": round(successful / total * 100, 2) if total > 0 else 0,
            "avg_recovery_attempts": round(avg_attempts, 2),
            "objections_distribution": objections
        }
    except Exception as e:
        logger.error(f"خطا در دریافت آمار بازیابی: {e}")
        return {}
    finally:
        db.close()
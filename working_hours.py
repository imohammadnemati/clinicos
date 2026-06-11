"""
ماژول ساعات کاری هوشمند (Smart Working Hours)
این ماژول مسئول مدیریت پاسخگویی خودکار بات در خارج از ساعات کاری کلینیک است.
از حفظ مکالمات فعال در شب پشتیبانی می‌کند و تجربه کاربری روانی را فراهم می‌آورد.
"""

from datetime import datetime, time, timedelta
from typing import Tuple, Optional
from database import SessionLocal
from models import ClinicWorkingHours, Session


def get_clinic_working_hours(clinic_id: int) -> Optional[Tuple[time, time, int]]:
    """
    دریافت ساعات کاری کلینیک از دیتابیس
    پارامترها:
        clinic_id: شناسه کلینیک
    خروجی:
        (ساعت شروع, ساعت پایان, زمان فعال بودن مکالمه بر حسب دقیقه) یا None در صورت عدم تنظیم
    """
    db = SessionLocal()
    wh = db.query(ClinicWorkingHours).filter_by(clinic_id=clinic_id).first()
    db.close()
    
    if wh:
        return (wh.start_time, wh.end_time, wh.active_timeout_minutes)
    return None


def is_within_working_hours(clinic_id: int, current_time: Optional[datetime] = None) -> bool:
    """
    بررسی آیا زمان فعلی در ساعات کاری کلینیک است
    پارامترها:
        clinic_id: شناسه کلینیک
        current_time: زمان فعلی (اختیاری، پیش‌فرض زمان حال)
    خروجی:
        True اگر در ساعات کاری باشد، False در غیر این صورت
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    wh = get_clinic_working_hours(clinic_id)
    if not wh:
        # اگر ساعات کاری تنظیم نشده، فرض می‌کنیم همیشه فعال است
        return True
    
    start_time, end_time, _ = wh
    current_time_only = current_time.time()
    
    # مدیریت بازه‌های شب (مثلاً 22:00 تا 08:00)
    if start_time <= end_time:
        # بازه عادی (مثلاً 08:00 تا 22:00)
        return start_time <= current_time_only <= end_time
    else:
        # بازه شب (مثلاً 22:00 تا 08:00)
        return current_time_only >= start_time or current_time_only <= end_time


def is_active_conversation(session_id: int, db, timeout_minutes: int = 30) -> bool:
    """
    بررسی آیا مکالمه فعال است (در 30 دقیقه اخیر پیامی رد و بدل شده)
    پارامترها:
        session_id: شناسه جلسه مکالمه
        db: نشست دیتابیس (برای تزریق)
        timeout_minutes: حداکثر زمان سکوت برای غیرفعال شدن مکالمه
    خروجی:
        True اگر مکالمه فعال باشد، False در غیر این صورت
    """
    session = db.query(Session).filter_by(id=session_id).first()
    if not session or not session.last_activity:
        return False
    
    now = datetime.utcnow()
    time_since_last_activity = now - session.last_activity
    return time_since_last_activity < timedelta(minutes=timeout_minutes)


def update_session_activity(session_id: int, db) -> None:
    """
    به‌روزرسانی زمان آخرین فعالیت جلسه
    پارامترها:
        session_id: شناسه جلسه
        db: نشست دیتابیس
    """
    db.query(Session).filter_by(id=session_id).update({"last_activity": datetime.utcnow()})
    db.commit()


def can_auto_reply(clinic_id: int, session_id: int, db, current_time: Optional[datetime] = None) -> Tuple[bool, str]:
    """
    تصمیم‌گیری درباره امکان ارسال پاسخ خودکار
    پارامترها:
        clinic_id: شناسه کلینیک
        session_id: شناسه جلسه
        db: نشست دیتابیس (برای تزریق)
        current_time: زمان فعلی (اختیاری)
    خروجی:
        (آیا پاسخ دهد؟, دلیل/پیام)
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    wh = get_clinic_working_hours(clinic_id)
    if not wh:
        return True, "در ساعات کاری (پیش‌فرض)"
    
    start_time, end_time, active_timeout = wh
    within_hours = is_within_working_hours(clinic_id, current_time)
    
    # به‌روزرسانی آخرین فعالیت جلسه
    update_session_activity(session_id, db)
    
    # حالت 1: داخل ساعات کاری هستیم
    if within_hours:
        return True, "در ساعات کاری"
    
    # حالت 2: خارج از ساعات کاری، اما مکالمه فعال است
    if is_active_conversation(session_id, db, active_timeout):
        return True, "مکالمه فعال ادامه دارد"
    
    # حالت 3: خارج از ساعات کاری و مکالمه فعال نیست
    return False, "خارج از ساعات کاری و مکالمه فعال نیست"


def get_out_of_hours_message(lang: str = 'fa') -> str:
    """
    دریافت پیام مناسب برای پاسخ خارج از ساعات کاری
    پارامترها:
        lang: زبان (fa, en, ar)
    خروجی:
        متن پیام
    """
    messages = {
        'fa': "🌙 سلام.\nپیام شما ثبت شد. همکاران ما از ساعت ۸ صبح پاسخگوی شما خواهند بود و در اولین فرصت با شما ارتباط می‌گیرند.\nشب خوش 🌷",
        'en': "🌙 Hello.\nYour message has been recorded. Our team will respond from 8 AM and will get back to you as soon as possible.\nGood night 🌷",
        'ar': "🌙 مرحباً.\nتم تسجيل رسالتك. سيقوم فريقنا بالرد اعتباراً من الساعة 8 صباحاً وسيتواصل معك في أقرب فرصة.\nليلة سعيدة 🌷"
    }
    return messages.get(lang, messages['fa'])


def get_out_of_hours_but_active_message(lang: str = 'fa') -> str:
    """
    دریافت پیام برای زمانی که خارج از ساعات کاری هستیم اما مکالمه فعال است
    (برای یادآوری به کاربر که پاسخ‌ها ممکن است با تأخیر همراه باشد)
    """
    messages = {
        'fa': "🌙 در حال حاظر خارج از ساعات کاری کلینیک هستیم. پیام شما را دریافت کردم و سعی می‌کنم پاسخ دهم، اما ممکن است پاسخ‌های تخصصی با کمی تأخیر همراه باشد.",
        'en': "🌙 We are currently outside of business hours. I received your message and will try to respond, but some answers may be delayed.",
        'ar': "🌙 نحن حالياً خارج ساعات العمل. لقد تلقيت رسالتك وسأحاول الرد، ولكن قد تتأخر بعض الردود."
    }
    return messages.get(lang, messages['fa'])


def set_clinic_working_hours(clinic_id: int, start_time: time, end_time: time, active_timeout_minutes: int = 30) -> bool:
    """
    تنظیم ساعات کاری کلینیک
    پارامترها:
        clinic_id: شناسه کلینیک
        start_time: ساعت شروع (مثال: time(8, 0))
        end_time: ساعت پایان (مثال: time(22, 0))
        active_timeout_minutes: مدت زمان فعال بودن مکالمه خارج از ساعت (دقیقه)
    خروجی:
        True در صورت موفقیت، False در غیر این صورت
    """
    try:
        db = SessionLocal()
        wh = db.query(ClinicWorkingHours).filter_by(clinic_id=clinic_id).first()
        
        if wh:
            wh.start_time = start_time
            wh.end_time = end_time
            wh.active_timeout_minutes = active_timeout_minutes
        else:
            wh = ClinicWorkingHours(
                clinic_id=clinic_id,
                start_time=start_time,
                end_time=end_time,
                active_timeout_minutes=active_timeout_minutes
            )
            db.add(wh)
        
        db.commit()
        db.close()
        return True
    except Exception as e:
        print(f"خطا در تنظیم ساعات کاری: {e}")
        return False


def get_default_working_hours() -> Tuple[time, time, int]:
    """
    دریافت ساعات کاری پیش‌فرض
    خروجی:
        (ساعت شروع, ساعت پایان, زمان فعال بودن مکالمه)
    """
    return time(8, 0), time(22, 0), 30
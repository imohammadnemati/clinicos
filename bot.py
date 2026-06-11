"""
فایل اصلی بات تلگرام (Telegram Bot)
این فایل مسئول راه‌اندازی و مدیریت بات تلگرام است.
شامل:
- ثبت کاربران داخلی (پزشک، منشی، مالک)
- مدیریت مکالمات بیماران
- ارسال پیام به patient_agent برای پردازش
- دستورات مدیریتی مانند /invite
"""

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, OWNER_TELEGRAM_ID
from database import init_db, SessionLocal
from models import Staff, Clinic, Patient
from patient_agent import process_patient_message
from scheduler import start_scheduler
from datetime import datetime
import asyncio
import logging

# تنظیم لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    دستور /start - ثبت کاربر جدید یا نمایش وضعیت
    """
    tid = update.effective_user.id
    name = update.effective_user.first_name
    username = update.effective_user.username
    
    db = SessionLocal()
    try:
        # بررسی آیا کاربر در جدول staff وجود دارد
        staff = db.query(Staff).filter_by(telegram_id=tid).first()
        
        if staff:
            # کاربر داخلی است
            await update.message.reply_text(
                f"🧠 *کلینیک برین*\n\n"
                f"به سیستم مدیریت کلینیک خوش آمدید.\n\n"
                f"👤 نام: {staff.name}\n"
                f"📋 نقش: {staff.role}\n"
                f"🆔 شناسه: {staff.id}\n\n"
                f"دستورات مدیریت:\n"
                f"/invite [telegram_id] [role] - دعوت کاربر جدید\n"
                f"/confirm_appt [request_id] [date] - تأیید نوبت\n"
                f"/stats - آمار امروز",
                parse_mode='Markdown'
            )
        else:
            # کاربر عادی (بیمار) - فقط مالک می‌تواند کارمند اضافه کند
            if tid == OWNER_TELEGRAM_ID:
                # ایجاد کلینیک پیش‌فرض و ثبت مالک
                clinic = db.query(Clinic).first()
                if not clinic:
                    clinic = Clinic(name="کلینیک پیش‌فرض", subdomain="default", created_at=datetime.utcnow())
                    db.add(clinic)
                    db.commit()
                    logger.info(f"کلینیک پیش‌فرض با شناسه {clinic.id} ایجاد شد.")
                
                # بررسی نکنه قبلاً ثبت شده
                existing = db.query(Staff).filter_by(telegram_id=tid).first()
                if not existing:
                    owner = Staff(
                        clinic_id=clinic.id,
                        telegram_id=tid,
                        name=name,
                        role="owner",
                        created_at=datetime.utcnow()
                    )
                    db.add(owner)
                    db.commit()
                    logger.info(f"مالک جدید با شناسه {tid} ثبت شد.")
                
                await update.message.reply_text(
                    "👑 *شما به عنوان مالک کلینیک ثبت شدید.*\n\n"
                    "دستورات:\n"
                    "/invite [telegram_id] [role] - دعوت منشی یا پزشک\n"
                    "/stats - مشاهده آمار",
                    parse_mode='Markdown'
                )
            else:
                # کاربر عادی که هنوز ثبت نشده
                await update.message.reply_text(
                    "🩺 *به کلینیک برین خوش آمدید*\n\n"
                    "این بات به شما کمک می‌کند تا پاسخ سوالات خود را دریافت کنید.\n"
                    "لطفاً سوال خود را بپرسید.",
                    parse_mode='Markdown'
                )
    except Exception as e:
        logger.error(f"خطا در دستور start: {e}")
        await update.message.reply_text("خطا در پردازش درخواست. لطفاً دقایقی دیگر تلاش کنید.")
    finally:
        db.close()


async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    دستور /invite - دعوت کاربر جدید (فقط مالک)
    فرمت: /invite [telegram_id] [role]
    نقش‌ها: doctor, secretary
    """
    tid = update.effective_user.id
    
    db = SessionLocal()
    try:
        # بررسی مالک بودن کاربر
        owner = db.query(Staff).filter_by(telegram_id=tid, role='owner').first()
        if not owner:
            await update.message.reply_text("⛔ فقط مالک کلینیک می‌تواند کاربر جدید دعوت کند.")
            return
        
        if len(context.args) != 2:
            await update.message.reply_text(
                "❌ فرمت اشتباه.\n"
                "فرمت صحیح: `/invite [telegram_id] [role]`\n"
                "نقش‌ها: `doctor` یا `secretary`",
                parse_mode='Markdown'
            )
            return
        
        try:
            new_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ شناسه تلگرام باید عدد باشد.")
            return
        
        role = context.args[1].lower()
        if role not in ['doctor', 'secretary']:
            await update.message.reply_text("❌ نقش باید `doctor` یا `secretary` باشد.", parse_mode='Markdown')
            return
        
        # بررسی وجود کاربر
        existing = db.query(Staff).filter_by(telegram_id=new_id).first()
        if existing:
            await update.message.reply_text(f"⚠️ کاربر با شناسه {new_id} قبلاً ثبت شده است.")
            return
        
        # ایجاد کاربر جدید
        new_staff = Staff(
            clinic_id=owner.clinic_id,
            telegram_id=new_id,
            name=f"کاربر {new_id}",
            role=role,
            invited_by=owner.id,
            created_at=datetime.utcnow()
        )
        db.add(new_staff)
        db.commit()
        
        await update.message.reply_text(
            f"✅ کاربر با شناسه `{new_id}` به عنوان `{role}` دعوت شد.\n"
            f"کاربر مورد نظر باید بات را استارت کند (ارسال /start).",
            parse_mode='Markdown'
        )
        logger.info(f"کاربر جدید با شناسه {new_id} به عنوان {role} دعوت شد.")
        
    except Exception as e:
        logger.error(f"خطا در دستور invite: {e}")
        await update.message.reply_text("خطا در پردازش درخواست.")
    finally:
        db.close()


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    دستور /stats - نمایش آمار امروز (فقط کارکنان)
    """
    tid = update.effective_user.id
    
    db = SessionLocal()
    try:
        staff = db.query(Staff).filter_by(telegram_id=tid).first()
        if not staff:
            await update.message.reply_text("⛔ شما دسترسی به این دستور ندارید.")
            return
        
        # آمار ساده از دیتابیس
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        from models import RawMessage, Lead, Appointment
        
        messages_today = db.query(RawMessage).filter(
            RawMessage.clinic_id == staff.clinic_id,
            RawMessage.created_at >= today_start
        ).count()
        
        leads_today = db.query(Lead).filter(
            Lead.clinic_id == staff.clinic_id,
            Lead.created_at >= today_start
        ).count()
        
        appointments_today = db.query(Appointment).filter(
            Appointment.clinic_id == staff.clinic_id,
            Appointment.appointment_date >= today_start
        ).count()
        
        await update.message.reply_text(
            f"📊 *آمار امروز*\n\n"
            f"📨 پیام‌ها: {messages_today}\n"
            f"🎯 لیدها: {leads_today}\n"
            f"📅 نوبت‌ها: {appointments_today}\n\n"
            f"برای اطلاعات بیشتر به داشبورد مراجعه کنید.",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"خطا در دستور stats: {e}")
        await update.message.reply_text("خطا در دریافت آمار.")
    finally:
        db.close()


async def confirm_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    دستور /confirm_appt - تأیید نوبت (فقط کارکنان)
    فرمت: /confirm_appt [request_id] [YYYY-MM-DD HH:MM]
    """
    tid = update.effective_user.id
    
    db = SessionLocal()
    try:
        staff = db.query(Staff).filter_by(telegram_id=tid).first()
        if not staff or staff.role not in ['owner', 'doctor', 'secretary']:
            await update.message.reply_text("⛔ شما دسترسی به این دستور ندارید.")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ فرمت اشتباه.\n"
                "فرمت صحیح: `/confirm_appt [request_id] [YYYY-MM-DD HH:MM]`",
                parse_mode='Markdown'
            )
            return
        
        try:
            request_id = int(context.args[0])
            date_str = ' '.join(context.args[1:])
            confirmed_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            await update.message.reply_text("❌ فرمت تاریخ اشتباه. مثال: `2025-01-15 14:30`", parse_mode='Markdown')
            return
        
        from appointment_engine import confirm_appointment as confirm_appt_func
        success = confirm_appt_func(request_id, confirmed_date, staff.id)
        
        if success:
            await update.message.reply_text(f"✅ نوبت با شناسه {request_id} برای تاریخ {date_str} تأیید شد.")
        else:
            await update.message.reply_text(f"❌ خطا در تأیید نوبت {request_id}. لطفاً شناسه را بررسی کنید.")
            
    except Exception as e:
        logger.error(f"خطا در دستور confirm_appointment: {e}")
        await update.message.reply_text("خطا در پردازش درخواست.")
    finally:
        db.close()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    مدیریت پیام‌های دریافتی
    - کاربران داخلی (کارکنان) پیام‌های خود را دریافت می‌کنند
    - بیماران پیام به patient_agent ارسال می‌شود
    """
    tid = update.effective_user.id
    text = update.message.text or update.message.caption
    
    if not text:
        # پیام بدون متن (ممکن است عکس باشد که در نسخه ساده پشتیبانی نمی‌شود)
        await update.message.reply_text("در حال حاظر فقط پیام متنی پشتیبانی می‌شود.")
        return
    
    db = SessionLocal()
    try:
        # بررسی کاربر داخلی بودن
        staff = db.query(Staff).filter_by(telegram_id=tid).first()
        
        if staff:
            # کاربر داخلی – فقط دستورات را پردازش می‌کند
            if text.startswith('/'):
                # دستورات توسط CommandHandler پردازش می‌شوند
                pass
            else:
                await update.message.reply_text(
                    f"سلام {staff.name} 🌷\n"
                    f"شما به عنوان {staff.role} ثبت شده‌اید.\n"
                    f"برای مدیریت از دستورات استفاده کنید:\n"
                    f"/stats - آمار\n"
                    f"/invite - دعوت کاربر جدید"
                )
        else:
            # بیمار – ارسال به patient_agent
            clinic = db.query(Clinic).first()
            if not clinic:
                await update.message.reply_text("سیستم در حال راه‌اندازی است. لطفاً دقایقی دیگر تلاش کنید.")
                return
            
            clinic_id = clinic.id
            platform = "telegram"
            external_user_id = str(tid)
            
            # پردازش پیام بیمار
            await process_patient_message(
                update=update,
                context=context,
                clinic_id=clinic_id,
                platform=platform,
                external_user_id=external_user_id,
                raw_text=text,
                media_url=None,
                media_type=None,
                transcript=None
            )
    except Exception as e:
        logger.error(f"خطا در handle_message: {e}")
        await update.message.reply_text("خطا در پردازش پیام. لطفاً دقایقی دیگر تلاش کنید.")
    finally:
        db.close()


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت خطاهای全局"""
    logger.error(f"خطا: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("خطای داخلی رخ داده است. لطفاً بعداً تلاش کنید.")


def main():
    """
    تابع اصلی راه‌اندازی بات
    """
    # راه‌اندازی دیتابیس
    init_db()
    logger.info("✅ دیتابیس راه‌اندازی شد.")
    
    # ایجاد اپلیکیشن
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ثبت هندلرهای دستورات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("invite", invite))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("confirm_appt", confirm_appointment))
    
    # هندلر پیام‌های متنی
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # هندلر خطا
    application.add_error_handler(error_handler)
    
    # راه‌اندازی زمان‌بند وظایف شبانه
    start_scheduler()
    logger.info("⏰ زمان‌بند وظایف راه‌اندازی شد.")
    
    # استارت بات
    logger.info("🚀 بات در حال راه‌اندازی...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logger.info("✅ بات متوقف شد.")


if __name__ == "__main__":
    main()
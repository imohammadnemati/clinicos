from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, OWNER_TELEGRAM_ID
from database import init_db, SessionLocal
from models import Staff, Clinic
from patient_agent import process_patient_message
from voice_transcriber import transcribe_voice
from scheduler import start_scheduler
import tempfile
import os
from datetime import datetime

async def start(update: Update, context):
    tid = update.effective_user.id
    db = SessionLocal()
    staff = db.query(Staff).filter_by(telegram_id=tid).first()
    if staff:
        await update.message.reply_text(f"🧠 خوش آمدید {staff.name}\nنقش: {staff.role}")
    else:
        if tid == OWNER_TELEGRAM_ID:
            clinic = db.query(Clinic).first()
            if not clinic:
                clinic = Clinic(name="Default Clinic", subdomain="default")
                db.add(clinic)
                db.commit()
            owner = Staff(clinic_id=clinic.id, telegram_id=tid, name=update.effective_user.first_name, role="owner")
            db.add(owner)
            db.commit()
            await update.message.reply_text("شما به عنوان مالک کلینیک ثبت شدید. برای دعوت منشی از /invite استفاده کنید.")
        else:
            await update.message.reply_text("شما دسترسی ندارید. لطفاً با مالک کلینیک تماس بگیرید.")
    db.close()

async def invite(update: Update, context):
    tid = update.effective_user.id
    db = SessionLocal()
    owner = db.query(Staff).filter_by(telegram_id=tid, role='owner').first()
    if not owner:
        await update.message.reply_text("فقط مالک کلینیک می‌تواند منشی دعوت کند.")
        db.close()
        return
    if len(context.args) != 2:
        await update.message.reply_text("فرمت: /invite [telegram_id] [role] (doctor, secretary)")
        db.close()
        return
    new_id = int(context.args[0])
    role = context.args[1]
    if role not in ['doctor', 'secretary']:
        await update.message.reply_text("نقش باید doctor یا secretary باشد.")
        db.close()
        return
    existing = db.query(Staff).filter_by(telegram_id=new_id).first()
    if existing:
        await update.message.reply_text("این کاربر قبلاً ثبت شده است.")
        db.close()
        return
    new_staff = Staff(clinic_id=owner.clinic_id, telegram_id=new_id, name="کاربر جدید", role=role, invited_by=owner.id)
    db.add(new_staff)
    db.commit()
    await update.message.reply_text(f"کاربر با شناسه {new_id} به عنوان {role} دعوت شد.")
    db.close()

async def handle_message(update: Update, context):
    tid = update.effective_user.id
    db = SessionLocal()
    staff = db.query(Staff).filter_by(telegram_id=tid).first()
    db.close()
    if staff:
        # For simplicity in polling version, just echo or handle commands
        text = update.message.text
        if text.startswith('/invite'):
            await invite(update, context)
        else:
            await update.message.reply_text("شما به عنوان کاربر داخلی ثبت شده‌اید. برای مدیریت به پنل مراجعه کنید.")
        return
    # patient
    clinic = db.query(Clinic).first()
    if not clinic:
        await update.message.reply_text("سیستم در حال راه‌اندازی است.")
        return
    clinic_id = clinic.id
    platform = "telegram"
    external_user_id = str(tid)
    text = update.message.text or update.message.caption
    media_url = None
    media_type = None
    transcript = None
    if update.message.voice:
        media_type = "voice"
        file = await context.bot.get_file(update.message.voice.file_id)
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            await file.download_to_drive(tmp.name)
            tmp_path = tmp.name
        transcript = await transcribe_voice(tmp_path)
        os.unlink(tmp_path)
    elif update.message.photo:
        media_type = "photo"
        media_url = update.message.photo[-1].file_id
    elif update.message.video:
        media_type = "video"
        media_url = update.message.video.file_id
    await process_patient_message(update, context, clinic_id, platform, external_user_id, text, media_url, media_type, transcript)

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("invite", invite))
    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE | filters.PHOTO | filters.VIDEO, handle_message))
    start_scheduler()
    print("✅ ClinicOS نسخه کامل راه‌اندازی شد.")
    app.run_polling()

if __name__ == "__main__":
    main()
import os
import sys
import asyncio
import threading
import logging
from flask import Flask, request, jsonify
import requests
from config import BOT_TOKEN, OWNER_TELEGRAM_ID
from database import SessionLocal, init_db
from models import Clinic, Staff
from patient_agent import process_patient_message

# تنظیم لاگینگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# اطمینان از ایجاد جداول دیتابیس
init_db()


def get_or_create_default_clinic():
    """دریافت کلینیک پیش‌فرض (برای MVP تک کلینیکی)"""
    db = SessionLocal()
    try:
        clinic = db.query(Clinic).first()
        if not clinic:
            clinic = Clinic(name="کلینیک پیش‌فرض", subdomain="default")
            db.add(clinic)
            db.commit()
            logger.info(f"کلینیک پیش‌فرض با ID {clinic.id} ایجاد شد.")
        return clinic.id
    finally:
        db.close()


def run_async_in_thread(coro):
    """اجرای یک تابع async در یک ترد جداگانه (برای استفاده در Flask)"""
    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro)
    thread = threading.Thread(target=_run)
    thread.start()
    return thread


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    نقطه ورود پیام‌های تلگرام (وب‌هوک)
    """
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"status": "no_message"}), 200

    msg = data['message']
    chat_id = msg['chat']['id']
    text = msg.get('text', '')
    from_user = msg['from']

    # دریافت شناسه کلینیک (در MVP فقط یک کلینیک داریم)
    clinic_id = get_or_create_default_clinic()

    # آماده‌سازی یک DummyUpdate برای انتقال به patient_agent
    class DummyMessage:
        def __init__(self, text, chat_id):
            self.text = text
            self.chat_id = chat_id
        def reply_text(self, reply_text):
            """ارسال پاسخ به تلگرام"""
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            try:
                requests.post(url, json={"chat_id": self.chat_id, "text": reply_text}, timeout=5)
            except Exception as e:
                logger.error(f"خطا در ارسال پاسخ: {e}")

    class DummyUpdate:
        def __init__(self, user_id, username, first_name, message_text, chat_id):
            self.effective_user = type('User', (), {
                'id': user_id,
                'username': username,
                'first_name': first_name,
                'full_name': first_name
            })()
            self.effective_message = DummyMessage(message_text, chat_id)
        def reply_text(self, text):
            self.effective_message.reply_text(text)

    user_id = from_user.get('id')
    username = from_user.get('username')
    first_name = from_user.get('first_name', '')
    dummy_update = DummyUpdate(user_id, username, first_name, text, chat_id)

    # ایجاد یک سشن دیتابیس برای ارسال به تابع پردازش
    db_session = SessionLocal()

    # اجرای patient_agent در ترد جداگانه (تا درخواست Flask بلاک نشود)
    def process():
        try:
            asyncio.run(process_patient_message(
                update=dummy_update,
                context=None,
                clinic_id=clinic_id,
                platform="telegram",
                external_user_id=str(user_id),
                raw_text=text,
                media_url=None,
                media_type=None,
                transcript=None,
                db=db_session
            ))
        except Exception as e:
            logger.error(f"خطا در process_patient_message: {e}")
            # ارسال پیام خطا به کاربر
            dummy_update.reply_text("خطایی رخ داده است. لطفاً دقایقی دیگر تلاش کنید.")
        finally:
            db_session.close()

    threading.Thread(target=process).start()

    return jsonify({"status": "ok"}), 200


@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """
    تنظیم وب‌هوک تلگرام (یک بار اجرا کنید)
    آدرس: https://your-app-name.up.railway.app/set_webhook
    """
    # اول سعی کن از متغیر محیطی Railway استفاده کنی
    railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
    if not railway_domain:
        # fallback: اگر متغیر محیطی تنظیم نشده، از آدرس ثابت خودت استفاده کن (بر اساس دامنه‌ای که Railway به تو داده)
        # مثال: railway_domain = "clinicos-production-d6a1.up.railway.app"
        railway_domain = "clinicos-production-d6a1.up.railway.app"   # <-- نام دامنه واقعی خود را اینجا وارد کن
        logger.warning(f"RAILWAY_PUBLIC_DOMAIN not set, using fallback: {railway_domain}")

    webhook_url = f"https://{railway_domain}/webhook"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
    try:
        resp = requests.get(url)
        return resp.text
    except Exception as e:
        return str(e), 500


@app.route('/health', methods=['GET'])
def health():
    """نقطه سلامت برای بررسی وضعیت سرویس"""
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

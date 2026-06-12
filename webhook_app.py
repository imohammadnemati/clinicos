import os
import asyncio
import threading
import logging
from flask import Flask, request, jsonify
import requests
from config import BOT_TOKEN
from database import SessionLocal, init_db
from models import Clinic
from patient_agent import process_patient_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
init_db()

def get_or_create_default_clinic():
    db = SessionLocal()
    try:
        clinic = db.query(Clinic).first()
        if not clinic:
            clinic = Clinic(name="کلینیک پیش‌فرض", subdomain="default")
            db.add(clinic)
            db.commit()
            logger.info("کلینیک پیش‌فرض ایجاد شد.")
        return clinic.id
    finally:
        db.close()

class DummyMessage:
    def __init__(self, text, chat_id):
        self.text = text
        self.chat_id = chat_id
    async def reply_text(self, reply_text):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        await asyncio.to_thread(requests.post, url, json={"chat_id": self.chat_id, "text": reply_text}, timeout=5)

class DummyUpdate:
    def __init__(self, user_id, username, first_name, message_text, chat_id):
        self.effective_user = type('User', (), {
            'id': user_id,
            'username': username,
            'first_name': first_name,
            'full_name': first_name
        })()
        self.message = DummyMessage(message_text, chat_id)
        self.effective_message = self.message

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"status": "no_message"}), 200
    msg = data['message']
    text = msg.get('text', '')
    from_user = msg['from']
    chat_id = msg['chat']['id']
    clinic_id = get_or_create_default_clinic()
    user_id = from_user.get('id')
    username = from_user.get('username')
    first_name = from_user.get('first_name', '')
    dummy_update = DummyUpdate(user_id, username, first_name, text, chat_id)
    db_session = SessionLocal()
    def process():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(process_patient_message(
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
            # fallback با requests معمولی
            try:
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": "خطایی رخ داده است. لطفاً دقایقی دیگر تلاش کنید."})
            except:
                pass
        finally:
            db_session.close()
    threading.Thread(target=process).start()
    return jsonify({"status": "ok"}), 200

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    railway_domain = "clinicos-production-9a22.up.railway.app"
    webhook_url = f"https://{railway_domain}/webhook"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
    try:
        resp = requests.get(url)
        return resp.text
    except Exception as e:
        return str(e), 500

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
from flask import Flask, request, jsonify
import requests
import os
import asyncio
import threading
from config import BOT_TOKEN
from patient_agent import process_patient_message
from telegram import Update, User, Chat, Message
from database import SessionLocal

app = Flask(__name__)

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and 'message' in data:
        msg = data['message']
        chat_id = msg['chat']['id']
        # ساخت یک DummyUpdate (فقط برای فراخوانی process_patient_message)
        class DummyUpdate:
            effective_user = type('obj', (), {
                'id': msg['from']['id'],
                'username': msg['from'].get('username'),
                'full_name': msg['from'].get('first_name', '')
            })()
            effective_message = type('obj', (), {
                'reply_text': lambda self, text: None,
                'text': msg.get('text')
            })()
            def reply_text(self, text):
                # ارسال پاسخ به تلگرام
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                requests.post(url, json={"chat_id": chat_id, "text": text})
            effective_message.reply_text = reply_text.__get__(effective_message)

        dummy_update = DummyUpdate()
        # فراخوانی تابع async در یک ترد جداگانه
        def task():
            asyncio.run(process_patient_message(
                update=dummy_update,
                context=None,
                clinic_id=1,  # باید clinic_id واقعی را پیدا کنی
                platform="telegram",
                external_user_id=str(msg['from']['id']),
                raw_text=msg.get('text', ''),
                media_url=None,
                media_type=None,
                transcript=None,
                db=SessionLocal()
            ))
        threading.Thread(target=task).start()
        return jsonify({"status": "ok"})
    return jsonify({"status": "no_message"})

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    railway_url = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
    if not railway_url:
        return "RAILWAY_PUBLIC_DOMAIN not set", 500
    webhook_url = f"{railway_url}/webhook"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
    return requests.get(url).text

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

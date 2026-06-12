# استفاده از نسخه پایتون 3.11 (سازگار با همه کتابخانه‌ها)
FROM python:3.11-slim

# تنظیم متغیرهای محیطی برای جلوگیری از بافر شدن خروجی و بهینه‌سازی pip
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# نصب وابستگی‌های سیستمی (برای whisper، librosa، faiss و ...)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    ffmpeg \
    libsndfile1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ایجاد دایرکتوری کاری
WORKDIR /app

# کپی فایل requirements.txt اول (برای استفاده از کش لایه‌ها)
COPY requirements.txt .

# نصب کتابخانه‌های پایتون (با فعال کردن build isolation برای whisper)
RUN pip install --no-cache-dir -r requirements.txt

# کپی بقیه فایل‌های پروژه
COPY . .

# در معرض گذاشتن پورت (Railway به صورت خودکار از PORT استفاده می‌کند)
EXPOSE $PORT

# اجرای برنامه (وب‌هوک Flask)
CMD ["python", "webhook_app.py"]

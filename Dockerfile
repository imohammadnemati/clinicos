FROM python:3.11-slim

WORKDIR /app

# نصب وابستگی‌های سیستمی مورد نیاز برای whisper و librosa
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "webhook_app.py"]

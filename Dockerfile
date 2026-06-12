FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    ffmpeg \
    libsndfile1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# نصب با --no-build-isolation برای جلوگیری از خطای pkg_resources
RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt

COPY . .

EXPOSE $PORT

CMD ["python", "webhook_app.py"]

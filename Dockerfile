# ============================================================
# Clinicos – Dockerfile for Railway Deployment
# ============================================================
# NOTE: Vosk models are NOT downloaded during build to avoid timeout.
# They will be downloaded automatically at runtime when first needed.
# ============================================================

FROM python:3.11-slim

# ============================================================
# Set working directory
# ============================================================
WORKDIR /app

# ============================================================
# Install system dependencies
# Required for: audio processing (ffmpeg, libsndfile),
#               building Python packages (gcc, g++),
#               downloading models (wget, unzip – optional, but kept for safety)
# ============================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    ffmpeg \
    libsndfile1 \
    wget \
    unzip \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# Copy requirements first for better caching
# ============================================================
COPY requirements.txt .

# ============================================================
# Install Python dependencies
# ============================================================
RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt

# ============================================================
# Copy the entire project
# ============================================================
COPY . .

# ============================================================
# NOTE: Vosk models are NOT downloaded here.
# The download_vosk_models.py script is kept for runtime use.
# Models will be downloaded lazily via vosk_stt.py -> ensure_model()
# ============================================================

# ============================================================
# Set environment variables (optional – can be overridden in Railway)
# ============================================================
ENV PYTHONUNBUFFERED=1
ENV STT_ENGINE=auto
ENV WHISPER_MODEL_SIZE=base

# ============================================================
# Expose port (Telegram webhook not used, but kept for compatibility)
# ============================================================
EXPOSE 8080

# ============================================================
# Command to run the bot
# ============================================================
CMD ["python", "bot.py"]

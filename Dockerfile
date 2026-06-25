# ============================================================
# Clinicos – Dockerfile for Railway Deployment
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
#               downloading models (wget, unzip)
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
# Download Vosk models (runs during build)
# ============================================================
RUN python download_vosk_models.py

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

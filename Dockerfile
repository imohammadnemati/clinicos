# ============================================================
# Clinicos – Dockerfile for Railway Deployment
# ONLY Local LLM (TinyLlama) – NO Voice, NO STT, NO Vosk, NO Whisper
# ============================================================

FROM python:3.11-slim

# ============================================================
# Set working directory
# ============================================================
WORKDIR /app

# ============================================================
# Install ONLY essential system dependencies
# Required for: llama-cpp-python (compilation) + model download
# ============================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
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
# Install Python dependencies (NO STT, NO Vosk, NO Whisper)
# ============================================================
RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt

# ============================================================
# Copy the entire project
# ============================================================
COPY . .

# ============================================================
# Set environment variables for Local LLM
# ============================================================
ENV PYTHONUNBUFFERED=1
ENV LOCAL_LLM_THREADS=4

# ============================================================
# Expose port (Telegram webhook not used, kept for compatibility)
# ============================================================
EXPOSE 8080

# ============================================================
# Command to run the bot
# ============================================================
CMD ["python", "bot.py"]

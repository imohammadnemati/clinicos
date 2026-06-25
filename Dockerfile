# ============================================================
# Clinicos – Dockerfile for Railway Deployment
# Local LLM only (TinyLlama) – no external APIs, no Voice/Photo
# ============================================================

FROM python:3.11-slim

# ============================================================
# Set working directory
# ============================================================
WORKDIR /app

# ============================================================
# Install system dependencies
# Required for: llama-cpp-python (compilation), audio (optional),
#               downloading models (wget, unzip)
# ============================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    ffmpeg \
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
# Set environment variables (can be overridden in Railway)
# ============================================================
ENV PYTHONUNBUFFERED=1
ENV LOCAL_LLM_THREADS=4
ENV LOCAL_LLM_MODEL_REPO="TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
ENV LOCAL_LLM_MODEL_FILE="tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

# ============================================================
# Expose port (Telegram webhook not used, kept for compatibility)
# ============================================================
EXPOSE 8080

# ============================================================
# Command to run the bot
# ============================================================
CMD ["python", "bot.py"]
"""
Speech-to-Text service for Clinicos.
Uses local Whisper model (open-source) – no API key, no cost, offline.
"""

import os
import logging
import asyncio
from typing import Optional

# Import whisper – will be installed via requirements.txt
import whisper

# Optional: set model size via environment variable (default: "base")
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")

logger = logging.getLogger(__name__)


class STTService:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the Whisper model (lazy loading, runs once)."""
        if self.model is None:
            try:
                logger.info(f"Loading Whisper model '{WHISPER_MODEL_SIZE}'... (this may take a moment)")
                self.model = whisper.load_model(WHISPER_MODEL_SIZE)
                logger.info("Whisper model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                self.model = None

    async def transcribe_audio_file(self, file_path: str) -> Optional[str]:
        """
        Transcribe audio file using local Whisper.
        Supports all common formats (ogg, mp3, m4a, wav, etc.).
        Returns transcribed text or None on failure.
        """
        if self.model is None:
            self._load_model()
            if self.model is None:
                logger.error("Whisper model not available. Check installation and memory.")
                return None

        try:
            # Whisper runs synchronously – run in thread to avoid blocking the event loop
            result = await asyncio.to_thread(
                self.model.transcribe,
                file_path,
                language="fa",         # force Persian; use "auto" for automatic detection
                task="transcribe",     # standard transcription (not translation)
                fp16=False,            # set to True if GPU available, False for CPU
                verbose=False,
                temperature=0.0,       # deterministic output
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0,
                no_speech_threshold=0.6,
                condition_on_previous_text=True,
                initial_prompt=None,
                word_timestamps=False,
                prepend_punctuations="\"'“¿([{-",
                append_punctuations="\"'.。，,！：:；?？、",
                clip_timestamps=None,
                hallucination_silence_threshold=None,
            )
            transcript = result.get("text", "").strip()
            if transcript:
                logger.info(f"Local Whisper STT succeeded: {len(transcript)} characters")
                return transcript
            else:
                logger.warning("Local Whisper STT returned empty transcript")
                return None
        except Exception as e:
            logger.error(f"Local Whisper STT error: {e}")
            return None
"""
Speech-to-Text service for Clinicos.
Uses local Whisper model (open-source) – no API key, no cost, offline.
Supports dynamic language selection based on user's preferred language.
"""

import os
import logging
import asyncio
from typing import Optional

import whisper
from config import WHISPER_MODEL_SIZE

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

    async def transcribe_audio_file(self, file_path: str, language: str = "fa") -> Optional[str]:
        """
        Transcribe audio file using local Whisper.
        Supports all common formats (ogg, mp3, m4a, wav, etc.).
        Returns transcribed text or None on failure.

        Args:
            file_path: Path to the audio file.
            language: User's preferred language code ('fa', 'en', 'az', 'ar', etc.).
                      Maps to Whisper language codes.
        """
        if self.model is None:
            self._load_model()
            if self.model is None:
                logger.error("Whisper model not available. Check installation and memory.")
                return None

        # Map language codes to Whisper language codes
        # Whisper supports many languages, we map our supported ones
        lang_map = {
            "fa": "fa",      # Persian
            "en": "en",      # English
            "ar": "ar",      # Arabic
            "az": "az",      # Azerbaijani
            "tr": "tr",      # Turkish (fallback for Azerbaijani if needed)
        }
        whisper_lang = lang_map.get(language, "fa")  # default to Persian

        try:
            # Whisper runs synchronously – run in thread to avoid blocking the event loop
            result = await asyncio.to_thread(
                self.model.transcribe,
                file_path,
                language=whisper_lang,
                task="transcribe",
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
            )
            transcript = result.get("text", "").strip()
            if transcript:
                logger.info(f"STT ({whisper_lang}) succeeded: {len(transcript)} characters")
                return transcript
            else:
                logger.warning("STT returned empty transcript")
                return None
        except Exception as e:
            logger.error(f"STT error: {e}")
            return None
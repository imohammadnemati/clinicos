"""
Unified Speech-to-Text service combining Vosk and Whisper.
Automatically selects the best engine based on language and fallback logic.

Environment variables:
    STT_ENGINE: 'auto' (default), 'vosk', 'whisper', or 'hybrid'
        - auto: choose based on language (Vosk for fa/en/ar/tr, Whisper otherwise)
        - vosk: always use Vosk (falls back to Whisper if Vosk fails)
        - whisper: always use Whisper (falls back to Vosk if Whisper fails)
        - hybrid: try Vosk first, then Whisper (with quality check)
"""

import os
import logging
from typing import Optional

from vosk_stt import VoskSTTService
from stt_service import STTService as WhisperSTTService

logger = logging.getLogger(__name__)


class UnifiedSTTService:
    def __init__(self, primary_engine: str = "auto"):
        """
        Args:
            primary_engine: One of 'auto', 'vosk', 'whisper', 'hybrid'.
        """
        self.primary_engine = os.getenv("STT_ENGINE", primary_engine).lower()
        self.vosk = VoskSTTService()
        self.whisper = WhisperSTTService()
        logger.info(f"Unified STT service initialized with engine: {self.primary_engine}")

    async def transcribe_audio_file(self, file_path: str, language: str = "fa") -> Optional[str]:
        """
        Transcribe audio using the best engine based on configuration.
        The audio file should be in WAV format (mono 16kHz 16-bit PCM) for Vosk,
        but Whisper can handle various formats (OGG, MP3, etc.).
        The caller is responsible for providing a compatible file.
        """
        # Determine which engine to use first
        engine_mode = self._get_engine_mode(language)

        transcript = None

        if engine_mode == "vosk":
            transcript = await self._try_vosk(file_path, language)
            if transcript:
                return transcript
            logger.info(f"Vosk failed for {language}, falling back to Whisper")
            return await self._try_whisper(file_path, language)

        elif engine_mode == "whisper":
            transcript = await self._try_whisper(file_path, language)
            if transcript:
                return transcript
            logger.info(f"Whisper failed for {language}, falling back to Vosk")
            return await self._try_vosk(file_path, language)

        elif engine_mode == "hybrid":
            # Try Vosk first, check quality, then Whisper if needed
            transcript = await self._try_vosk(file_path, language)
            if transcript and self._is_quality_good(transcript):
                logger.info(f"Vosk provided good quality ({len(transcript)} chars)")
                return transcript
            if transcript:
                logger.info(f"Vosk transcript too short ({len(transcript)}), trying Whisper")
            else:
                logger.info("Vosk returned empty, trying Whisper")
            return await self._try_whisper(file_path, language)

        else:
            # Fallback: try Whisper first
            return await self._try_whisper(file_path, language)

    def _get_engine_mode(self, language: str) -> str:
        """Determine which engine to use based on configuration and language."""
        # Languages with good Vosk models (fast and accurate enough)
        vosk_supported = {"fa", "en", "ar", "tr", "az"}

        if self.primary_engine == "vosk":
            return "vosk"
        elif self.primary_engine == "whisper":
            return "whisper"
        elif self.primary_engine == "hybrid":
            return "hybrid"
        else:  # auto
            if language in vosk_supported:
                return "vosk"
            else:
                return "whisper"

    def _is_quality_good(self, transcript: str) -> bool:
        """Heuristic: if transcript has at least 10 characters, consider it good."""
        return len(transcript.strip()) >= 10

    async def _try_vosk(self, file_path: str, language: str) -> Optional[str]:
        try:
            return await self.vosk.transcribe_audio_file(file_path, language)
        except Exception as e:
            logger.error(f"Vosk error: {e}")
            return None

    async def _try_whisper(self, file_path: str, language: str) -> Optional[str]:
        try:
            # Whisper can handle WAV, but we need to pass the correct language
            return await self.whisper.transcribe_audio_file(file_path, language)
        except Exception as e:
            logger.error(f"Whisper error: {e}")
            return None
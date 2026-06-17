"""
Speech-to-Text service for Clinicos.
Supports OpenAI Whisper and Google Cloud Speech-to-Text.
"""

import os
import logging
import asyncio
from typing import Optional

from openai import OpenAI
from config import (
    OPENAI_API_KEY,
    STT_MODEL,
    STT_PROVIDER,
    GOOGLE_STT_LANGUAGE_CODE
)

logger = logging.getLogger(__name__)


class STTService:
    def __init__(self, provider: str = None):
        self.provider = provider or STT_PROVIDER
        self.api_key = OPENAI_API_KEY
        self._sync_client = None

        if self.provider == "openai":
            if not self.api_key:
                logger.warning("OPENAI_API_KEY is not set. OpenAI STT will not work.")
            else:
                self._sync_client = OpenAI(api_key=self.api_key)

        elif self.provider == "google":
            # Google uses GOOGLE_APPLICATION_CREDENTIALS environment variable
            try:
                from google.cloud import speech_v1
                self._google_client = speech_v1.SpeechClient()
                logger.info("Google Cloud Speech-to-Text client initialized.")
            except ImportError:
                logger.error("google-cloud-speech not installed. Please install it.")
                self._google_client = None
            except Exception as e:
                logger.error(f"Failed to initialize Google Speech client: {e}")
                self._google_client = None
        else:
            raise ValueError(f"Unsupported STT provider: {self.provider}")

    async def transcribe_audio_file(self, file_path: str) -> Optional[str]:
        """
        Transcribe an audio file to text using the configured provider.
        Supports ogg, mp3, m4a, wav, etc. (any format supported by the provider).
        Returns None on failure.
        """
        if self.provider == "openai":
            return await self._transcribe_openai(file_path)
        elif self.provider == "google":
            return await self._transcribe_google(file_path)
        else:
            raise ValueError(f"Unsupported STT provider: {self.provider}")

    async def _transcribe_openai(self, file_path: str) -> Optional[str]:
        if not self._sync_client:
            logger.error("OpenAI client not initialized for STT")
            return None
        try:
            with open(file_path, "rb") as audio_file:
                response = await asyncio.to_thread(
                    self._sync_client.audio.transcriptions.create,
                    model=STT_MODEL,
                    file=audio_file,
                    response_format="text"
                )
            transcript = response.strip() if isinstance(response, str) else response.text.strip()
            if transcript:
                logger.info(f"OpenAI STT succeeded: {len(transcript)} characters")
                return transcript
            else:
                logger.warning("OpenAI STT returned empty transcript")
                return None
        except Exception as e:
            logger.error(f"OpenAI STT error: {e}")
            return None

    async def _transcribe_google(self, file_path: str) -> Optional[str]:
        if not hasattr(self, '_google_client') or self._google_client is None:
            logger.error("Google Speech client not initialized. Check credentials and installation.")
            return None

        try:
            # Read audio file
            with open(file_path, "rb") as audio_file:
                content = audio_file.read()

            # Detect encoding from file extension (simplified)
            # For Telegram voice messages, typically OGG_OPUS
            # We'll default to OGG_OPUS; can be extended.
            from google.cloud.speech_v1 import RecognitionAudio, RecognitionConfig
            from google.cloud.speech_v1 import enums

            audio = RecognitionAudio(content=content)
            config = RecognitionConfig(
                encoding=RecognitionConfig.AudioEncoding.OGG_OPUS,
                language_code=GOOGLE_STT_LANGUAGE_CODE,
                sample_rate_hertz=48000,  # Typical for Telegram voice
            )

            # Use asyncio.to_thread for blocking call
            response = await asyncio.to_thread(
                self._google_client.recognize,
                config=config,
                audio=audio
            )

            if response.results and len(response.results) > 0:
                transcript = response.results[0].alternatives[0].transcript
                if transcript:
                    logger.info(f"Google STT succeeded: {len(transcript)} characters")
                    return transcript
                else:
                    logger.warning("Google STT returned empty transcript")
                    return None
            else:
                logger.warning("Google STT returned no results")
                return None

        except Exception as e:
            logger.error(f"Google STT error: {e}")
            return None

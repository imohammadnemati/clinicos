"""
Speech-to-Text service using Vosk offline models.
Supports: fa (small-fa-0.5), en (small-en-us-0.15), ar (ar-mgb2-0.4), tr (small-tr-0.3).
Models are downloaded automatically during build via download_vosk_models.py.
Audio must be mono 16kHz 16-bit PCM WAV format.
"""

import os
import json
import wave
import logging
from typing import Optional

from vosk import Model, KaldiRecognizer

logger = logging.getLogger(__name__)

# Model paths – these are the directories extracted from zip files
MODEL_PATHS = {
    "fa": "models/vosk/vosk-model-small-fa-0.5",        # Primary Persian model
    "fa_alt": "models/vosk/vosk-model-small-fa-0.42",   # Alternative Persian model
    "en": "models/vosk/vosk-model-small-en-us-0.15",    # English small
    "en_large": "models/vosk/vosk-model-en-us-0.22-lgraph",  # Larger English model (optional)
    "ar": "models/vosk/vosk-model-ar-mgb2-0.4",         # Arabic model
    "tr": "models/vosk/vosk-model-small-tr-0.3",        # Turkish model
}


class VoskSTTService:
    def __init__(self):
        self.models = {}
        self._load_all_models()
        self._log_model_status()

    def _load_all_models(self):
        """Load all available Vosk models."""
        for lang_key, path in MODEL_PATHS.items():
            if os.path.exists(path):
                try:
                    self.models[lang_key] = Model(path)
                    logger.info(f"Vosk model loaded for '{lang_key}' from {path}")
                except Exception as e:
                    logger.error(f"Failed to load Vosk model for '{lang_key}': {e}")
            else:
                logger.warning(f"Vosk model for '{lang_key}' not found at {path}")

    def _log_model_status(self):
        """Log which models are available."""
        loaded = [k for k, v in self.models.items() if v is not None]
        if loaded:
            logger.info(f"Vosk models loaded: {', '.join(loaded)}")
        else:
            logger.warning("No Vosk models loaded. STT will fail.")

    def _get_model(self, language: str) -> Optional[Model]:
        """
        Get the appropriate Vosk model for the given language.
        Falls back to alternative models if primary is not available.
        """
        lang_map = {
            "fa": "fa",
            "en": "en",
            "ar": "ar",
            "tr": "tr",
        }
        model_key = lang_map.get(language)
        if not model_key:
            logger.error(f"Unsupported language for Vosk: {language}")
            return None

        # Try primary model
        model = self.models.get(model_key)
        if model:
            return model

        # Fallback for Persian
        if language == "fa" and "fa_alt" in self.models:
            logger.info("Using fallback Persian model (fa_alt)")
            return self.models["fa_alt"]

        # Fallback for English
        if language == "en" and "en_large" in self.models:
            logger.info("Using fallback English model (en_large)")
            return self.models["en_large"]

        logger.error(f"No Vosk model available for language: {language}")
        return None

    async def transcribe_audio_file(self, file_path: str, language: str = "fa") -> Optional[str]:
        """
        Transcribe audio file using Vosk.
        Expects mono 16kHz 16-bit PCM WAV file.
        If file is not WAV, caller must convert it first (e.g., using pydub).
        """
        model = self._get_model(language)
        if not model:
            logger.error(f"No Vosk model for language {language}")
            return None

        try:
            wf = wave.open(file_path, "rb")
        except Exception as e:
            logger.error(f"Failed to open audio file: {e}")
            return None

        # Validate audio format
        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        framerate = wf.getframerate()

        if channels != 1:
            logger.error(f"Audio must be mono (1 channel), got {channels}")
            wf.close()
            return None

        if sample_width != 2:
            logger.error(f"Audio must be 16-bit PCM (sample width 2), got {sample_width}")
            wf.close()
            return None

        if framerate != 16000:
            logger.error(f"Audio must be 16kHz, got {framerate}")
            wf.close()
            return None

        try:
            rec = KaldiRecognizer(model, framerate)
            rec.SetWords(False)

            final_text = ""
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    if "text" in res:
                        final_text += " " + res["text"]

            # Get partial/final result
            partial = json.loads(rec.FinalResult())
            if "text" in partial:
                final_text += " " + partial["text"]

            wf.close()

            transcript = final_text.strip()
            if transcript:
                logger.info(f"Vosk STT ({language}) succeeded: {len(transcript)} chars")
                return transcript
            else:
                logger.warning(f"Vosk STT ({language}) returned empty transcript")
                return None

        except Exception as e:
            logger.error(f"Vosk STT error: {e}")
            if not wf.closed:
                wf.close()
            return None

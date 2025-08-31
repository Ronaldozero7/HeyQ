from __future__ import annotations
import queue
import threading
import time
from dataclasses import dataclass
from typing import Optional, Any, TYPE_CHECKING

# SpeechRecognition imports 'aifc' which was removed in Python 3.13.
# Make it optional so the rest of the project can run without voice on 3.13.
try:  # pragma: no cover - environment dependent
    import speech_recognition as sr  # type: ignore
except Exception:  # If unavailable, degrade gracefully
    sr = None  # type: ignore

try:
    import whisper  # type: ignore
    HAVE_WHISPER = True
except Exception:  # pragma: no cover
    whisper = None
    HAVE_WHISPER = False

from loguru import logger
from ..config import CONFIG


@dataclass
class VoiceConfig:
    wake_word: str = CONFIG.wake_word
    stt_engine: str = CONFIG.stt_engine  # whisper|google


class VoiceInterface:
    """Continuously listens for wake word then streams commands."""

    def __init__(self, cfg: VoiceConfig | None = None):
        self.cfg = cfg or VoiceConfig()
        self.recognizer = sr.Recognizer() if sr else None
        # Lazily initialize Microphone to avoid requiring PyAudio at import/install time
        self.mic: Optional[Any] = None
        self.stop_event = threading.Event()
        self.command_queue: "queue.Queue[str]" = queue.Queue()
        self._whisper_model = whisper.load_model("base") if (self.cfg.stt_engine == "whisper" and HAVE_WHISPER) else None

    def start(self):
        if sr is None:
            logger.error("SpeechRecognition not available on this Python version; voice mode disabled.")
            raise RuntimeError("Voice is unavailable: SpeechRecognition import failed (likely Python 3.13 'aifc' removal). Use plan runner or lower Python.")
        # Initialize microphone only when starting the voice loop
        if self.mic is None:
            try:
                self.mic = sr.Microphone()
            except Exception as e:
                logger.error("Microphone initialization failed: {}", e)
                raise
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.stop_event.set()

    def get_command(self, timeout: Optional[float] = None) -> Optional[str]:
        try:
            return self.command_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def _transcribe(self, audio: Any) -> str | None:
        try:
            if self.cfg.stt_engine == "google" and self.recognizer is not None:
                return self.recognizer.recognize_google(audio)
            if self._whisper_model is not None:
                import tempfile
                wav_bytes = audio.get_wav_data()
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tf:
                    tf.write(wav_bytes)
                    tf.flush()
                    result = self._whisper_model.transcribe(tf.name, fp16=False, language='en')
                    return result.get("text")
            else:
                # Fallback to Sphinx offline if available
                try:
                    if self.recognizer is not None:
                        return self.recognizer.recognize_sphinx(audio)
                except Exception:
                    pass
                return None
        except Exception as e:
            logger.warning("STT error: {}", e)
            return None

    def _loop(self):
    if self.mic is None or self.recognizer is None:
            logger.error("Microphone not initialized. Call start() first.")
            return
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            logger.info("Voice loop started. Say '{}' to wake.", self.cfg.wake_word)
            while not self.stop_event.is_set():
                try:
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=8)
                except sr.WaitTimeoutError:
                    continue
                text = self._transcribe(audio)
                if not text:
                    continue
                t = text.lower().strip()
                logger.debug("Heard: {}", t)
                if self.cfg.wake_word in t:
                    logger.info("Wake word detected. Listening for command…")
                    try:
                        audio_cmd = self.recognizer.listen(source, timeout=6, phrase_time_limit=12)
                        cmd_text = self._transcribe(audio_cmd)
                        if cmd_text:
                            logger.info("Command: {}", cmd_text)
                            self.command_queue.put(cmd_text)
                    except sr.WaitTimeoutError:
                        logger.warning("No command detected after wake word.")
                time.sleep(0.1)

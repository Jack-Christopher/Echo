"""Microphone capture to WAV while PTT is held (live stream)."""

from __future__ import annotations

import logging
import tempfile
import threading
import wave
from pathlib import Path

import numpy as np

from echo.speech.audio_preprocess import preprocess

logger = logging.getLogger(__name__)

SAMPLE_RATE = 16000
CHANNELS = 1
MIN_SECONDS = 0.3
MAX_SECONDS = 30.0


class AudioCapture:
    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
    ) -> None:
        self._sample_rate = sample_rate
        self._channels = channels
        self._frames: list[np.ndarray] = []
        self._recording = False
        self._stream = None
        self._lock = threading.Lock()

    @property
    def is_recording(self) -> bool:
        return self._recording

    def _callback(self, indata, _frames_count, _time, status) -> None:
        if status:
            logger.warning("Audio stream: %s", status)
        if self._recording:
            self._frames.append(indata.copy())

    def start(self) -> bool:
        """Start live microphone capture. Returns False if mic unavailable."""
        with self._lock:
            if self._recording:
                return True
            try:
                import sounddevice as sd
            except ImportError:
                logger.error("sounddevice not installed")
                return False

            self._frames = []
            self._recording = True
            try:
                self._stream = sd.InputStream(
                    samplerate=self._sample_rate,
                    channels=self._channels,
                    dtype="float32",
                    callback=self._callback,
                )
                self._stream.start()
                logger.info("Microphone recording started")
                return True
            except Exception as e:
                self._recording = False
                self._stream = None
                logger.exception("Failed to start microphone: %s", e)
                return False

    def stop_and_save(self) -> Path | None:
        with self._lock:
            self._recording = False
            if self._stream is not None:
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception as e:
                    logger.debug("Stream close: %s", e)
                self._stream = None

            if not self._frames:
                logger.warning("No audio frames captured")
                return None

            audio = np.concatenate(self._frames, axis=0).flatten()
            duration = len(audio) / self._sample_rate
            logger.info("Captured %.2f s of audio (%d samples)", duration, len(audio))

            if duration < MIN_SECONDS:
                logger.warning("Audio too short (min %.1f s)", MIN_SECONDS)
                return None
            if duration > MAX_SECONDS:
                audio = audio[: int(MAX_SECONDS * self._sample_rate)]

            audio = preprocess(audio, self._sample_rate)
            duration = len(audio) / self._sample_rate
            if duration < MIN_SECONDS:
                logger.warning("Audio too short after preprocess (min %.1f s)", MIN_SECONDS)
                return None

            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            path = Path(tmp.name)
            tmp.close()

            with wave.open(str(path), "wb") as wf:
                wf.setnchannels(self._channels)
                wf.setsampwidth(2)
                wf.setframerate(self._sample_rate)
                samples = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
                wf.writeframes(samples.tobytes())

            logger.info("Saved WAV: %s", path)
            return path

    def add_chunk(self, chunk: np.ndarray) -> None:
        if self._recording:
            self._frames.append(chunk)

    def record_blocking(self, duration: float) -> Path | None:
        """Record for a fixed duration (tests / fallback)."""
        try:
            import sounddevice as sd

            self._frames = []
            self._recording = True
            samples = int(duration * self._sample_rate)
            data = sd.rec(
                samples,
                samplerate=self._sample_rate,
                channels=self._channels,
                dtype="float32",
            )
            sd.wait()
            self._recording = False
            self._frames = [data.flatten()]
            return self.stop_and_save()
        except Exception as e:
            logger.exception("record_blocking failed: %s", e)
            self._recording = False
            return None

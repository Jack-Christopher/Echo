"""Short soft feedback tone (unknown command, etc.)."""

from __future__ import annotations

import logging
import math
import struct
import tempfile
import wave
from pathlib import Path

logger = logging.getLogger(__name__)

_DURATION_MS = 500
_FREQUENCY_HZ = 740
_SAMPLE_RATE = 22050
_VOLUME = 0.12


def play_soft_beep(duration_ms: int = _DURATION_MS) -> None:
    """Play a brief low-volume beep (~0.5 s)."""
    try:
        path = _write_beep_wav(duration_ms)
        try:
            import winsound

            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception:
            _play_with_sounddevice(path)
    except Exception as e:
        logger.debug("beep failed: %s", e)


def _write_beep_wav(duration_ms: int) -> Path:
    n = int(_SAMPLE_RATE * duration_ms / 1000)
    fade = int(_SAMPLE_RATE * 0.04)
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    path = Path(tmp.name)
    tmp.close()
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(_SAMPLE_RATE)
        frames = bytearray()
        for i in range(n):
            env = 1.0
            if i < fade:
                env = i / fade
            elif i > n - fade:
                env = max(0.0, (n - i) / fade)
            t = i / _SAMPLE_RATE
            sample = int(
                32767 * _VOLUME * env * math.sin(2 * math.pi * _FREQUENCY_HZ * t)
            )
            frames.extend(struct.pack("<h", sample))
        wf.writeframes(frames)
    return path


def _play_with_sounddevice(path: Path) -> None:
    import sounddevice as sd
    import numpy as np

    with wave.open(str(path), "rb") as wf:
        data = wf.readframes(wf.getnframes())
        audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767
        sd.play(audio, wf.getframerate())
        sd.wait()

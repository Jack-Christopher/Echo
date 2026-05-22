"""Lightweight speech preprocessing before Whisper."""

from __future__ import annotations

import numpy as np

# 20 ms frames at 16 kHz
_FRAME_SAMPLES = 320
_TRIM_THRESHOLD = 0.012
_TARGET_PEAK = 0.92


def trim_silence(
    audio: np.ndarray,
    sample_rate: int,
    *,
    threshold: float = _TRIM_THRESHOLD,
    pad_ms: float = 120.0,
) -> np.ndarray:
    """Remove leading/trailing silence; keep a short pad around speech."""
    if audio.size == 0:
        return audio
    frame = max(1, int(sample_rate * 0.02))
    pad = int(sample_rate * pad_ms / 1000.0)
    energies = []
    for i in range(0, len(audio), frame):
        chunk = audio[i : i + frame]
        energies.append(float(np.sqrt(np.mean(chunk * chunk))))
    if not energies:
        return audio
    peak_e = max(energies) or 1.0
    rel = [e / peak_e for e in energies]
    voiced = [i for i, v in enumerate(rel) if v >= threshold]
    if not voiced:
        return audio
    start = max(0, voiced[0] * frame - pad)
    end = min(len(audio), (voiced[-1] + 1) * frame + pad)
    return audio[start:end]


def normalize_peak(audio: np.ndarray, target: float = _TARGET_PEAK) -> np.ndarray:
    peak = float(np.max(np.abs(audio)))
    if peak < 1e-6:
        return audio
    return np.clip(audio * (target / peak), -1.0, 1.0)


def preprocess(audio: np.ndarray, sample_rate: int) -> np.ndarray:
    """DC removal, trim silence, peak normalize for clearer STT."""
    if audio.size == 0:
        return audio
    out = audio.astype(np.float32, copy=True)
    out = out - float(np.mean(out))
    out = trim_silence(out, sample_rate)
    return normalize_peak(out)

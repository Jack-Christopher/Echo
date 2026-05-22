import numpy as np
import pytest

from echo.speech.audio_preprocess import normalize_peak, preprocess, trim_silence


@pytest.mark.unit
def test_normalize_peak():
    audio = np.array([0.1, -0.1, 0.2], dtype=np.float32)
    out = normalize_peak(audio, target=0.9)
    assert float(np.max(np.abs(out))) == pytest.approx(0.9, rel=0.01)


@pytest.mark.unit
def test_trim_silence_keeps_speech():
    sr = 16000
    silence = np.zeros(sr, dtype=np.float32)
    speech = np.full(sr // 2, 0.5, dtype=np.float32)
    audio = np.concatenate([silence, speech, silence])
    out = trim_silence(audio, sr, threshold=0.05)
    assert len(out) < len(audio)
    assert len(out) >= len(speech) // 2


@pytest.mark.unit
def test_preprocess_not_empty():
    sr = 16000
    audio = np.random.randn(sr).astype(np.float32) * 0.3
    out = preprocess(audio, sr)
    assert out.size > 0
    assert float(np.max(np.abs(out))) <= 1.0

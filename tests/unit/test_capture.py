from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from echo.speech.capture import MIN_SECONDS, AudioCapture, SAMPLE_RATE


@pytest.mark.unit
def test_stop_too_short():
    cap = AudioCapture()
    cap.start()
    cap._recording = True
    cap._frames = [np.zeros(int(SAMPLE_RATE * 0.1), dtype=np.float32)]
    cap._recording = False
    assert cap.stop_and_save() is None


@pytest.mark.unit
@patch("sounddevice.InputStream")
def test_start_stream(mock_stream_cls):
    stream = MagicMock()
    mock_stream_cls.return_value = stream
    cap = AudioCapture()
    assert cap.start() is True
    stream.start.assert_called_once()
    cap._frames = [np.zeros(int(SAMPLE_RATE * MIN_SECONDS) + 100, dtype=np.float32)]
    path = cap.stop_and_save()
    assert path is not None
    path.unlink(missing_ok=True)


@pytest.mark.unit
def test_stop_saves_wav_with_frames():
    cap = AudioCapture()
    cap._recording = True
    cap._frames = [np.zeros(int(SAMPLE_RATE * MIN_SECONDS) + 100, dtype=np.float32)]
    path = cap.stop_and_save()
    assert path is not None
    assert path.is_file()
    path.unlink(missing_ok=True)

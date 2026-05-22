from unittest.mock import MagicMock, patch

import pytest

from echo.speech import audio_devices


@pytest.mark.unit
def test_log_audio_devices(capsys):
    mock_sd = MagicMock()
    mock_sd.default.device = [0, 1]
    mock_sd.query_devices.return_value = [
        {"name": "Mic Test", "max_input_channels": 1, "max_output_channels": 0},
        {"name": "Speakers Test", "max_input_channels": 0, "max_output_channels": 2},
    ]
    with patch.dict("sys.modules", {"sounddevice": mock_sd}):
        audio_devices.log_audio_devices()
    out = capsys.readouterr().out
    assert "Mic Test" in out
    assert "Speakers Test" in out

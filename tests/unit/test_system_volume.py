from unittest.mock import MagicMock, patch

import pytest

from echo.system import volume


@pytest.mark.unit
@patch("echo.system.volume._get_interface")
def test_adjust_up(mock_get):
    vol = MagicMock()
    vol.GetMasterVolumeLevelScalar.return_value = 0.5
    mock_get.return_value = vol
    assert volume.adjust("up") is True


@pytest.mark.unit
@patch("echo.system.volume._get_interface", return_value=None)
@patch("echo.system.volume._fallback_keys", return_value=True)
def test_fallback(mock_fb, mock_get):
    assert volume.adjust("down") is True

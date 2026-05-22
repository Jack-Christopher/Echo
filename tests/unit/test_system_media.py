from unittest.mock import patch

import pytest

from echo.system import media


@pytest.mark.unit
@patch("echo.system.media.pyautogui.press")
def test_send_media_key(mock_press):
    assert media.send_media_key("pause") is True
    mock_press.assert_called_with("playpause")

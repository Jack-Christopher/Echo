from unittest.mock import patch

import pytest

from echo.system import brightness


@pytest.mark.unit
@patch("screen_brightness_control.get_brightness", return_value=50)
@patch("screen_brightness_control.set_brightness")
def test_adjust(mock_set, mock_get):
    assert brightness.adjust("up") is True
    mock_set.assert_called_once()


@pytest.mark.unit
@patch("screen_brightness_control.set_brightness", side_effect=OSError("no ddc"))
def test_adjust_noop(mock_set):
    assert brightness.adjust("up") is False

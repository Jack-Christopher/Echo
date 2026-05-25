from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from echo.browser import brave
from echo.config.schema import EchoConfig


@pytest.mark.unit
@patch("psutil.process_iter")
def test_is_running_true(mock_iter):
    proc = MagicMock()
    proc.info = {"name": "brave.exe"}
    mock_iter.return_value = [proc]
    assert brave.is_running() is True


@pytest.mark.unit
@patch("psutil.process_iter")
def test_is_running_false(mock_iter):
    mock_iter.return_value = []
    assert brave.is_running() is False


@pytest.mark.unit
@patch("echo.browser.control.write_browser_launch_log")
@patch("echo.browser.control.focus", return_value=True)
@patch("echo.browser.control.subprocess.Popen")
@patch("echo.browser.control.find_browser_path")
def test_launch(mock_find, mock_popen, mock_focus, mock_log, tmp_path):
    exe = tmp_path / "brave.exe"
    exe.write_text("")
    mock_find.return_value = exe
    proc = MagicMock()
    proc.pid = 1234
    proc.poll.return_value = None
    mock_popen.return_value = proc
    config = EchoConfig(browser="brave", browser_path=str(exe))
    assert brave.launch("https://youtube.com", config) is True
    mock_popen.assert_called_once()
    mock_log.assert_called_once()

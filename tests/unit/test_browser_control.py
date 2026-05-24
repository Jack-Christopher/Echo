from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest

from echo.browser import control
from echo.browser.control import (
    BROWSER_IDS,
    find_browser_path,
    get_spec,
    launch,
    normalize_browser_id,
)
from echo.config.schema import EchoConfig


@pytest.mark.unit
def test_normalize_browser_id():
    assert normalize_browser_id("chrome") == "chrome"
    assert normalize_browser_id("invalid") == "brave"


@pytest.mark.unit
def test_browser_ids_include_common_browsers():
    assert "brave" in BROWSER_IDS
    assert "opera" in BROWSER_IDS
    assert "firefox" in BROWSER_IDS


@pytest.mark.unit
def test_find_browser_path_custom(tmp_path):
    exe = tmp_path / "chrome.exe"
    exe.write_text("")
    config = EchoConfig(browser="chrome", browser_path=str(exe))
    assert find_browser_path(config) == exe


@pytest.mark.unit
@patch("echo.browser.control.subprocess.Popen")
@patch("echo.browser.control.focus", return_value=True)
def test_launch_chrome_new_tab(mock_focus, mock_popen, tmp_path):
    exe = tmp_path / "chrome.exe"
    exe.write_text("")
    config = EchoConfig(browser="chrome", browser_path=str(exe))
    spec = get_spec(config)
    assert launch("https://example.com", config) is True
    args = mock_popen.call_args[0][0]
    assert args[0] == str(exe)
    assert args[1] == spec.new_tab_flag
    assert args[2] == "https://example.com"
    kwargs = mock_popen.call_args[1]
    assert "creationflags" not in kwargs
    assert "startupinfo" not in kwargs
    mock_focus.assert_called_once()


@pytest.mark.unit
@patch("echo.browser.control.subprocess.Popen", side_effect=OSError("denied"))
def test_launch_returns_false_on_os_error(mock_popen, tmp_path):
    exe = tmp_path / "brave.exe"
    exe.write_text("")
    config = EchoConfig(browser="brave", browser_path=str(exe))
    assert launch("https://example.com", config) is False


@pytest.mark.unit
def test_find_browser_path_falls_back_when_custom_missing(tmp_path):
    good = tmp_path / "brave.exe"
    good.write_text("")
    spec = replace(control.BROWSER_SPECS["brave"], default_paths=(good,))
    config = EchoConfig(
        browser="brave",
        browser_path=str(tmp_path / "missing.exe"),
    )
    with patch.dict(control.BROWSER_SPECS, {"brave": spec}):
        assert find_browser_path(config) == good

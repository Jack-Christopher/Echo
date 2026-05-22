from pathlib import Path
from unittest.mock import patch

import pytest

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
def test_launch_chrome_new_tab(mock_popen, tmp_path):
    exe = tmp_path / "chrome.exe"
    exe.write_text("")
    config = EchoConfig(browser="chrome", browser_path=str(exe))
    spec = get_spec(config)
    assert launch("https://example.com", config) is True
    args = mock_popen.call_args[0][0]
    assert args[0] == str(exe)
    assert args[1] == spec.new_tab_flag
    assert args[2] == "https://example.com"

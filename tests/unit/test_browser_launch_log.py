from unittest.mock import MagicMock

import pytest

from echo.browser.launch_log import browser_log_path, write_browser_launch_log


@pytest.mark.unit
def test_write_browser_launch_log_with_error(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "echo.browser.launch_log.appdata_dir",
        lambda: tmp_path,
    )
    path = write_browser_launch_log(["brave.exe", "--new-tab", "https://x.com"], error="not found")
    assert path == browser_log_path()
    content = path.read_text(encoding="utf-8")
    assert "command:" in content
    assert "not found" in content


@pytest.mark.unit
def test_write_browser_launch_log_running_process(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "echo.browser.launch_log.appdata_dir",
        lambda: tmp_path,
    )
    proc = MagicMock()
    proc.pid = 4242
    proc.poll.return_value = None
    path = write_browser_launch_log(["opera.exe", "--new-tab", "https://x.com"], proc, focus_ok=True)
    content = path.read_text(encoding="utf-8")
    assert "pid: 4242" in content
    assert "running" in content
    assert "focus: ok" in content

from pathlib import Path

import pytest


@pytest.mark.unit
def test_no_window_kwargs_on_windows():
    from echo.system import subprocess_win

    kwargs = subprocess_win.no_window_kwargs()
    if __import__("sys").platform == "win32":
        assert "creationflags" in kwargs
        assert "startupinfo" in kwargs
    else:
        assert kwargs == {}


@pytest.mark.unit
def test_run_echo_logon_vbs_exists():
    root = Path(__file__).resolve().parents[2]
    vbs = root / "run_echo_logon.vbs"
    assert vbs.is_file()
    content = vbs.read_text(encoding="utf-8")
    assert "pythonw.exe" in content
    assert "startup-last.log" in content
    assert "WScript.Sleep" in content

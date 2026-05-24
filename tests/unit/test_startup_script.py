from pathlib import Path

import pytest


@pytest.mark.unit
def test_install_startup_script_exists():
    root = Path(__file__).resolve().parents[2]
    script = root / "install_startup.ps1"
    assert script.is_file()
    content = script.read_text(encoding="utf-8")
    assert "Register-ScheduledTask" in content
    assert "Echo" in content
    assert "run_echo_logon.vbs" in content
    assert "LogonType Interactive" in content
    assert "wscript.exe" in content


@pytest.mark.unit
def test_run_echo_bat_exists():
    root = Path(__file__).resolve().parents[2]
    bat = root / "run_echo.bat"
    assert bat.is_file()
    assert "echo.main" in bat.read_text(encoding="utf-8")


@pytest.mark.unit
def test_run_echo_logon_bat_exists():
    root = Path(__file__).resolve().parents[2]
    bat = root / "run_echo_logon.bat"
    assert bat.is_file()
    content = bat.read_text(encoding="utf-8")
    assert "echo.main" in content
    assert ".venv\\Scripts\\pythonw.exe" in content
    assert "startup-last.log" in content
    assert "timeout /t 20" in content

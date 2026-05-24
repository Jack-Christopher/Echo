"""Log browser launch commands and subprocess output for debugging."""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from echo.config.store import appdata_dir


def browser_log_path() -> Path:
    return appdata_dir() / "logs" / "browser-last.log"


def _format_cmd(cmd: list[str]) -> str:
    return subprocess.list2cmdline(cmd)


def write_browser_launch_log(
    cmd: list[str],
    proc: subprocess.Popen[str] | subprocess.Popen[bytes] | None = None,
    *,
    error: str = "",
    focus_ok: bool | None = None,
) -> Path:
    """Write command, pid, exit code, and captured stdout/stderr to browser-last.log."""
    log_dir = browser_log_path().parent
    log_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        f"[{datetime.now().isoformat(timespec='seconds')}] Browser launch",
        f"command: {_format_cmd(cmd)}",
    ]

    if error:
        lines.append(f"error: {error}")
    elif proc is not None:
        lines.append(f"pid: {proc.pid}")
        rc = proc.poll()
        if rc is None:
            lines.append("status: running (browser detached or still starting)")
            stdout = stderr = ""
        else:
            stdout, stderr = proc.communicate()
            lines.append(f"exit_code: {rc}")
            if stdout:
                lines.append(f"stdout:\n{stdout.rstrip()}")
            if stderr:
                lines.append(f"stderr:\n{stderr.rstrip()}")
            if not stdout and not stderr:
                lines.append("stdout/stderr: (empty)")

    if focus_ok is not None:
        lines.append(f"focus: {'ok' if focus_ok else 'failed'}")

    path = browser_log_path()
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path

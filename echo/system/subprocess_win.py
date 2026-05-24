"""Windows subprocess helpers (hide console windows)."""

from __future__ import annotations

import subprocess
import sys


def no_window_kwargs() -> dict[str, object]:
    """Keyword args for console CLIs (Whisper/Piper). Do not use for GUI apps like browsers."""
    if sys.platform != "win32":
        return {}
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    return {
        "startupinfo": startupinfo,
        "creationflags": subprocess.CREATE_NO_WINDOW,
    }

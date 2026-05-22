"""Backward-compatible entry points (implementation in control.py)."""

from __future__ import annotations

from echo.browser.control import (
    find_browser_path,
    focus,
    is_running as is_browser_running,
    launch,
    open_url,
)
from echo.config.schema import EchoConfig

BRAVE_NAMES = ("brave.exe", "brave")


def find_brave_path(config: EchoConfig):
    return find_browser_path(config)


def is_running() -> bool:
    """True if Brave process exists (legacy helper, ignores config.browser)."""
    import psutil

    for proc in psutil.process_iter(["name"]):
        try:
            name = (proc.info.get("name") or "").lower()
            if name in BRAVE_NAMES:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def focus_brave() -> bool:
    """Focus Brave window only (legacy; use control.focus(config) instead)."""
    try:
        from pywinauto import Application

        app = Application(backend="uia").connect(path="brave.exe", timeout=3)
        win = app.top_window()
        win.set_focus()
        return True
    except Exception:
        return False


__all__ = ["find_brave_path", "is_running", "focus_brave", "launch", "open_url", "BRAVE_NAMES"]

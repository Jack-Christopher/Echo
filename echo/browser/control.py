"""Multi-browser launch, focus, and new-tab handling (Windows)."""

from __future__ import annotations

import logging
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import psutil

from echo.config.schema import EchoConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BrowserSpec:
    id: str
    label: str
    process_names: tuple[str, ...]
    connect_path: str
    new_tab_flag: str
    default_paths: tuple[Path, ...]


def _pf(*parts: str) -> Path:
    return Path(os.environ.get("PROGRAMFILES", "C:\\Program Files"), *parts)


def _pf86(*parts: str) -> Path:
    return Path(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), *parts)


def _local(*parts: str) -> Path:
    return Path(os.environ.get("LOCALAPPDATA", ""), *parts)


BROWSER_SPECS: dict[str, BrowserSpec] = {
    "brave": BrowserSpec(
        id="brave",
        label="Brave",
        process_names=("brave.exe", "brave"),
        connect_path="brave.exe",
        new_tab_flag="--new-tab",
        default_paths=(
            _pf("BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
            _pf86("BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
            _local("BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
        ),
    ),
    "chrome": BrowserSpec(
        id="chrome",
        label="Google Chrome",
        process_names=("chrome.exe", "chrome"),
        connect_path="chrome.exe",
        new_tab_flag="--new-tab",
        default_paths=(
            _pf("Google", "Chrome", "Application", "chrome.exe"),
            _pf86("Google", "Chrome", "Application", "chrome.exe"),
            _local("Google", "Chrome", "Application", "chrome.exe"),
        ),
    ),
    "edge": BrowserSpec(
        id="edge",
        label="Microsoft Edge",
        process_names=("msedge.exe", "msedge"),
        connect_path="msedge.exe",
        new_tab_flag="--new-tab",
        default_paths=(
            _pf("Microsoft", "Edge", "Application", "msedge.exe"),
            _pf86("Microsoft", "Edge", "Application", "msedge.exe"),
        ),
    ),
    "firefox": BrowserSpec(
        id="firefox",
        label="Mozilla Firefox",
        process_names=("firefox.exe", "firefox"),
        connect_path="firefox.exe",
        new_tab_flag="-new-tab",
        default_paths=(
            _pf("Mozilla Firefox", "firefox.exe"),
            _pf86("Mozilla Firefox", "firefox.exe"),
        ),
    ),
    "opera": BrowserSpec(
        id="opera",
        label="Opera",
        process_names=("opera.exe", "opera"),
        connect_path="opera.exe",
        new_tab_flag="--new-tab",
        default_paths=(
            _local("Programs", "Opera", "opera.exe"),
            _pf("Opera", "opera.exe"),
            _pf("Opera", "launcher.exe"),
        ),
    ),
    "opera_gx": BrowserSpec(
        id="opera_gx",
        label="Opera GX",
        process_names=("opera.exe", "opera"),
        connect_path="opera.exe",
        new_tab_flag="--new-tab",
        default_paths=(
            _local("Programs", "Opera GX", "opera.exe"),
            _pf("Opera GX", "opera.exe"),
        ),
    ),
}

BROWSER_IDS: tuple[str, ...] = tuple(BROWSER_SPECS.keys())


def normalize_browser_id(browser: str | None) -> str:
    key = (browser or "brave").strip().lower().replace(" ", "_")
    if key in BROWSER_SPECS:
        return key
    return "brave"


def get_spec(config: EchoConfig) -> BrowserSpec:
    return BROWSER_SPECS[normalize_browser_id(config.browser)]


def browser_path_override(config: EchoConfig) -> str:
    return (config.browser_path or config.brave_path or "").strip()


def find_browser_path(config: EchoConfig) -> Path | None:
    custom = browser_path_override(config)
    if custom:
        p = Path(custom)
        if p.is_file():
            return p
    spec = get_spec(config)
    for candidate in spec.default_paths:
        if candidate.is_file():
            return candidate
    return None


def is_running(config: EchoConfig) -> bool:
    spec = get_spec(config)
    names = {n.lower() for n in spec.process_names}
    for proc in psutil.process_iter(["name"]):
        try:
            name = (proc.info.get("name") or "").lower()
            if name in names:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def launch(url: str, config: EchoConfig) -> bool:
    """Open URL in a new tab (starts browser if needed)."""
    exe = find_browser_path(config)
    if not exe:
        logger.error("%s executable not found", get_spec(config).label)
        return False
    spec = get_spec(config)
    subprocess.Popen(
        [str(exe), spec.new_tab_flag, url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return True


def focus(config: EchoConfig) -> bool:
    spec = get_spec(config)
    try:
        from pywinauto import Application

        app = Application(backend="uia").connect(path=spec.connect_path, timeout=3)
        win = app.top_window()
        win.set_focus()
        time.sleep(0.15)
        return True
    except Exception as e:
        logger.debug("focus %s failed: %s", spec.id, e)
        return False


def open_url(url: str, config: EchoConfig) -> bool:
    """Open URL in a new tab (Chromium/Firefox CLI; keyboard fallback)."""
    if launch(url, config):
        return True
    if is_running(config) and focus(config):
        import pyautogui

        pyautogui.hotkey("ctrl", "t")
        time.sleep(0.1)
        pyautogui.write(url, interval=0.02)
        pyautogui.press("enter")
        return True
    return False

"""Media key simulation."""

from __future__ import annotations

import pyautogui

pyautogui.FAILSAFE = False

_KEY_MAP = {
    "play": "playpause",
    "pause": "playpause",
    "playpause": "playpause",
    "next": "nexttrack",
    "previous": "prevtrack",
    "mute": "volumemute",
    "unmute": "volumeup",
}


def send_media_key(action: str) -> bool:
    key = _KEY_MAP.get(action, action)
    try:
        pyautogui.press(key)
        return True
    except Exception:
        return False

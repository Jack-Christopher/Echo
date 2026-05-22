"""System volume control via pycaw."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_STEP = 0.1


def _get_interface():
    try:
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return interface.QueryInterface(IAudioEndpointVolume)
    except Exception as e:
        logger.debug("pycaw unavailable: %s", e)
        return None


def adjust(direction: str, preferred: int = 50) -> bool:
    vol = _get_interface()
    if vol is None:
        return _fallback_keys(direction)
    try:
        current = vol.GetMasterVolumeLevelScalar()
        if direction == "up":
            new_val = min(1.0, current + _STEP)
        else:
            new_val = max(0.0, current - _STEP)
        vol.SetMasterVolumeLevelScalar(new_val, None)
        return True
    except Exception as e:
        logger.debug("volume adjust failed: %s", e)
        return _fallback_keys(direction)


def set_level(percent: int) -> bool:
    vol = _get_interface()
    if vol is None:
        return False
    try:
        vol.SetMasterVolumeLevelScalar(max(0, min(100, percent)) / 100.0, None)
        return True
    except Exception:
        return False


def _fallback_keys(direction: str) -> bool:
    try:
        import pyautogui

        key = "volumeup" if direction == "up" else "volumedown"
        pyautogui.press(key)
        return True
    except Exception:
        return False

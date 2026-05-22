"""Screen brightness control."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_STEP = 10


def adjust(direction: str) -> bool:
    try:
        import screen_brightness_control as sbc

        current = sbc.get_brightness(display=0)
        if isinstance(current, list):
            current = current[0] if current else 50
        if direction == "up":
            new_val = min(100, int(current) + _STEP)
        else:
            new_val = max(0, int(current) - _STEP)
        sbc.set_brightness(new_val, display=0)
        return True
    except Exception as e:
        logger.debug("brightness adjust failed: %s", e)
        return False


def set_level(percent: int) -> bool:
    try:
        import screen_brightness_control as sbc

        sbc.set_brightness(max(0, min(100, percent)), display=0)
        return True
    except Exception:
        return False

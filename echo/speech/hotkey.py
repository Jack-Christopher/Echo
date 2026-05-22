"""Global push-to-talk hotkey (Win+Space default) via key state polling."""

from __future__ import annotations

import ctypes
import logging
import threading
import time
from typing import Callable

logger = logging.getLogger(__name__)

VK_LWIN = 0x5B
VK_RWIN = 0x5C
VK_MENU = 0x12
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_SPACE = 0x20

_HOTKEY_MAP = {
    "win+space": (VK_LWIN, VK_SPACE),
    "windows+space": (VK_LWIN, VK_SPACE),
    "alt+space": (VK_MENU, VK_SPACE),
    "ctrl+space": (VK_CONTROL, VK_SPACE),
    "shift+space": (VK_SHIFT, VK_SPACE),
}


class PushToTalkHotkey:
    def __init__(
        self,
        hotkey: str = "win+space",
        on_press: Callable[[], None] | None = None,
        on_release: Callable[[], None] | None = None,
        poll_interval: float = 0.05,
    ) -> None:
        self._hotkey = hotkey.lower().strip().replace("windows", "win")
        self._on_press = on_press
        self._on_release = on_release
        self._poll_interval = poll_interval
        key = self._hotkey.replace("windows", "win")
        self._mods_vk = _HOTKEY_MAP.get(key, _HOTKEY_MAP["win+space"])
        self._thread: threading.Thread | None = None
        self._running = False
        self._pressed = False
        self._user32 = ctypes.windll.user32

    def register(self) -> bool:
        key = self._hotkey.replace("windows", "win")
        if key not in _HOTKEY_MAP:
            logger.error("Unsupported hotkey: %s", self._hotkey)
            return False
        logger.info("PTT hotkey registered: %s", self._hotkey)
        return True

    def unregister(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def start_listener(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def _is_key_down(self, vk: int) -> bool:
        return bool(self._user32.GetAsyncKeyState(vk) & 0x8000)

    def _mod_down(self, mod_vk: int) -> bool:
        if mod_vk in (VK_LWIN, VK_RWIN):
            return self._is_key_down(VK_LWIN) or self._is_key_down(VK_RWIN)
        return self._is_key_down(mod_vk)

    def _combo_down(self) -> bool:
        mod_vk, key_vk = self._mods_vk
        return self._mod_down(mod_vk) and self._is_key_down(key_vk)

    def _poll_loop(self) -> None:
        while self._running:
            down = self._combo_down()
            if down and not self._pressed:
                self._pressed = True
                if self._on_press:
                    self._on_press()
            elif not down and self._pressed:
                self._pressed = False
                if self._on_release:
                    self._on_release()
            time.sleep(self._poll_interval)

    def simulate_press(self) -> None:
        if not self._pressed:
            self._pressed = True
            if self._on_press:
                self._on_press()

    def simulate_release(self) -> None:
        if self._pressed:
            self._pressed = False
            if self._on_release:
                self._on_release()

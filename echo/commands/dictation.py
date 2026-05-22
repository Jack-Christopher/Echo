"""Dictation mode: type spoken text."""

from __future__ import annotations

import time

import pyautogui

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.02


def type_text(text: str) -> None:
    if not text:
        return
    pyautogui.write(text, interval=0.01)

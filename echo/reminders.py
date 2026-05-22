"""Simple reminder scheduler (v2)."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable

from echo.config.store import appdata_dir

logger = logging.getLogger(__name__)


class ReminderScheduler:
    def __init__(
        self,
        on_fire: Callable[[dict], None] | None = None,
        store_path: Path | None = None,
    ) -> None:
        self._on_fire = on_fire
        self._path = store_path or (appdata_dir() / "reminders.json")
        self._reminders: list[dict] = []

    def load(self) -> list[dict]:
        if self._path.is_file():
            try:
                self._reminders = json.loads(
                    self._path.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, OSError):
                self._reminders = []
        return self._reminders

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._reminders, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def add(self, text: str, due_iso: str) -> dict:
        entry = {"text": text, "due": due_iso, "fired": False}
        self._reminders.append(entry)
        self.save()
        return entry

    def check_due(self) -> list[dict]:
        now = datetime.now()
        fired = []
        for r in self._reminders:
            if r.get("fired"):
                continue
            due_str = r.get("due", "")
            try:
                due = datetime.fromisoformat(due_str)
            except ValueError:
                continue
            if due <= now:
                r["fired"] = True
                fired.append(r)
                if self._on_fire:
                    self._on_fire(r)
        if fired:
            self.save()
        return fired

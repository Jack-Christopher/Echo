"""Append-only command history (JSONL)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from echo.config.store import appdata_dir


def default_log_path() -> Path:
    return appdata_dir() / "logs" / "history.jsonl"


def normalize_entry(entry: dict[str, Any]) -> dict[str, str]:
    """Map legacy JSONL rows to text / intent / result only."""
    text = entry.get("text") or entry.get("raw_text") or ""
    intent = entry.get("intent") or ""
    result = entry.get("result") or entry.get("message") or entry.get("error") or ""
    if not result and "success" in entry:
        result = "ok" if entry.get("success") else "fallo"
    return {"text": str(text), "intent": str(intent), "result": str(result)}


def format_entry_line(entry: dict[str, Any]) -> str:
    row = normalize_entry(entry)
    return f"{row['text']} → {row['intent']} → {row['result']}"


class HistoryLog:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or default_log_path()

    @property
    def path(self) -> Path:
        return self._path

    def append(
        self,
        raw_text: str,
        intent_name: str,
        success: bool,
        message: str = "",
        error: str = "",
    ) -> None:
        result = message or error or ("ok" if success else "fallo")
        entry = {
            "text": raw_text,
            "intent": intent_name,
            "result": result,
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def read_recent(self, limit: int = 100) -> list[dict[str, str]]:
        if not self._path.is_file():
            return []
        lines = self._path.read_text(encoding="utf-8").strip().splitlines()
        entries: list[dict[str, str]] = []
        for line in lines[-limit:]:
            try:
                entries.append(normalize_entry(json.loads(line)))
            except json.JSONDecodeError:
                continue
        return entries

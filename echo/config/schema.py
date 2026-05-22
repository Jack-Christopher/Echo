"""Typed configuration schema and validation."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from echo.config.resources import normalize_link_handlers, normalize_websites


def _defaults_path() -> Path:
    return Path(__file__).resolve().parent / "defaults.json"


def load_default_dict() -> dict[str, Any]:
    with open(_defaults_path(), encoding="utf-8") as f:
        return json.load(f)


@dataclass
class EchoConfig:
    hotkey: str = "win+space"
    fuzzy_threshold: int = 85
    voice_confirmations: bool = True
    always_listening: bool = False
    search_engine_template: str = "https://www.google.com/search?q={query}"
    browser: str = "brave"
    browser_path: str = ""
    brave_path: str = ""
    preferred_volume: int = 50
    whisper_model: str = "small"
    whisper_model_path: str = ""
    whisper_beam_size: int = 8
    whisper_best_of: int = 5
    whisper_threads: int = 0
    whisper_use_prompt: bool = True
    websites: dict[str, Any] = field(default_factory=dict)
    link_handlers: dict[str, Any] = field(default_factory=dict)
    search_routes: list[dict[str, Any]] = field(default_factory=list)
    custom_site_searches: list[dict[str, Any]] = field(default_factory=list)
    folders: dict[str, str] = field(default_factory=dict)
    series: list[str] = field(default_factory=list)
    routines: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    reminders: list[dict[str, Any]] = field(default_factory=list)
    dictation_active: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EchoConfig:
        base = load_default_dict()
        merged = {**base, **data}
        return cls(
            hotkey=str(merged.get("hotkey", "win+space")),
            fuzzy_threshold=int(merged.get("fuzzy_threshold", 85)),
            voice_confirmations=bool(merged.get("voice_confirmations", True)),
            always_listening=bool(merged.get("always_listening", False)),
            search_engine_template=str(
                merged.get(
                    "search_engine_template",
                    "https://www.google.com/search?q={query}",
                )
            ),
            browser=str(merged.get("browser", "brave")),
            browser_path=str(
                merged.get("browser_path") or merged.get("brave_path", "")
            ),
            brave_path=str(
                merged.get("brave_path") or merged.get("browser_path", "")
            ),
            preferred_volume=int(merged.get("preferred_volume", 50)),
            whisper_model=str(merged.get("whisper_model", "small")),
            whisper_model_path=str(merged.get("whisper_model_path", "")),
            whisper_beam_size=int(merged.get("whisper_beam_size", 8)),
            whisper_best_of=int(merged.get("whisper_best_of", 5)),
            whisper_threads=int(merged.get("whisper_threads", 0)),
            whisper_use_prompt=bool(merged.get("whisper_use_prompt", True)),
            websites=normalize_websites(dict(merged.get("websites", {}))),
            link_handlers=normalize_link_handlers(merged.get("link_handlers")),
            search_routes=list(merged.get("search_routes") or []),
            custom_site_searches=list(merged.get("custom_site_searches") or []),
            folders=dict(merged.get("folders", {})),
            series=list(merged.get("series", [])),
            routines=dict(merged.get("routines", {})),
            reminders=list(merged.get("reminders", [])),
            dictation_active=bool(merged.get("dictation_active", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "hotkey": self.hotkey,
            "fuzzy_threshold": self.fuzzy_threshold,
            "voice_confirmations": self.voice_confirmations,
            "always_listening": self.always_listening,
            "search_engine_template": self.search_engine_template,
            "browser": self.browser,
            "browser_path": self.browser_path,
            "brave_path": self.brave_path,
            "preferred_volume": self.preferred_volume,
            "whisper_model": self.whisper_model,
            "whisper_model_path": self.whisper_model_path,
            "whisper_beam_size": self.whisper_beam_size,
            "whisper_best_of": self.whisper_best_of,
            "whisper_threads": self.whisper_threads,
            "whisper_use_prompt": self.whisper_use_prompt,
            "websites": copy.deepcopy(self.websites),
            "link_handlers": copy.deepcopy(self.link_handlers),
            "search_routes": copy.deepcopy(self.search_routes),
            "custom_site_searches": copy.deepcopy(self.custom_site_searches),
            "folders": copy.deepcopy(self.folders),
            "series": list(self.series),
            "routines": copy.deepcopy(self.routines),
            "reminders": copy.deepcopy(self.reminders),
            "dictation_active": self.dictation_active,
        }

    def mirror_subset(self) -> dict[str, Any]:
        """Subset mirrored to project backup config."""
        return {
            "websites": copy.deepcopy(self.websites),
            "link_handlers": copy.deepcopy(self.link_handlers),
            "search_routes": copy.deepcopy(self.search_routes),
            "custom_site_searches": copy.deepcopy(self.custom_site_searches),
            "folders": copy.deepcopy(self.folders),
            "series": list(self.series),
        }

    def validate(self) -> None:
        from echo.browser.control import normalize_browser_id

        if not 0 <= self.fuzzy_threshold <= 100:
            raise ValueError("fuzzy_threshold must be 0-100")
        if not 0 <= self.preferred_volume <= 100:
            raise ValueError("preferred_volume must be 0-100")
        if not 1 <= self.whisper_beam_size <= 16:
            raise ValueError("whisper_beam_size must be 1-16")
        if not 1 <= self.whisper_best_of <= 10:
            raise ValueError("whisper_best_of must be 1-10")
        wm = (self.whisper_model or "small").lower()
        if wm not in ("base", "small", "medium", "large"):
            self.whisper_model = "small"
        else:
            self.whisper_model = wm
        self.browser = normalize_browser_id(self.browser)
        self.websites = normalize_websites(self.websites)
        self.link_handlers = normalize_link_handlers(self.link_handlers)

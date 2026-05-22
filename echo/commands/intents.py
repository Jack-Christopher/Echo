"""Command intent dataclasses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Intent:
    name: str


@dataclass(frozen=True)
class OpenWebsite(Intent):
    alias: str
    url: str

    def __init__(self, alias: str, url: str) -> None:
        object.__setattr__(self, "name", "open_website")
        object.__setattr__(self, "alias", alias)
        object.__setattr__(self, "url", url)


@dataclass(frozen=True)
class SearchWeb(Intent):
    query: str
    url: str
    route_label: str

    def __init__(self, query: str, url: str = "", route_label: str = "") -> None:
        object.__setattr__(self, "name", "search_web")
        object.__setattr__(self, "query", query)
        object.__setattr__(self, "url", url)
        object.__setattr__(self, "route_label", route_label)


@dataclass(frozen=True)
class MediaControl(Intent):
    action: str

    def __init__(self, action: str) -> None:
        object.__setattr__(self, "name", "media_control")
        object.__setattr__(self, "action", action)


@dataclass(frozen=True)
class SystemAdjust(Intent):
    target: str
    direction: str

    def __init__(self, target: str, direction: str) -> None:
        object.__setattr__(self, "name", "system_adjust")
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "direction", direction)


@dataclass(frozen=True)
class OpenFolder(Intent):
    folder_key: str

    def __init__(self, folder_key: str) -> None:
        object.__setattr__(self, "name", "open_folder")
        object.__setattr__(self, "folder_key", folder_key)


@dataclass(frozen=True)
class RunRoutine(Intent):
    routine_name: str

    def __init__(self, routine_name: str) -> None:
        object.__setattr__(self, "name", "run_routine")
        object.__setattr__(self, "routine_name", routine_name)


@dataclass(frozen=True)
class DictationToggle(Intent):
    enable: bool

    def __init__(self, enable: bool) -> None:
        object.__setattr__(self, "name", "dictation_toggle")
        object.__setattr__(self, "enable", enable)


@dataclass(frozen=True)
class DictationText(Intent):
    text: str

    def __init__(self, text: str) -> None:
        object.__setattr__(self, "name", "dictation_text")
        object.__setattr__(self, "text", text)


@dataclass(frozen=True)
class Unknown(Intent):
    raw: str

    def __init__(self, raw: str) -> None:
        object.__setattr__(self, "name", "unknown")
        object.__setattr__(self, "raw", raw)


@dataclass(frozen=True)
class ActionChain(Intent):
    steps: tuple[Any, ...]

    def __init__(self, steps: tuple[Any, ...]) -> None:
        object.__setattr__(self, "name", "action_chain")
        object.__setattr__(self, "steps", steps)

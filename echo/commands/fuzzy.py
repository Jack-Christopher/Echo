"""RapidFuzz-based fuzzy command matching."""

from __future__ import annotations

from rapidfuzz import fuzz, process

from echo.commands.intents import (
    DictationToggle,
    Intent,
    MediaControl,
    OpenFolder,
    OpenWebsite,
    RunRoutine,
    SystemAdjust,
)
from echo.config.resources import normalize_website_entry, website_url
from echo.config.schema import EchoConfig

_CANONICAL: list[tuple[str, str, dict]] = [
    ("pausa", "media_control", {"action": "pause"}),
    ("reproducir", "media_control", {"action": "play"}),
    ("siguiente", "media_control", {"action": "next"}),
    ("siguiente video", "media_control", {"action": "next"}),
    ("anterior", "media_control", {"action": "previous"}),
    ("silencio", "media_control", {"action": "mute"}),
    ("desilenciar", "media_control", {"action": "unmute"}),
    ("sube volumen", "system_adjust", {"target": "volume", "direction": "up"}),
    ("baja volumen", "system_adjust", {"target": "volume", "direction": "down"}),
    ("sube brillo", "system_adjust", {"target": "brightness", "direction": "up"}),
    ("baja brillo", "system_adjust", {"target": "brightness", "direction": "down"}),
    ("abre descargas", "open_folder", {"folder_key": "descargas"}),
    ("abre documentos", "open_folder", {"folder_key": "documentos"}),
    ("iniciar dictado", "dictation_toggle", {"enable": True}),
    ("terminar dictado", "dictation_toggle", {"enable": False}),
]


def _build_phrase_index(config: EchoConfig) -> dict[str, tuple[str, dict]]:
    index: dict[str, tuple[str, dict]] = {}
    for phrase, kind, payload in _CANONICAL:
        index[phrase] = (kind, payload)
    for alias in config.websites:
        for template in (f"abre {alias}", f"pon {alias}"):
            index[template] = ("open_website", {"alias": alias})
    return index


def _intent_from_match(kind: str, payload: dict, config: EchoConfig) -> Intent | None:
    if kind == "open_website":
        alias = payload["alias"]
        entry = config.websites.get(alias)
        if entry:
            url = website_url(normalize_website_entry(entry))
            if url:
                return OpenWebsite(alias=alias, url=url)
    elif kind == "media_control":
        return MediaControl(action=payload["action"])
    elif kind == "system_adjust":
        return SystemAdjust(target=payload["target"], direction=payload["direction"])
    elif kind == "open_folder":
        return OpenFolder(folder_key=payload["folder_key"])
    elif kind == "dictation_toggle":
        return DictationToggle(enable=payload["enable"])
    elif kind == "run_routine":
        name = payload["routine_name"]
        if name in config.routines:
            return RunRoutine(routine_name=name)
    return None


def match_fuzzy(text: str, config: EchoConfig) -> Intent | None:
    index = _build_phrase_index(config)
    phrases = list(index.keys())
    result = process.extractOne(text, phrases, scorer=fuzz.token_sort_ratio)
    if not result:
        return None
    matched_phrase, score, _ = result
    if score < config.fuzzy_threshold:
        return None
    kind, payload = index[matched_phrase]
    return _intent_from_match(kind, payload, config)

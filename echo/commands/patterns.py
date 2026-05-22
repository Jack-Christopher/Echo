"""Spanish regex patterns for command routing."""

from __future__ import annotations

import re
from typing import Callable

from echo.commands.intents import (
    DictationToggle,
    Intent,
    MediaControl,
    OpenFolder,
    OpenWebsite,
    RunRoutine,
    SearchWeb,
    SystemAdjust,
)
from echo.commands.search_router import resolve_search
from echo.config.resources import normalize_website_entry, website_url
from echo.config.schema import EchoConfig

_OPEN_RE = re.compile(
    r"^(?:abre|abrir|abreme|pon|poner|quiero|ir a|ve a|ve al|ir al)\s+(.+)$"
)
_SEARCH_RE = re.compile(r"^(?:busca|buscar|search|googlea|google)\s+(.+)$")
_ROUTINE_RE = re.compile(r"^(?:modo|rutina|activar)\s+(.+)$")
_DICTATION_START_RE = re.compile(
    r"^(?:iniciar|empezar|activar)\s+(?:el\s+)?dictado$"
)
_DICTATION_STOP_RE = re.compile(
    r"^(?:terminar|finalizar|parar|detener)\s+(?:el\s+)?dictado$"
)

_MEDIA_MAP = {
    "pausa": "pause",
    "pause": "pause",
    "reproducir": "play",
    "play": "play",
    "siguiente": "next",
    "siguiente video": "next",
    "anterior": "previous",
    "silencio": "mute",
    "mute": "mute",
    "desilenciar": "unmute",
}

_SYSTEM_RE = re.compile(
    r"^(?:(sube|baja|aumenta|reduce|mas|menos)\s+)?(volumen|brillo|brightness|volume)$"
)
_SYSTEM_ALT_RE = re.compile(
    r"^(sube|baja)\s+(?:el\s+)?(volumen|brillo)$"
)

_FOLDER_RE = re.compile(r"^(?:abre|abrir)\s+(descargas|documentos|downloads)$")


def match_patterns(text: str, config: EchoConfig) -> Intent | None:
    if config.dictation_active:
        stop = _DICTATION_STOP_RE.match(text)
        if stop:
            return DictationToggle(enable=False)
        return None

    m = _DICTATION_START_RE.match(text)
    if m:
        return DictationToggle(enable=True)

    m = _SEARCH_RE.match(text)
    if m:
        raw_q = m.group(1).strip()
        resolved = resolve_search(raw_q, config)
        return SearchWeb(
            query=resolved.query,
            url=resolved.url,
            route_label=resolved.label,
        )

    m = _OPEN_RE.match(text)
    if m:
        alias = m.group(1).strip()
        if "://" in alias or alias.startswith(("http", "https", "ftp", "ftps")):
            return OpenWebsite(alias=alias, url=alias)
        entry = config.websites.get(alias)
        if entry:
            normalized = normalize_website_entry(entry)
            url = website_url(normalized)
            if url:
                return OpenWebsite(alias=alias, url=url)

    m = _ROUTINE_RE.match(text)
    if m:
        name = m.group(1).strip().replace(" ", "_")
        if name in config.routines:
            return RunRoutine(routine_name=name)

    if text in _MEDIA_MAP:
        return MediaControl(action=_MEDIA_MAP[text])

    m = _SYSTEM_ALT_RE.match(text)
    if m:
        direction = "up" if m.group(1) in ("sube", "aumenta", "mas") else "down"
        target = "volume" if "volumen" in m.group(2) else "brightness"
        return SystemAdjust(target=target, direction=direction)

    m = _SYSTEM_RE.match(text)
    if m:
        direction_word = m.group(1)
        target_word = m.group(2)
        if direction_word:
            direction = (
                "up"
                if direction_word in ("sube", "aumenta", "mas")
                else "down"
            )
        else:
            direction = "up"
        target = "volume" if target_word in ("volumen", "volume") else "brightness"
        return SystemAdjust(target=target, direction=direction)

    m = _FOLDER_RE.match(text)
    if m:
        key = m.group(1)
        if key == "downloads":
            key = "descargas"
        return OpenFolder(folder_key=key)

    return None


def match_open_alias(
    text: str, config: EchoConfig, resolver: Callable[[str], str | None]
) -> Intent | None:
    """Resolve alias via websites dict after normalization."""
    url = resolver(text)
    if url:
        return OpenWebsite(alias=text, url=url)
    return None

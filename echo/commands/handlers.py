"""Intent → action handlers."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from echo.automation.routines import RoutineRunner
from echo.browser.control import get_spec
from echo.browser.link_opener import open_resource
from echo.browser import navigation
from echo.commands.intents import (
    ActionChain,
    DictationText,
    DictationToggle,
    Intent,
    MediaControl,
    OpenFolder,
    OpenWebsite,
    RunRoutine,
    SearchWeb,
    SystemAdjust,
    Unknown,
)
from echo.config.schema import EchoConfig
from echo.system import brightness, files, media, volume

logger = logging.getLogger(__name__)


@dataclass
class HandlerResult:
    success: bool
    message: str = ""
    speak: bool = True


class IntentHandlers:
    def __init__(self, config: EchoConfig) -> None:
        self._config = config
        self._routines = RoutineRunner(config)
        self._on_dictation_change: Callable[[bool], None] | None = None

    def set_dictation_callback(self, cb: Callable[[bool], None]) -> None:
        self._on_dictation_change = cb

    def update_config(self, config: EchoConfig) -> None:
        self._config = config
        self._routines.update_config(config)

    def handle(self, intent: Intent) -> HandlerResult:
        handlers = {
            "open_website": self._open_website,
            "search_web": self._search_web,
            "media_control": self._media_control,
            "system_adjust": self._system_adjust,
            "open_folder": self._open_folder,
            "run_routine": self._run_routine,
            "dictation_toggle": self._dictation_toggle,
            "dictation_text": self._dictation_text,
            "action_chain": self._action_chain,
            "unknown": self._unknown,
        }
        handler = handlers.get(intent.name, self._unknown)
        return handler(intent)  # type: ignore[arg-type]

    def _open_website(self, intent: OpenWebsite) -> HandlerResult:
        ok = open_resource(intent.url, self._config)
        browser = get_spec(self._config).label
        return HandlerResult(
            success=ok,
            message=f"Abriendo {intent.alias} en {browser}" if ok else f"No se encontro {browser}",
        )

    def _search_web(self, intent: SearchWeb) -> HandlerResult:
        ok = navigation.search(
            intent.query,
            self._config,
            url=intent.url or None,
        )
        label = intent.route_label or "Web"
        msg = f"{label}: {intent.query}" if ok else f"Fallo busqueda: {intent.query}"
        return HandlerResult(success=ok, message=msg)

    def _media_control(self, intent: MediaControl) -> HandlerResult:
        media.send_media_key(intent.action)
        return HandlerResult(success=True, message="Listo")

    def _system_adjust(self, intent: SystemAdjust) -> HandlerResult:
        if intent.target == "volume":
            volume.adjust(intent.direction, self._config.preferred_volume)
        else:
            brightness.adjust(intent.direction)
        return HandlerResult(success=True, message="Listo")

    def _open_folder(self, intent: OpenFolder) -> HandlerResult:
        path = files.resolve_folder(intent.folder_key, self._config)
        files.open_folder(path)
        return HandlerResult(success=True, message=f"Abriendo {intent.folder_key}")

    def _run_routine(self, intent: RunRoutine) -> HandlerResult:
        ok = self._routines.run(intent.routine_name)
        return HandlerResult(
            success=ok,
            message=f"Rutina {intent.routine_name}" if ok else "Rutina no encontrada",
        )

    def _dictation_toggle(self, intent: DictationToggle) -> HandlerResult:
        self._config.dictation_active = intent.enable
        if self._on_dictation_change:
            self._on_dictation_change(intent.enable)
        msg = "Dictado iniciado" if intent.enable else "Dictado terminado"
        return HandlerResult(success=True, message=msg)

    def _dictation_text(self, intent: DictationText) -> HandlerResult:
        from echo.commands.dictation import type_text

        type_text(intent.text)
        return HandlerResult(success=True, message="", speak=False)

    def _action_chain(self, intent: ActionChain) -> HandlerResult:
        for step in intent.steps:
            self.handle(step)
        return HandlerResult(success=True, message="Listo")

    def _unknown(self, intent: Unknown) -> HandlerResult:
        logger.warning("Unknown command: %s", intent.raw)
        return HandlerResult(
            success=False,
            message="No entendi",
            speak=False,
        )

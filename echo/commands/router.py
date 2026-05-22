"""Command router: utterance → intent."""

from __future__ import annotations

from echo.commands import fuzzy, patterns
from echo.commands.intents import DictationText, Unknown
from echo.commands.normalizer import normalize
from echo.config.schema import EchoConfig
from echo.commands.intents import Intent


class CommandRouter:
    def __init__(self, config: EchoConfig) -> None:
        self._config = config

    @property
    def config(self) -> EchoConfig:
        return self._config

    def update_config(self, config: EchoConfig) -> None:
        self._config = config

    def route(self, raw_text: str) -> Intent:
        text = normalize(raw_text)
        if not text:
            return Unknown(raw=raw_text)

        if self._config.dictation_active:
            stop = patterns.match_patterns(text, self._config)
            if stop is not None and stop.name == "dictation_toggle":
                return stop
            return DictationText(text=raw_text.strip())

        intent = patterns.match_patterns(text, self._config)
        if intent is not None:
            return intent

        intent = fuzzy.match_fuzzy(text, self._config)
        if intent is not None:
            return intent

        return Unknown(raw=raw_text)

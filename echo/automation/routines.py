"""Named multi-step routines."""

from __future__ import annotations

import logging

from echo.browser.link_opener import open_resource
from echo.browser import navigation
from echo.config.schema import EchoConfig
from echo.system import brightness, volume

logger = logging.getLogger(__name__)


class RoutineRunner:
    def __init__(self, config: EchoConfig) -> None:
        self._config = config

    def update_config(self, config: EchoConfig) -> None:
        self._config = config

    def run(self, name: str) -> bool:
        steps = self._config.routines.get(name)
        if not steps:
            if name == "noche":
                return self._default_noche()
            return False
        for step in steps:
            self._execute_step(step)
        return True

    def _default_noche(self) -> bool:
        brightness.set_level(30)
        volume.set_level(20)
        url = self._config.websites.get(
            "youtube", "https://www.youtube.com/results?search_query=relaxing+music"
        )
        open_resource(url, self._config)
        return True

    def _execute_step(self, step: dict) -> None:
        action = step.get("action", "")
        if action == "brightness":
            brightness.set_level(int(step.get("value", 50)))
        elif action == "volume":
            volume.set_level(int(step.get("value", 50)))
        elif action == "open_url":
            open_resource(str(step.get("url", "")), self._config)
        elif action == "search":
            navigation.search(str(step.get("query", "")), self._config)

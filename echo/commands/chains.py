"""Compound command parsing (v3): 'y' / 'luego' chains."""

from __future__ import annotations

import re

from echo.commands.intents import ActionChain, Intent
from echo.commands.router import CommandRouter

_SPLIT_RE = re.compile(r"\s+(?:y|luego|entonces)\s+")


def parse_chain(raw_text: str, router: CommandRouter) -> Intent | None:
    parts = _SPLIT_RE.split(raw_text.strip())
    if len(parts) < 2:
        return None
    steps: list[Intent] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        intent = router.route(part)
        if intent.name == "unknown":
            return None
        steps.append(intent)
    if len(steps) < 2:
        return None
    return ActionChain(steps=tuple(steps))

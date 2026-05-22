"""Browser navigation: open search URLs in a new tab (fast path)."""

from __future__ import annotations

import logging
import urllib.parse

from echo.browser.link_opener import open_resource
from echo.commands.search_router import resolve_search
from echo.config.schema import EchoConfig

logger = logging.getLogger(__name__)


def search(
    query: str,
    config: EchoConfig,
    *,
    url: str | None = None,
) -> bool:
    """Open resolved search URL in a new tab."""
    target = url or open_search_url(query, config)
    ok = open_resource(target, config)
    if not ok:
        logger.warning("search launch failed for query=%r url=%r", query, target)
    return ok


def open_search_url(query: str, config: EchoConfig) -> str:
    return resolve_search(query, config).url

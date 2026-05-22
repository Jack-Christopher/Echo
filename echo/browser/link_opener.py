"""Open URLs and links using per-protocol / per-site handlers."""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from echo.browser.control import find_browser_path, get_spec, launch
from echo.config.resources import (
    normalize_link_handlers,
    normalize_website_entry,
    scheme_for_url,
    website_url,
)
from echo.config.schema import EchoConfig

logger = logging.getLogger(__name__)


def open_resource(
    url: str,
    config: EchoConfig,
    *,
    website_entry: dict[str, str] | None = None,
) -> bool:
    """Open a URL using link_handlers or a website entry opener."""
    url = url.strip()
    if not url:
        return False

    if website_entry:
        opener = website_entry.get("opener", "browser")
        custom = website_entry.get("app", "")
        return _open_with_app(url, config, opener, custom)

    scheme = scheme_for_url(url)
    handlers = normalize_link_handlers(config.link_handlers)
    handler = handlers.get(scheme) or handlers.get("https", {"app": "browser", "path": ""})
    return _open_with_app(url, config, handler.get("app", "browser"), handler.get("path", ""))


def open_website_alias(alias: str, config: EchoConfig) -> bool:
    raw = config.websites.get(alias)
    if raw is None:
        return False
    entry = normalize_website_entry(raw)
    url = website_url(entry)
    if not url:
        return False
    return open_resource(url, config, website_entry=entry)


def _open_with_app(url: str, config: EchoConfig, app: str, custom_path: str) -> bool:
    app = (app or "browser").lower()
    if app == "browser":
        return launch(url, config)
    if app == "shell":
        try:
            os.startfile(url)  # noqa: S606 — Windows shell association
            return True
        except OSError as e:
            logger.error("shell open failed: %s", e)
            return False
    if app == "custom" and custom_path:
        path = Path(custom_path)
        if path.is_file():
            subprocess.Popen([str(path), url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        logger.error("custom opener not found: %s", custom_path)
        return False
    logger.warning("unknown opener %s, using browser", app)
    return launch(url, config)

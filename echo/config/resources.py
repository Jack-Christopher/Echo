"""Normalize websites and link-handler entries from config."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

VALID_OPENERS = frozenset({"browser", "shell", "custom"})


def normalize_website_entry(value: Any) -> dict[str, str]:
    """Return {url, opener, app} with defaults."""
    if isinstance(value, str):
        return {"url": value.strip(), "opener": "browser", "app": ""}
    if isinstance(value, dict):
        url = str(value.get("url", "")).strip()
        opener = str(value.get("opener", "browser")).strip().lower() or "browser"
        if opener not in VALID_OPENERS:
            opener = "browser"
        return {
            "url": url,
            "opener": opener,
            "app": str(value.get("app", "")).strip(),
        }
    return {"url": "", "opener": "browser", "app": ""}


def normalize_websites(raw: dict[str, Any]) -> dict[str, dict[str, str]]:
    return {str(k): normalize_website_entry(v) for k, v in raw.items()}


def website_url(entry: dict[str, str]) -> str:
    return entry.get("url", "")


def normalize_link_handlers(raw: dict[str, Any] | None) -> dict[str, dict[str, str]]:
    if not raw:
        return _default_link_handlers()
    out: dict[str, dict[str, str]] = {}
    for scheme, val in raw.items():
        key = str(scheme).lower().strip()
        if isinstance(val, dict):
            app = str(val.get("app", "browser")).lower() or "browser"
            out[key] = {
                "app": app if app in VALID_OPENERS else "browser",
                "path": str(val.get("path", val.get("app_path", ""))).strip(),
            }
        else:
            out[key] = {"app": "browser", "path": ""}
    return out


def _default_link_handlers() -> dict[str, dict[str, str]]:
    return {
        "http": {"app": "browser", "path": ""},
        "https": {"app": "browser", "path": ""},
        "ftp": {"app": "browser", "path": ""},
        "ftps": {"app": "browser", "path": ""},
        "mailto": {"app": "shell", "path": ""},
        "file": {"app": "shell", "path": ""},
    }


def scheme_for_url(url: str) -> str:
    parsed = urlparse(url)
    return (parsed.scheme or "https").lower()

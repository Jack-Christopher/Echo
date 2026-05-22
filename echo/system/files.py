"""Simple folder open operations."""

from __future__ import annotations

import os
from pathlib import Path

from echo.config.schema import EchoConfig

_WINDOWS_FOLDERS = {
    "downloads": Path.home() / "Downloads",
    "documents": Path.home() / "Documents",
    "descargas": Path.home() / "Downloads",
    "documentos": Path.home() / "Documents",
}


def resolve_folder(folder_key: str, config: EchoConfig) -> Path:
    mapped = config.folders.get(folder_key, folder_key)
    if mapped in _WINDOWS_FOLDERS:
        return _WINDOWS_FOLDERS[mapped]
    if mapped in ("downloads", "documents"):
        return _WINDOWS_FOLDERS[mapped]
    return Path(mapped).expanduser()


def open_folder(path: Path) -> bool:
    path = path.expanduser()
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    os.startfile(str(path))
    return True

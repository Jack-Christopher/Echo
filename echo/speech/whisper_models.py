"""Download Whisper ggml models into models/whisper."""

from __future__ import annotations

import logging
import urllib.request
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WHISPER_DIR = PROJECT_ROOT / "models" / "whisper"
HF_BASE = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main"

MODEL_FILES = {
    "base": "ggml-base.bin",
    "small": "ggml-small.bin",
    "medium": "ggml-medium.bin",
    "large": "ggml-large.bin",
}


def model_file_path(model_id: str) -> Path:
    name = MODEL_FILES.get(model_id, MODEL_FILES["small"])
    return WHISPER_DIR / name


def is_model_installed(model_id: str) -> bool:
    return model_file_path(model_id).is_file()


def download_whisper_model(
    model_id: str,
    *,
    on_progress: Callable[[str], None] | None = None,
) -> tuple[bool, str]:
    """Download one ggml model. Returns (success, message)."""
    if model_id not in MODEL_FILES:
        model_id = "small"
    dest = model_file_path(model_id)
    if dest.is_file():
        return True, f"Modelo ya instalado: {dest.name}"

    WHISPER_DIR.mkdir(parents=True, exist_ok=True)
    url = f"{HF_BASE}/{dest.name}"

    def report(msg: str) -> None:
        logger.info(msg)
        if on_progress:
            on_progress(msg)

    report(f"Descargando {dest.name} (puede tardar varios minutos)...")
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception as e:
        logger.exception("Whisper model download failed: %s", e)
        if dest.is_file():
            dest.unlink(missing_ok=True)
        return False, f"Error al descargar {dest.name}: {e}"

    if not dest.is_file() or dest.stat().st_size < 1_000_000:
        dest.unlink(missing_ok=True)
        return False, f"Descarga incompleta: {dest.name}"

    report(f"Listo: {dest.name}")
    return True, dest.name

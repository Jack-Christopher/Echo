"""Whisper.cpp CLI wrapper with accuracy-oriented defaults."""

from __future__ import annotations

import logging
import os
import re
import subprocess
from pathlib import Path

from echo.config.schema import EchoConfig
from echo.speech.whisper_prompt import build_initial_prompt

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WHISPER_MODELS_DIR = PROJECT_ROOT / "models" / "whisper"
VALID_MODELS = ("small", "base", "medium", "large")


def default_whisper_cli() -> Path:
    return WHISPER_MODELS_DIR / "whisper-cli.exe"


def resolve_model_path(config: EchoConfig | None = None) -> Path:
    """Pick ggml model: explicit path > configured size > base fallback."""
    if config and config.whisper_model_path:
        custom = Path(config.whisper_model_path)
        if custom.is_file():
            return custom
    size = "base"
    if config:
        size = (config.whisper_model or "small").strip().lower()
        if size not in VALID_MODELS:
            size = "small"
    preferred = WHISPER_MODELS_DIR / f"ggml-{size}.bin"
    if preferred.is_file():
        return preferred
    base = WHISPER_MODELS_DIR / "ggml-base.bin"
    if base.is_file() and size != "base":
        logger.warning(
            "Modelo ggml-%s.bin no encontrado; usando ggml-base.bin. "
            "Ejecuta .\\setup.ps1 para mejor precision.",
            size,
        )
    return preferred if preferred.is_file() else base


class WhisperEngine:
    def __init__(
        self,
        config: EchoConfig | None = None,
        cli_path: Path | None = None,
        model_path: Path | None = None,
        language: str = "es",
    ) -> None:
        self._config = config
        self._cli = cli_path or default_whisper_cli()
        self._model = model_path or resolve_model_path(config)
        self._language = language

    def update_config(self, config: EchoConfig) -> None:
        self._config = config
        self._model = resolve_model_path(config)

    @property
    def cli_path(self) -> Path:
        return self._cli

    @property
    def model_path(self) -> Path:
        return self._model

    @property
    def model_label(self) -> str:
        return self._model.name if self._model else "missing"

    def is_available(self) -> bool:
        return self._cli.is_file() and self._model.is_file()

    def _decode_options(self) -> dict[str, int | float | bool | str]:
        cfg = self._config
        if cfg is None:
            return {
                "beam_size": 8,
                "best_of": 5,
                "threads": max(4, (os.cpu_count() or 4) - 1),
                "use_prompt": True,
            }
        threads = cfg.whisper_threads
        if threads <= 0:
            threads = max(4, (os.cpu_count() or 4) - 1)
        return {
            "beam_size": max(1, min(cfg.whisper_beam_size, 16)),
            "best_of": max(1, min(cfg.whisper_best_of, 10)),
            "threads": threads,
            "use_prompt": cfg.whisper_use_prompt,
        }

    def transcribe(self, wav_path: Path) -> str:
        if not self.is_available():
            raise FileNotFoundError(
                f"Whisper not found: cli={self._cli} model={self._model}"
            )
        opts = self._decode_options()
        cmd = [
            str(self._cli),
            "-m",
            str(self._model),
            "-l",
            self._language,
            "--no-timestamps",
            "-np",
            "-nf",
            "--temperature",
            "0",
            "--beam-size",
            str(opts["beam_size"]),
            "--best-of",
            str(opts["best_of"]),
            "-t",
            str(opts["threads"]),
            "-f",
            str(wav_path),
        ]
        if opts["use_prompt"] and self._config is not None:
            prompt = build_initial_prompt(self._config)
            cmd.extend(["--prompt", prompt, "--carry-initial-prompt"])
        logger.info(
            "Whisper: model=%s beam=%s threads=%s prompt=%s",
            self.model_label,
            opts["beam_size"],
            opts["threads"],
            opts["use_prompt"],
        )
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode != 0:
            logger.warning(
                "whisper-cli exit %s: %s",
                result.returncode,
                (result.stderr or "")[:500],
            )
        text = self._parse_output(result.stdout)
        if not text and result.stderr:
            text = self._parse_output(result.stderr)
        return text.strip()

    @staticmethod
    def _parse_output(output: str) -> str:
        skip_prefixes = (
            "whisper_",
            "system_info:",
            "main:",
            "ggml_",
            "[",
        )
        lines = []
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            lower = line.lower()
            if any(line.startswith(p) for p in skip_prefixes):
                continue
            if "processing '" in lower and ".wav" in lower:
                continue
            if "n_threads" in lower and "whisper" in lower:
                continue
            line = re.sub(r"^\d{2}:\d{2}:\d{2}\.\d{3}\s+", "", line)
            lines.append(line)
        return " ".join(lines)

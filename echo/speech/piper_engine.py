"""Piper TTS CLI wrapper and playback."""

from __future__ import annotations

import subprocess
import tempfile
import wave
from pathlib import Path

from echo.system.subprocess_win import no_window_kwargs

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def default_piper_exe() -> Path:
    return PROJECT_ROOT / "models" / "piper" / "piper.exe"


def default_piper_model() -> Path:
    return (
        PROJECT_ROOT
        / "models"
        / "piper"
        / "es_ES-davefx-medium.onnx"
    )


class PiperEngine:
    def __init__(
        self,
        exe_path: Path | None = None,
        model_path: Path | None = None,
    ) -> None:
        self._exe = exe_path or default_piper_exe()
        self._model = model_path or default_piper_model()

    def is_available(self) -> bool:
        return self._exe.is_file() and self._model.is_file()

    def synthesize(self, text: str, output_path: Path | None = None) -> Path:
        if not self.is_available():
            raise FileNotFoundError(
                f"Piper not found: exe={self._exe} model={self._model}"
            )
        if output_path is None:
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            output_path = Path(tmp.name)
            tmp.close()

        cmd = [
            str(self._exe),
            "--model",
            str(self._model),
            "--output_file",
            str(output_path),
        ]
        subprocess.run(
            cmd,
            input=text,
            text=True,
            capture_output=True,
            check=True,
            **no_window_kwargs(),
        )
        return output_path

    def speak(self, text: str) -> bool:
        if not text:
            return False
        try:
            wav = self.synthesize(text)
            self.play_wav(wav)
            return True
        except Exception:
            return False

    @staticmethod
    def play_wav(path: Path) -> None:
        try:
            import winsound

            winsound.PlaySound(str(path), winsound.SND_FILENAME)
        except Exception:
            with wave.open(str(path), "rb") as wf:
                import sounddevice as sd

                data = wf.readframes(wf.getnframes())
                import numpy as np

                audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767
                sd.play(audio, wf.getframerate())
                sd.wait()

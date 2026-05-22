from pathlib import Path
from unittest.mock import patch

import pytest

from echo.speech.piper_engine import PiperEngine


@pytest.mark.unit
def test_is_available(tmp_path):
    exe = tmp_path / "piper.exe"
    model = tmp_path / "model.onnx"
    exe.write_text("")
    model.write_text("")
    assert PiperEngine(exe, model).is_available() is True


@pytest.mark.unit
@patch("subprocess.run")
def test_synthesize(mock_run, tmp_path):
    exe = tmp_path / "piper.exe"
    model = tmp_path / "model.onnx"
    exe.write_text("")
    model.write_text("")
    engine = PiperEngine(exe, model)
    out = engine.synthesize("hola", tmp_path / "out.wav")
    assert mock_run.called
    assert out == tmp_path / "out.wav"

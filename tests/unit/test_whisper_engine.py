from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from echo.config.schema import EchoConfig
from echo.speech.whisper_engine import WhisperEngine


@pytest.mark.unit
def test_is_available_false(tmp_path):
    engine = WhisperEngine(
        cli_path=tmp_path / "missing.exe",
        model_path=tmp_path / "missing.bin",
    )
    assert engine.is_available() is False


@pytest.mark.unit
def test_transcribe_parses_output(tmp_path):
    cli = tmp_path / "whisper-cli.exe"
    model = tmp_path / "ggml-base.bin"
    cli.write_text("")
    model.write_text("")
    config = EchoConfig(whisper_use_prompt=True, whisper_beam_size=8)
    engine = WhisperEngine(config=config, cli_path=cli, model_path=model)
    wav = tmp_path / "test.wav"
    wav.write_bytes(b"RIFF")

    mock_result = MagicMock()
    mock_result.stdout = "hola mundo\n"
    mock_result.stderr = ""
    mock_result.returncode = 0

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        text = engine.transcribe(wav)
        assert "hola mundo" in text
        args = mock_run.call_args[0][0]
        assert "-l" in args
        assert "es" in args
        assert "--beam-size" in args
        assert "8" in args
        assert "--prompt" in args
        assert "-nf" in args
        assert "-np" in args


@pytest.mark.unit
def test_parse_output_ignores_whisper_logs():
    raw = """system_info: n_threads = 15 / 16 | WHISPER : COREML = 0
main: processing 'test.wav' (74048 samples, 4.6 sec)
abre youtube
whisper_print_timings: total time = 100 ms"""
    text = WhisperEngine._parse_output(raw)
    assert text == "abre youtube"


@pytest.mark.unit
def test_transcribe_missing_binary(tmp_path):
    engine = WhisperEngine(
        cli_path=tmp_path / "nope.exe",
        model_path=tmp_path / "nope.bin",
    )
    with pytest.raises(FileNotFoundError):
        engine.transcribe(tmp_path / "a.wav")

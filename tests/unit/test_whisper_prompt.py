import pytest

from echo.config.schema import EchoConfig, load_default_dict
from echo.speech.whisper_prompt import build_initial_prompt


@pytest.mark.unit
def test_prompt_includes_core_commands():
    cfg = EchoConfig.from_dict(load_default_dict())
    prompt = build_initial_prompt(cfg)
    assert "quiero ver" in prompt
    assert "quiero aprender" in prompt
    assert "quiero escuchar" in prompt
    assert "sube volumen" in prompt
    assert "espanol" in prompt.lower() or "espa" in prompt.lower()


@pytest.mark.unit
def test_prompt_includes_custom_sites():
    data = load_default_dict()
    data["websites"] = {"netflix": "https://netflix.com"}
    cfg = EchoConfig.from_dict(data)
    prompt = build_initial_prompt(cfg)
    assert "abre netflix" in prompt

import pytest

from echo.commands.intents import OpenFolder, SearchWeb, SystemAdjust
from echo.commands.patterns import match_patterns
from echo.config.schema import EchoConfig, load_default_dict


@pytest.fixture
def config():
    return EchoConfig.from_dict(load_default_dict())


@pytest.mark.unit
def test_quiero_ver_returns_search(config):
    intent = match_patterns("quiero ver matrix", config)
    assert isinstance(intent, SearchWeb)
    assert intent.query == "matrix"
    assert "m.ok.ru" in intent.url.lower()
    assert "OK.ru" in intent.route_label


@pytest.mark.unit
def test_quiero_aprender_returns_search(config):
    intent = match_patterns("quiero aprender soldar", config)
    assert isinstance(intent, SearchWeb)
    assert intent.query == "soldar"
    assert "youtube.com/results" in intent.url


@pytest.mark.unit
def test_quiero_escuchar_returns_search(config):
    intent = match_patterns("quiero escuchar rock clasico", config)
    assert isinstance(intent, SearchWeb)
    assert intent.query == "rock clasico"
    assert "music.youtube.com" in intent.url


@pytest.mark.unit
def test_busca_fallback_uses_google(config):
    intent = match_patterns("busca recetas de pollo", config)
    assert isinstance(intent, SearchWeb)
    assert "google.com" in intent.url


@pytest.mark.unit
def test_open_folder(config):
    intent = match_patterns("abre descargas", config)
    assert isinstance(intent, OpenFolder)
    assert intent.folder_key == "descargas"


@pytest.mark.unit
def test_volume_up(config):
    intent = match_patterns("sube volumen", config)
    assert isinstance(intent, SystemAdjust)
    assert intent.target == "volume"
    assert intent.direction == "up"

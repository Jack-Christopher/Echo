import pytest

from echo.commands.intents import OpenFolder, OpenWebsite, SearchWeb
from echo.commands.patterns import match_patterns
from echo.config.schema import EchoConfig, load_default_dict


@pytest.fixture
def config():
    return EchoConfig.from_dict(load_default_dict())


@pytest.mark.unit
def test_open_website(config):
    intent = match_patterns("abre youtube", config)
    assert isinstance(intent, OpenWebsite)
    assert intent.alias == "youtube"


@pytest.mark.unit
def test_search(config):
    intent = match_patterns("busca recetas de pollo", config)
    assert isinstance(intent, SearchWeb)
    assert intent.query == "recetas de pollo"


@pytest.mark.unit
def test_open_folder(config):
    intent = match_patterns("abre descargas", config)
    assert isinstance(intent, OpenFolder)
    assert intent.folder_key == "descargas"

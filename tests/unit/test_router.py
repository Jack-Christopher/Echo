import pytest

from echo.commands.intents import MediaControl, OpenWebsite, SearchWeb, Unknown
from echo.commands.router import CommandRouter
from echo.config.schema import EchoConfig, load_default_dict


@pytest.fixture
def router():
    return CommandRouter(EchoConfig.from_dict(load_default_dict()))


@pytest.mark.unit
@pytest.mark.parametrize(
    "text,intent_name",
    [
        ("abre youtube", "open_website"),
        ("busca videos de carpinteria", "search_web"),
        ("pausa", "media_control"),
        ("sube volumen", "system_adjust"),
        ("abre descargas", "open_folder"),
    ],
)
def test_route_known(router, text, intent_name):
    intent = router.route(text)
    assert intent.name == intent_name


@pytest.mark.unit
def test_unknown(router):
    intent = router.route("comando inventado xyz")
    assert isinstance(intent, Unknown)


@pytest.mark.unit
def test_dictation_mode(router):
    router.config.dictation_active = True
    intent = router.route("hola mundo")
    assert intent.name == "dictation_text"
    assert intent.text == "hola mundo"

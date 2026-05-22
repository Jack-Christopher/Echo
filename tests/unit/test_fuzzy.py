import pytest

from echo.commands.fuzzy import match_fuzzy
from echo.commands.intents import OpenWebsite
from echo.config.schema import EchoConfig, load_default_dict


@pytest.mark.unit
def test_fuzzy_youtube_variant():
    config = EchoConfig.from_dict(load_default_dict())
    intent = match_fuzzy("quiero youtube", config)
    assert isinstance(intent, OpenWebsite)
    assert intent.alias == "youtube"


@pytest.mark.unit
def test_fuzzy_below_threshold():
    config = EchoConfig.from_dict(load_default_dict())
    config.fuzzy_threshold = 99
    intent = match_fuzzy("xyz abc nonsense", config)
    assert intent is None

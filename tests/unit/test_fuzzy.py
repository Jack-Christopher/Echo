import pytest

from echo.commands.fuzzy import match_fuzzy
from echo.commands.intents import SystemAdjust
from echo.config.schema import EchoConfig, load_default_dict


@pytest.mark.unit
def test_fuzzy_volume_variant():
    config = EchoConfig.from_dict(load_default_dict())
    intent = match_fuzzy("subir volumen", config)
    assert isinstance(intent, SystemAdjust)
    assert intent.target == "volume"
    assert intent.direction == "up"


@pytest.mark.unit
def test_fuzzy_below_threshold():
    config = EchoConfig.from_dict(load_default_dict())
    config.fuzzy_threshold = 99
    intent = match_fuzzy("xyz abc nonsense", config)
    assert intent is None

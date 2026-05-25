import pytest

from echo.commands.chains import parse_chain
from echo.commands.router import CommandRouter
from echo.config.schema import EchoConfig, load_default_dict


@pytest.mark.unit
def test_parse_chain_two_steps():
    config = EchoConfig.from_dict(load_default_dict())
    router = CommandRouter(config)
    intent = parse_chain("sube volumen y abre descargas", router)
    assert intent is not None
    assert intent.name == "action_chain"
    assert len(intent.steps) == 2


@pytest.mark.unit
def test_parse_chain_single_returns_none():
    config = EchoConfig.from_dict(load_default_dict())
    router = CommandRouter(config)
    assert parse_chain("sube volumen", router) is None

from unittest.mock import patch

import pytest

from echo.commands.dictation import type_text
from echo.commands.router import CommandRouter
from echo.config.schema import EchoConfig, load_default_dict


@pytest.mark.unit
@patch("echo.commands.dictation.pyautogui.write")
def test_type_text(mock_write):
    type_text("hola")
    mock_write.assert_called_once_with("hola", interval=0.01)


@pytest.mark.unit
def test_dictation_toggle_intent():
    config = EchoConfig.from_dict(load_default_dict())
    router = CommandRouter(config)
    intent = router.route("iniciar dictado")
    assert intent.name == "dictation_toggle"
    assert intent.enable is True

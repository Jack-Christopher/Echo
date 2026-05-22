from unittest.mock import patch

import pytest

from echo.automation.routines import RoutineRunner
from echo.config.schema import EchoConfig, load_default_dict


@pytest.mark.unit
@patch("echo.automation.routines.brightness.set_level")
@patch("echo.automation.routines.volume.set_level")
@patch("echo.automation.routines.brave.open_url")
def test_default_noche(mock_open, mock_vol, mock_bright):
    config = EchoConfig.from_dict(load_default_dict())
    runner = RoutineRunner(config)
    assert runner.run("noche") is True


@pytest.mark.unit
def test_custom_routine():
    config = EchoConfig.from_dict(load_default_dict())
    config.routines["test"] = [{"action": "volume", "value": 10}]
    runner = RoutineRunner(config)
    with patch("echo.automation.routines.volume.set_level") as mock:
        assert runner.run("test") is True
        mock.assert_called_with(10)

from unittest.mock import patch

import pytest

from echo.automation.routines import RoutineRunner
from echo.config.schema import EchoConfig, load_default_dict


@pytest.mark.unit
def test_unknown_routine_returns_false():
    config = EchoConfig.from_dict(load_default_dict())
    runner = RoutineRunner(config)
    assert runner.run("inexistente") is False


@pytest.mark.unit
def test_custom_routine_volume():
    config = EchoConfig.from_dict(load_default_dict())
    config.routines["test"] = [{"action": "volume", "value": 10}]
    runner = RoutineRunner(config)
    with patch("echo.automation.routines.volume.set_level") as mock:
        assert runner.run("test") is True
        mock.assert_called_with(10)


@pytest.mark.unit
def test_custom_routine_brightness():
    config = EchoConfig.from_dict(load_default_dict())
    config.routines["dim"] = [{"action": "brightness", "value": 30}]
    runner = RoutineRunner(config)
    with patch("echo.automation.routines.brightness.set_level") as mock:
        assert runner.run("dim") is True
        mock.assert_called_with(30)

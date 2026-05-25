from unittest.mock import MagicMock, patch

import pytest

from echo.app import AppState, EchoApp
from echo.config.store import ConfigStore


@pytest.mark.unit
def test_process_text_volume(config_store):
    app = EchoApp(config_store)
    with patch("echo.system.volume.adjust", return_value=True) as mock:
        result = app.process_text("sube volumen")
        assert result.success
        mock.assert_called_once()
    assert app.state == AppState.IDLE


@pytest.mark.unit
def test_process_text_quiero_ver(config_store):
    app = EchoApp(config_store)
    with patch("echo.browser.navigation.search", return_value=True) as mock:
        result = app.process_text("quiero ver matrix")
        assert result.success
        mock.assert_called_once()
    assert app.state == AppState.IDLE


@pytest.mark.unit
def test_ptt_press_release_state(config_store):
    app = EchoApp(config_store)
    capture = MagicMock()
    capture.start.return_value = True
    capture.stop_and_save.return_value = None
    app._capture = capture

    app.ptt_press()
    assert app.state == AppState.LISTENING
    app.ptt_release()
    assert app.state == AppState.IDLE


@pytest.mark.unit
def test_ptt_mic_fail(config_store):
    app = EchoApp(config_store)
    capture = MagicMock()
    capture.start.return_value = False
    app._capture = capture
    app.ptt_press()
    assert app.state == AppState.IDLE

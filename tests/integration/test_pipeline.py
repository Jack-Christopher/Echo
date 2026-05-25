from unittest.mock import patch

import pytest

from echo.app import EchoApp


@pytest.mark.integration
@patch("echo.system.volume.adjust", return_value=True)
def test_pipeline_volume(mock_adjust, config_store):
    app = EchoApp(config_store)
    result = app.process_text("sube volumen")
    assert result.success
    assert mock_adjust.called
    entries = app._history.read_recent()
    assert len(entries) >= 1
    assert entries[-1]["intent"] == "system_adjust"


@pytest.mark.integration
@patch("echo.browser.navigation.search")
def test_pipeline_quiero_ver(mock_search, config_store):
    app = EchoApp(config_store)
    result = app.process_text("quiero ver matrix")
    assert result.success
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "matrix"
    assert "m.ok.ru" in kwargs["url"].lower()


@pytest.mark.integration
@patch("echo.browser.navigation.search")
def test_pipeline_busca_fallback(mock_search, config_store):
    app = EchoApp(config_store)
    result = app.process_text("busca recetas de pollo")
    assert result.success
    mock_search.assert_called_once()

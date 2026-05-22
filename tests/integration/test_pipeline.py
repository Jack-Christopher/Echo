from unittest.mock import patch

import pytest

from echo.app import EchoApp


@pytest.mark.integration
@patch("echo.browser.brave.open_url")
def test_pipeline_open_website(mock_open, config_store):
    app = EchoApp(config_store)
    result = app.process_text("abre youtube")
    assert result.success
    assert mock_open.called
    entries = app._history.read_recent()
    assert len(entries) >= 1
    assert entries[-1]["intent"] == "open_website"


@pytest.mark.integration
@patch("echo.browser.navigation.search")
def test_pipeline_search(mock_search, config_store):
    app = EchoApp(config_store)
    result = app.process_text("busca recetas de pollo")
    assert result.success
    mock_search.assert_called_once()

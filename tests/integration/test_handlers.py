from unittest.mock import MagicMock, patch

import pytest

from echo.commands.handlers import IntentHandlers
from echo.commands.intents import (
    MediaControl,
    OpenFolder,
    OpenWebsite,
    SearchWeb,
    SystemAdjust,
    Unknown,
)
from echo.config.schema import EchoConfig, load_default_dict


@pytest.fixture
def handlers():
    return IntentHandlers(EchoConfig.from_dict(load_default_dict()))


@pytest.mark.integration
@patch("echo.commands.handlers.open_resource", return_value=True)
def test_open_website(mock_open, handlers):
    intent = OpenWebsite("youtube", "https://www.youtube.com")
    result = handlers.handle(intent)
    assert result.success
    mock_open.assert_called_once()


@pytest.mark.integration
@patch("echo.browser.navigation.search")
def test_search(mock_search, handlers):
    result = handlers.handle(SearchWeb("recetas"))
    assert result.success
    mock_search.assert_called_once()


@pytest.mark.integration
@patch("echo.system.media.send_media_key")
def test_media(mock_media, handlers):
    handlers.handle(MediaControl("pause"))
    mock_media.assert_called_with("pause")


@pytest.mark.integration
@patch("echo.system.volume.adjust")
def test_volume(mock_vol, handlers):
    handlers.handle(SystemAdjust("volume", "up"))
    mock_vol.assert_called_once()


@pytest.mark.integration
@patch("echo.system.files.open_folder")
@patch("echo.system.files.resolve_folder")
def test_folder(mock_resolve, mock_open, handlers, tmp_path):
    mock_resolve.return_value = tmp_path
    handlers.handle(OpenFolder("descargas"))
    mock_open.assert_called_once()


@pytest.mark.integration
def test_unknown(handlers):
    result = handlers.handle(Unknown("xyz"))
    assert not result.success

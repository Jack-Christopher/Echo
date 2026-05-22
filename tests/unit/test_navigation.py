from unittest.mock import patch

import pytest

from echo.browser.navigation import open_search_url, search
from echo.config.schema import EchoConfig, load_default_dict


@pytest.mark.unit
def test_open_search_url():
    config = EchoConfig.from_dict(load_default_dict())
    url = open_search_url("pollo", config)
    assert "pollo" in url


@pytest.mark.unit
@patch("echo.browser.navigation.open_resource", return_value=True)
def test_search_opens_url(mock_open):
    config = EchoConfig.from_dict(load_default_dict())
    assert search("recetas pollo", config) is True
    mock_open.assert_called_once()
    url = mock_open.call_args[0][0]
    assert "google.com" in url
    assert "pollo" in url

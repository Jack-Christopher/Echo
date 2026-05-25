import pytest

from echo.commands.search_router import resolve_search
from echo.config.schema import EchoConfig, load_default_dict


@pytest.fixture
def config():
    return EchoConfig.from_dict(load_default_dict())


@pytest.mark.unit
def test_quiero_ver_uses_site_okru(config):
    r = resolve_search("quiero ver matrix", config)
    assert "google.com" in r.url
    assert "site" in r.url.lower()
    assert "m.ok.ru" in r.url.lower()
    assert "matrix" in r.url.lower()
    assert r.route_id == "quiero_ver"


@pytest.mark.unit
def test_quiero_aprender_routes_to_youtube(config):
    r = resolve_search("quiero aprender python", config)
    assert "youtube.com/results" in r.url
    assert "python" in r.url.lower()
    assert r.route_id == "quiero_aprender"


@pytest.mark.unit
def test_quiero_escuchar_routes_to_youtube_music(config):
    r = resolve_search("quiero escuchar bad bunny", config)
    assert "music.youtube.com" in r.url
    assert "bad+bunny" in r.url.lower() or "bad%20bunny" in r.url.lower()
    assert r.route_id == "quiero_escuchar"


@pytest.mark.unit
def test_fallback_google(config):
    r = resolve_search("clima madrid manana", config)
    assert "google.com" in r.url
    assert r.route_id == "general"


@pytest.mark.unit
def test_quiero_ver_strips_trigger(config):
    r = resolve_search("quiero ver pelicula breaking bad", config)
    assert "quiero+ver" not in r.url.lower()
    assert "quiero%20ver" not in r.url.lower()
    assert "pelicula" in r.url.lower() or "breaking" in r.url.lower()

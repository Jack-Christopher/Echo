import pytest

from echo.commands.search_router import resolve_search
from echo.config.schema import EchoConfig, load_default_dict


@pytest.fixture
def config():
    return EchoConfig.from_dict(load_default_dict())


@pytest.mark.unit
def test_pelicula_uses_site_okru(config):
    r = resolve_search("pelicula matrix", config)
    assert "google.com" in r.url
    assert "site" in r.url.lower()
    assert "m.ok.ru" in r.url.lower()
    assert r.route_id == "okru_pelicula"


@pytest.mark.unit
def test_video_routes_to_youtube(config):
    r = resolve_search("tutorial python", config)
    assert "youtube.com" in r.url
    assert r.route_id == "video"


@pytest.mark.unit
def test_exact_serie_uses_site(config):
    r = resolve_search("serie breaking bad", config)
    assert "google.com" in r.url
    assert "site" in r.url.lower()
    assert "m.ok.ru" in r.url.lower()
    assert r.route_id == "okru_serie_exact"


@pytest.mark.unit
def test_cuevana_template(config):
    r = resolve_search("cuevana matrix", config)
    assert "cuevanapro.org" in r.url
    assert "matrix" in r.url
    assert r.route_id == "cuevana"


@pytest.mark.unit
def test_gemini_route(config):
    r = resolve_search("gemini recetas veganas", config)
    assert "gemini.google.com" in r.url
    assert r.route_id == "gemini"


@pytest.mark.unit
def test_fallback_google(config):
    r = resolve_search("clima madrid manana", config)
    assert "google.com" in r.url

import pytest

from echo.commands.normalizer import normalize, strip_accents


@pytest.mark.unit
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Abre YouTube", "abre youtube"),
        ("  busca   recetas  ", "busca recetas"),
        ("POR FAVOR abre gmail", "abre gmail"),
    ],
)
def test_normalize(raw, expected):
    assert normalize(raw) == expected


@pytest.mark.unit
def test_strip_accents():
    assert strip_accents("configuración") == "configuracion"

import pytest

from echo.config.schema import EchoConfig, load_default_dict
from echo.system import files


@pytest.mark.unit
def test_resolve_folder():
    config = EchoConfig.from_dict(load_default_dict())
    path = files.resolve_folder("descargas", config)
    assert path.name.lower() in ("downloads", "descargas") or "download" in str(path).lower()


@pytest.mark.unit
def test_open_folder(tmp_path):
    assert files.open_folder(tmp_path) is True

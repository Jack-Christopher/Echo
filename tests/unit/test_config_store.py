import pytest

from echo.config.schema import EchoConfig
from echo.config.store import ConfigStore


@pytest.mark.unit
def test_load_defaults_when_no_files(config_store):
    cfg = config_store.load()
    assert config_store.active_source == "defaults"
    assert cfg.hotkey == "win+space"
    assert any(r.get("id") == "quiero_ver" for r in cfg.search_routes)


@pytest.mark.unit
def test_load_appdata_config(config_store, write_appdata_config):
    write_appdata_config({"preferred_volume": 77})
    cfg = config_store.load()
    assert config_store.active_source == "appdata"
    assert cfg.preferred_volume == 77


@pytest.mark.unit
def test_fallback_to_project_when_no_appdata(config_store, temp_config_dirs, sample_config_dict):
    _, project = temp_config_dirs
    (project / "config.json").write_text(
        '{"preferred_volume": 42, "websites": {}}', encoding="utf-8"
    )
    cfg = config_store.load()
    assert config_store.active_source == "project"
    assert cfg.preferred_volume == 42


@pytest.mark.unit
def test_save_to_appdata(config_store, temp_config_dirs):
    appdata, _ = temp_config_dirs
    cfg = config_store.load()
    cfg.preferred_volume = 60
    path = config_store.save(cfg)
    assert path == appdata / "config.json"
    reloaded = ConfigStore(
        appdata_path=appdata / "config.json",
        project_path=temp_config_dirs[1] / "config.json",
    ).load()
    assert reloaded.preferred_volume == 60


@pytest.mark.unit
def test_mirror_subset_on_appdata_save(config_store, temp_config_dirs):
    appdata, project = temp_config_dirs
    cfg = config_store.load()
    cfg.websites["test"] = "https://example.com"
    config_store.save(cfg)
    assert (project / "config.json").is_file()


@pytest.mark.unit
def test_validate_rejects_bad_threshold(default_config):
    default_config.fuzzy_threshold = 150
    with pytest.raises(ValueError):
        default_config.validate()

"""Shared pytest fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from echo.config.schema import EchoConfig, load_default_dict
from echo.config.store import ConfigStore


@pytest.fixture
def default_config() -> EchoConfig:
    return EchoConfig.from_dict(load_default_dict())


@pytest.fixture
def temp_config_dirs(tmp_path, monkeypatch):
    appdata = tmp_path / "appdata" / "Echo"
    project = tmp_path / "project"
    project.mkdir()
    appdata.mkdir(parents=True)
    monkeypatch.setattr(
        "echo.config.store.appdata_config_path",
        lambda: appdata / "config.json",
    )
    monkeypatch.setattr(
        "echo.config.store.project_config_path",
        lambda: project / "config.json",
    )
    monkeypatch.setattr(
        "echo.config.store.appdata_dir",
        lambda: appdata,
    )
    monkeypatch.setattr(
        "echo.logs.history.default_log_path",
        lambda: appdata / "logs" / "history.jsonl",
    )
    return appdata, project


@pytest.fixture
def config_store(temp_config_dirs) -> ConfigStore:
    appdata, project = temp_config_dirs
    return ConfigStore(
        appdata_path=appdata / "config.json",
        project_path=project / "config.json",
    )


@pytest.fixture
def sample_config_dict():
    return load_default_dict()


@pytest.fixture
def write_appdata_config(temp_config_dirs, sample_config_dict):
    appdata, _ = temp_config_dirs
    path = appdata / "config.json"

    def _write(overrides=None):
        data = {**sample_config_dict, **(overrides or {})}
        path.write_text(json.dumps(data), encoding="utf-8")
        return data

    return _write

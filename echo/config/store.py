"""Dual-path configuration: AppData primary, project fallback + mirror."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Literal

from echo.config.schema import EchoConfig, load_default_dict

ConfigSource = Literal["appdata", "project", "defaults"]


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def appdata_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA", "")
    if base:
        return Path(base) / "Echo"
    return _project_root() / ".echo_appdata"


def appdata_config_path() -> Path:
    return appdata_dir() / "config.json"


def project_config_path() -> Path:
    return _project_root() / "config.json"


def defaults_path() -> Path:
    return Path(__file__).resolve().parent / "defaults.json"


class ConfigStore:
    def __init__(
        self,
        appdata_path: Path | None = None,
        project_path: Path | None = None,
    ) -> None:
        self._appdata_path = appdata_path or appdata_config_path()
        self._project_path = project_path or project_config_path()
        self._active_source: ConfigSource = "defaults"
        self._config = EchoConfig.from_dict(load_default_dict())

    @property
    def active_source(self) -> ConfigSource:
        return self._active_source

    @property
    def active_path(self) -> Path | None:
        if self._active_source == "appdata":
            return self._appdata_path
        if self._active_source == "project":
            return self._project_path
        return None

    @property
    def config(self) -> EchoConfig:
        return self._config

    def load(self) -> EchoConfig:
        appdata_cfg = self._try_load_appdata()
        if appdata_cfg is not None:
            self._config = appdata_cfg
            self._active_source = "appdata"
            self._config.validate()
            return self._config

        project_cfg = self._try_load_project()
        if project_cfg is not None:
            self._config = project_cfg
            self._active_source = "project"
            self._config.validate()
            return self._config

        self._config = EchoConfig.from_dict(load_default_dict())
        self._active_source = "defaults"
        self._seed_appdata_if_possible()
        self._config.validate()
        return self._config

    def save(self, config: EchoConfig | None = None) -> Path:
        if config is not None:
            self._config = config
        self._config.validate()
        data = self._config.to_dict()

        if self._try_save(self._appdata_path, data):
            self._active_source = "appdata"
            self._mirror_to_project()
            return self._appdata_path

        if self._try_save(self._project_path, data):
            self._active_source = "project"
            return self._project_path

        raise OSError("Could not write config to AppData or project path")

    def _try_load_appdata(self) -> EchoConfig | None:
        return self._read_config_file(self._appdata_path)

    def _try_load_project(self) -> EchoConfig | None:
        return self._read_config_file(self._project_path)

    def _read_config_file(self, path: Path) -> EchoConfig | None:
        if not path.is_file():
            return None
        try:
            with open(path, encoding="utf-8") as f:
                return EchoConfig.from_dict(json.load(f))
        except (json.JSONDecodeError, OSError, ValueError):
            return None

    def _seed_appdata_if_possible(self) -> None:
        if self._appdata_path.is_file():
            return
        defaults = load_default_dict()
        self._try_save(self._appdata_path, defaults)

    def _try_save(self, path: Path, data: dict) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            tmp.replace(path)
            return True
        except OSError:
            return False

    def _mirror_to_project(self) -> None:
        try:
            subset = self._config.mirror_subset()
            existing: dict = {}
            if self._project_path.is_file():
                with open(self._project_path, encoding="utf-8") as f:
                    existing = json.load(f)
            existing.update(subset)
            self._try_save(self._project_path, {**load_default_dict(), **existing})
        except OSError:
            pass

    def reset_to_defaults(self) -> EchoConfig:
        self._config = EchoConfig.from_dict(load_default_dict())
        self.save()
        return self._config

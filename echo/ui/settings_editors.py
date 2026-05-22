"""Human-friendly list editors for Echo settings."""

from __future__ import annotations

import re
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from echo.config.resources import normalize_website_entry, website_url


def _slug_id(label: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "_", label.lower().strip())
    return base.strip("_") or "regla"


def _terms_to_text(terms: list[Any]) -> str:
    return ", ".join(str(t) for t in (terms or []))


def _text_to_terms(text: str) -> list[str]:
    return [p.strip() for p in text.split(",") if p.strip()]


class SearchRouteEditor(QWidget):
    """Edit search route rules (custom sites or general routes)."""

    def __init__(self, title: str, *, allow_fallback: bool = True, parent=None) -> None:
        super().__init__(parent)
        self._allow_fallback = allow_fallback
        self._rules: list[dict[str, Any]] = []
        self._build_ui(title)

    def _build_ui(self, title: str) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>{title}</b>"))

        body = QHBoxLayout()
        self._list = QListWidget()
        self._list.currentRowChanged.connect(self._on_select)
        body.addWidget(self._list, 1)

        form_box = QGroupBox("Detalle")
        form = QFormLayout(form_box)
        self._label = QLineEdit()
        form.addRow("Nombre:", self._label)
        self._terms = QLineEdit()
        self._terms.setPlaceholderText("pelicula, peli, film (separadas por coma)")
        form.addRow("Palabras clave:", self._terms)
        self._match = QComboBox()
        for key, lbl in (
            ("leading", "Empieza por (busca pelicula ...)"),
            ("exact", "Frase exacta"),
            ("contains", "Contiene la palabra"),
            ("fallback", "Si nada mas coincide"),
        ):
            if key == "fallback" and not self._allow_fallback:
                continue
            self._match.addItem(lbl, key)
        form.addRow("Cuando digas:", self._match)
        self._mode = QComboBox()
        self._mode.addItem("Buscar en Google con site:dominio", "site")
        self._mode.addItem("Abrir URL directa", "template")
        self._mode.currentIndexChanged.connect(self._update_mode_fields)
        form.addRow("Como buscar:", self._mode)
        self._site_domain = QLineEdit()
        self._site_domain.setPlaceholderText("m.ok.ru")
        form.addRow("Dominio site:", self._site_domain)
        self._template = QLineEdit()
        self._template.setPlaceholderText("https://ejemplo.com/search?q={query}")
        form.addRow("URL:", self._template)
        self._priority = QSpinBox()
        self._priority.setRange(0, 999)
        self._strip = QCheckBox("Quitar palabra clave del texto buscado")
        self._strip.setChecked(True)
        form.addRow("Prioridad:", self._priority)
        form.addRow("", self._strip)
        body.addWidget(form_box, 2)
        layout.addLayout(body)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("+ Agregar")
        add_btn.clicked.connect(self._add_rule)
        del_btn = QPushButton("Eliminar")
        del_btn.clicked.connect(self._delete_rule)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._form_fields = (
            self._label,
            self._terms,
            self._match,
            self._mode,
            self._site_domain,
            self._template,
            self._priority,
            self._strip,
        )
        self._set_form_enabled(False)

    def _set_form_enabled(self, on: bool) -> None:
        for w in self._form_fields:
            w.setEnabled(on)

    def _update_mode_fields(self) -> None:
        is_site = self._mode.currentData() == "site"
        self._site_domain.setEnabled(is_site)
        self._template.setEnabled(not is_site)

    def _display_text(self, rule: dict[str, Any]) -> str:
        label = rule.get("label") or rule.get("id", "Regla")
        terms = _terms_to_text(rule.get("terms") or [])
        if str(rule.get("match")) == "fallback":
            return f"{label} · (por defecto)"
        mode = rule.get("resolve_mode", "template")
        dest = (
            f"site:{rule.get('site_domain', '')}"
            if mode == "site"
            else (rule.get("template") or "")[:40]
        )
        return f"{label} · {terms or '—'} · {dest}"

    def load_rules(self, rules: list[dict[str, Any]]) -> None:
        self._rules = [dict(r) for r in rules]
        self._refresh_list()
        if self._rules:
            self._list.setCurrentRow(0)

    def get_rules(self) -> list[dict[str, Any]]:
        row = self._list.currentRow()
        if row >= 0:
            self._apply_form_to_row(row)
        return [dict(r) for r in self._rules]

    def _refresh_list(self) -> None:
        self._list.blockSignals(True)
        self._list.clear()
        for rule in self._rules:
            item = QListWidgetItem(self._display_text(rule))
            self._list.addItem(item)
        self._list.blockSignals(False)

    def _on_select(self, row: int) -> None:
        if row < 0:
            self._set_form_enabled(False)
            return
        self._set_form_enabled(True)
        rule = self._rules[row]
        self._label.setText(str(rule.get("label", "")))
        self._terms.setText(_terms_to_text(rule.get("terms") or []))
        idx = self._match.findData(str(rule.get("match", "leading")))
        self._match.setCurrentIndex(idx if idx >= 0 else 0)
        mode = str(rule.get("resolve_mode", "template"))
        midx = self._mode.findData(mode)
        self._mode.setCurrentIndex(midx if midx >= 0 else 0)
        self._site_domain.setText(str(rule.get("site_domain", "")))
        self._template.setText(str(rule.get("template", "")))
        self._priority.setValue(int(rule.get("priority", 100)))
        self._strip.setChecked(bool(rule.get("strip_terms", True)))
        self._update_mode_fields()

    def _apply_form_to_row(self, row: int) -> None:
        if row < 0 or row >= len(self._rules):
            return
        label = self._label.text().strip() or "Sin nombre"
        rule = self._rules[row]
        rule["label"] = label
        rule["id"] = rule.get("id") or _slug_id(label)
        rule["terms"] = _text_to_terms(self._terms.text())
        rule["match"] = self._match.currentData() or "leading"
        rule["resolve_mode"] = self._mode.currentData() or "template"
        rule["site_domain"] = self._site_domain.text().strip()
        rule["template"] = self._template.text().strip()
        rule["priority"] = self._priority.value()
        rule["strip_terms"] = self._strip.isChecked()
        item = self._list.item(row)
        if item:
            item.setText(self._display_text(rule))

    def _add_rule(self) -> None:
        row = self._list.currentRow()
        if row >= 0:
            self._apply_form_to_row(row)
        new_rule = {
            "id": "nueva_regla",
            "label": "Nueva regla",
            "match": "leading",
            "priority": 100,
            "terms": [],
            "strip_terms": True,
            "resolve_mode": "site",
            "site_domain": "",
            "template": "",
        }
        self._rules.append(new_rule)
        self._refresh_list()
        self._list.setCurrentRow(len(self._rules) - 1)

    def _delete_rule(self) -> None:
        row = self._list.currentRow()
        if row < 0:
            return
        if str(self._rules[row].get("match")) == "fallback":
            QMessageBox.warning(
                self,
                "Echo",
                "No elimines la regla de busqueda general (fallback).",
            )
            return
        del self._rules[row]
        self._refresh_list()
        if self._rules:
            self._list.setCurrentRow(min(row, len(self._rules) - 1))


class WebsiteEditor(QWidget):
    """Edit website shortcuts (abre youtube)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._sites: dict[str, dict[str, str]] = {}
        self._keys: list[str] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel("<b>Sitios para abrir</b> — di «abre youtube», «abre gemini», etc.")
        )

        body = QHBoxLayout()
        self._list = QListWidget()
        self._list.currentRowChanged.connect(self._on_select)
        body.addWidget(self._list, 1)

        form_box = QGroupBox("Detalle")
        form = QFormLayout(form_box)
        self._alias = QLineEdit()
        self._alias.setPlaceholderText("youtube")
        form.addRow("Nombre (voz):", self._alias)
        self._url = QLineEdit()
        self._url.setPlaceholderText("https://www.youtube.com")
        form.addRow("Enlace:", self._url)
        self._opener = QComboBox()
        self._opener.addItem("Navegador", "browser")
        self._opener.addItem("Programa de Windows", "shell")
        self._opener.addItem("Otro programa (.exe)", "custom")
        form.addRow("Abrir con:", self._opener)
        self._app_path = QLineEdit()
        self._app_path.setPlaceholderText("Solo si «Otro programa»")
        form.addRow("Ruta .exe:", self._app_path)
        body.addWidget(form_box, 2)
        layout.addLayout(body)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("+ Agregar sitio")
        add_btn.clicked.connect(self._add_site)
        del_btn = QPushButton("Eliminar")
        del_btn.clicked.connect(self._delete_site)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._form_fields = (self._alias, self._url, self._opener, self._app_path)
        self._set_form_enabled(False)

    def _set_form_enabled(self, on: bool) -> None:
        for w in self._form_fields:
            w.setEnabled(on)

    def load_sites(self, sites: dict[str, Any]) -> None:
        self._sites = {}
        self._keys: list[str] = []
        for key, val in sites.items():
            entry = normalize_website_entry(val)
            self._sites[key] = entry
            self._keys.append(key)
        self._refresh_list()
        if self._keys:
            self._list.setCurrentRow(0)

    def get_sites(self) -> dict[str, dict[str, str]]:
        row = self._list.currentRow()
        if row >= 0:
            self._apply_form_to_row(row)
        out: dict[str, dict[str, str]] = {}
        for key in self._keys:
            entry = self._sites[key]
            payload: dict[str, str] = {
                "url": entry.get("url", ""),
                "opener": entry.get("opener", "browser"),
            }
            if entry.get("app"):
                payload["app"] = entry["app"]
            out[key] = payload
        return out

    def _refresh_list(self) -> None:
        self._list.clear()
        for key in self._keys:
            entry = self._sites[key]
            url = website_url(entry)[:50]
            self._list.addItem(QListWidgetItem(f"{key} · {url}"))

    def _on_select(self, row: int) -> None:
        if row < 0 or row >= len(self._keys):
            self._set_form_enabled(False)
            return
        self._set_form_enabled(True)
        key = self._keys[row]
        entry = self._sites[key]
        self._alias.setText(key)
        self._url.setText(website_url(entry))
        idx = self._opener.findData(entry.get("opener", "browser"))
        self._opener.setCurrentIndex(idx if idx >= 0 else 0)
        self._app_path.setText(entry.get("app", ""))

    def _apply_form_to_row(self, row: int) -> None:
        if row < 0 or row >= len(self._keys):
            return
        old_key = self._keys[row]
        new_key = self._alias.text().strip().lower().replace(" ", "_") or old_key
        entry = {
            "url": self._url.text().strip(),
            "opener": self._opener.currentData() or "browser",
            "app": self._app_path.text().strip(),
        }
        if old_key != new_key:
            del self._sites[old_key]
            self._keys[row] = new_key
        self._sites[new_key] = entry
        self._refresh_list()
        self._list.setCurrentRow(row)

    def _add_site(self) -> None:
        row = self._list.currentRow()
        if row >= 0:
            self._apply_form_to_row(row)
        key = "nuevo"
        n = 1
        while key in self._sites:
            key = f"nuevo{n}"
            n += 1
        self._sites[key] = {"url": "https://", "opener": "browser", "app": ""}
        self._keys.append(key)
        self._refresh_list()
        self._list.setCurrentRow(len(self._keys) - 1)

    def _delete_site(self) -> None:
        row = self._list.currentRow()
        if row < 0:
            return
        key = self._keys[row]
        del self._sites[key]
        del self._keys[row]
        self._refresh_list()
        if self._keys:
            self._list.setCurrentRow(min(row, len(self._keys) - 1))

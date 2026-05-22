"""Settings window with human-friendly editors."""

from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from echo.browser.control import BROWSER_SPECS, normalize_browser_id
from echo.config.schema import EchoConfig
from echo.config.store import ConfigStore
from echo.logs.history import HistoryLog, format_entry_line
from echo.speech.whisper_models import download_whisper_model, is_model_installed
from echo.ui.settings_editors import SearchRouteEditor, WebsiteEditor


class _ModelDownloadWorker(QThread):
    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, model_id: str) -> None:
        super().__init__()
        self._model_id = model_id

    def run(self) -> None:
        ok, msg = download_whisper_model(
            self._model_id,
            on_progress=lambda m: self.progress.emit(m),
        )
        self.finished.emit(ok, msg)


class SettingsWindow(QDialog):
    saved = Signal(object)
    whisper_ready = Signal(object)

    def __init__(self, store: ConfigStore, parent=None) -> None:
        super().__init__(parent)
        self._store = store
        self._config = store.config
        self.setWindowTitle("Echo - Configuracion")
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint
        )
        self.setMinimumSize(640, 480)
        self.resize(780, 560)
        self._download_worker: _ModelDownloadWorker | None = None
        self._build_ui()
        self._load_values()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        general = QWidget()
        form = QFormLayout(general)
        self._hotkey = QLineEdit()
        form.addRow("Tecla push-to-talk:", self._hotkey)
        self._threshold = QSpinBox()
        self._threshold.setRange(0, 100)
        form.addRow("Tolerancia a errores de voz (%):", self._threshold)
        self._volume = QSpinBox()
        self._volume.setRange(0, 100)
        form.addRow("Volumen preferido:", self._volume)
        self._browser = QComboBox()
        for bid in BROWSER_SPECS:
            self._browser.addItem(BROWSER_SPECS[bid].label, bid)
        form.addRow("Navegador:", self._browser)
        self._browser_path = QLineEdit()
        self._browser_path.setPlaceholderText("Opcional si no se detecta solo")
        form.addRow("Ruta al navegador:", self._browser_path)
        self._search_engine = QLineEdit()
        self._search_engine.setPlaceholderText("https://www.google.com/search?q={query}")
        form.addRow("Motor busqueda (site:):", self._search_engine)
        self._path_label = QLabel()
        self._path_label.setWordWrap(True)
        form.addRow("Archivo config:", self._path_label)
        tabs.addTab(general, "General")

        voice = QWidget()
        voice_form = QFormLayout(voice)
        self._whisper_model = QComboBox()
        for mid, label in (
            ("small", "Small — recomendado"),
            ("base", "Base — mas rapido, menos preciso"),
            ("medium", "Medium — muy preciso, pesado"),
        ):
            self._whisper_model.addItem(label, mid)
        voice_form.addRow("Modelo de voz:", self._whisper_model)
        self._whisper_beam = QSpinBox()
        self._whisper_beam.setRange(1, 16)
        voice_form.addRow("Precision (beam):", self._whisper_beam)
        self._whisper_prompt = QComboBox()
        self._whisper_prompt.addItem("Si — reconoce mejor los comandos", True)
        self._whisper_prompt.addItem("No", False)
        voice_form.addRow("Pista de comandos:", self._whisper_prompt)
        self._voice_status = QLabel(
            "Al guardar se descarga el modelo si falta."
        )
        self._voice_status.setWordWrap(True)
        voice_form.addRow(self._voice_status)
        tabs.addTab(voice, "Voz")

        self._website_editor = WebsiteEditor()
        tabs.addTab(self._website_editor, "Sitios")

        routes = QWidget()
        routes_layout = QVBoxLayout(routes)
        routes_layout.addWidget(
            QLabel(
                "Define que pasa cuando dices «busca ...». "
                "OK.ru usa site:m.ok.ru en Google; Cuevana usa URL directa."
            )
        )
        self._custom_editor = SearchRouteEditor(
            "Peliculas, series, Cuevana y sitios custom",
            allow_fallback=False,
        )
        routes_layout.addWidget(self._custom_editor)
        self._routes_editor = SearchRouteEditor(
            "Otras busquedas (YouTube, recetas, Gemini...)",
            allow_fallback=True,
        )
        routes_layout.addWidget(self._routes_editor)
        tabs.addTab(routes, "Busquedas")

        history = QWidget()
        hist_layout = QVBoxLayout(history)
        self._history_view = QTextEdit()
        self._history_view.setReadOnly(True)
        hist_layout.addWidget(
            QLabel("Ultimos comandos (texto → intent → resultado):")
        )
        hist_layout.addWidget(self._history_view)
        tabs.addTab(history, "Historial")

        layout.addWidget(tabs)

        buttons = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("Cerrar")
        cancel_btn.clicked.connect(self.close)
        buttons.addStretch()
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def _load_values(self) -> None:
        c = self._config
        self._hotkey.setText(c.hotkey)
        self._threshold.setValue(c.fuzzy_threshold)
        self._volume.setValue(c.preferred_volume)
        browser_id = normalize_browser_id(c.browser)
        idx = self._browser.findData(browser_id)
        self._browser.setCurrentIndex(idx if idx >= 0 else 0)
        self._browser_path.setText(c.browser_path or c.brave_path)
        self._search_engine.setText(c.search_engine_template)
        src = self._store.active_source
        path = self._store.active_path
        self._path_label.setText(f"{src}\n{path or '(valores por defecto)'}")
        widx = self._whisper_model.findData(c.whisper_model)
        self._whisper_model.setCurrentIndex(widx if widx >= 0 else 0)
        self._whisper_beam.setValue(c.whisper_beam_size)
        pidx = self._whisper_prompt.findData(c.whisper_use_prompt)
        self._whisper_prompt.setCurrentIndex(pidx if pidx >= 0 else 0)
        model_id = c.whisper_model or "small"
        if is_model_installed(model_id):
            self._voice_status.setText(f"Modelo instalado: ggml-{model_id}.bin")
        else:
            self._voice_status.setText(
                f"Falta ggml-{model_id}.bin — pulsa Guardar para descargarlo."
            )
        self._website_editor.load_sites(c.websites)
        self._custom_editor.load_rules(c.custom_site_searches)
        self._routes_editor.load_rules(c.search_routes)
        entries = HistoryLog().read_recent(50)
        lines = [format_entry_line(e) for e in entries]
        self._history_view.setPlainText("\n".join(lines) if lines else "(sin historial)")

    def _save(self) -> None:
        self._config.hotkey = self._hotkey.text().strip() or "win+space"
        self._config.fuzzy_threshold = self._threshold.value()
        self._config.preferred_volume = self._volume.value()
        self._config.browser = self._browser.currentData() or "brave"
        exe_path = self._browser_path.text().strip()
        self._config.browser_path = exe_path
        self._config.brave_path = exe_path
        self._config.search_engine_template = (
            self._search_engine.text().strip()
            or "https://www.google.com/search?q={query}"
        )
        self._config.whisper_model = self._whisper_model.currentData() or "small"
        self._config.whisper_beam_size = self._whisper_beam.value()
        self._config.whisper_use_prompt = bool(self._whisper_prompt.currentData())
        self._config.websites = self._website_editor.get_sites()
        self._config.custom_site_searches = self._custom_editor.get_rules()
        self._config.search_routes = self._routes_editor.get_rules()
        self._store.save(self._config)
        self.saved.emit(self._config)

        model_id = self._config.whisper_model or "small"
        if is_model_installed(model_id):
            self._load_values()
            QMessageBox.information(self, "Echo", "Configuracion guardada.")
            return

        self._start_model_download(model_id)

    def _start_model_download(self, model_id: str) -> None:
        if self._download_worker and self._download_worker.isRunning():
            return
        self._voice_status.setText(f"Descargando ggml-{model_id}.bin...")
        for btn in self.findChildren(QPushButton):
            if btn.text() == "Guardar":
                btn.setEnabled(False)

        self._download_worker = _ModelDownloadWorker(model_id)
        self._download_worker.progress.connect(self._voice_status.setText)
        self._download_worker.finished.connect(self._on_download_finished)
        self._download_worker.start()

    def _on_download_finished(self, ok: bool, msg: str) -> None:
        for btn in self.findChildren(QPushButton):
            if btn.text() == "Guardar":
                btn.setEnabled(True)
        if ok:
            self._voice_status.setText(f"Modelo listo: {msg}")
            self.whisper_ready.emit(self._config)
            QMessageBox.information(
                self,
                "Echo",
                "Configuracion guardada y modelo de voz instalado.",
            )
        else:
            self._voice_status.setText(msg)
            QMessageBox.warning(self, "Echo", msg)
        self._load_values()

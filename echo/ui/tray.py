"""System tray icon and menu."""

from __future__ import annotations

from typing import Callable

from PySide6.QtGui import QAction, QCursor, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from echo.ui.icons import create_tray_icon


class SystemTray(QSystemTrayIcon):
    def __init__(
        self,
        parent=None,
        icon: QIcon | None = None,
        on_toggle: Callable[[], None] | None = None,
        on_show: Callable[[], None] | None = None,
        on_settings: Callable[[], None] | None = None,
        on_exit: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_toggle = on_toggle or on_show
        self._on_show = on_show
        self._on_settings = on_settings
        self._on_exit = on_exit
        tray_icon = icon if icon is not None and not icon.isNull() else create_tray_icon()
        self.setIcon(tray_icon)
        self._build_menu()
        self.activated.connect(self._on_activated)

    def _build_menu(self) -> None:
        self._menu = QMenu()
        self._show_action = QAction("Mostrar/Ocultar", self._menu)
        self._show_action.triggered.connect(self._handle_toggle)
        self._menu.addAction(self._show_action)

        self._settings_action = QAction("Configuracion", self._menu)
        self._settings_action.triggered.connect(self._handle_settings)
        self._menu.addAction(self._settings_action)

        self._menu.addSeparator()
        self._exit_action = QAction("Salir", self._menu)
        self._exit_action.triggered.connect(self._handle_exit)
        self._menu.addAction(self._exit_action)

        self.setContextMenu(self._menu)
        self.setToolTip("Echo Asistente — clic derecho o en el círculo azul")

    def show_context_menu(self) -> None:
        """Show tray menu at cursor (Windows often ignores setContextMenu alone)."""
        self._menu.popup(QCursor.pos())

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Context:
            self.show_context_menu()
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._handle_toggle()

    def _handle_toggle(self) -> None:
        if self._on_toggle:
            self._on_toggle()

    def _handle_show(self) -> None:
        if self._on_show:
            self._on_show()
        elif self._on_toggle:
            self._on_toggle()

    def _handle_settings(self) -> None:
        if self._on_settings:
            self._on_settings()

    def _handle_exit(self) -> None:
        if self._on_exit:
            self._on_exit()

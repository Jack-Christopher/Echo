"""Echo entry point."""

from __future__ import annotations

import logging
import sys


def _configure_windows_dpi() -> None:
    """Set DPI awareness before Qt loads (reduces access-denied warnings on Windows)."""
    if sys.platform != "win32":
        return
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "windows:dpiawareness=1")
    try:
        import ctypes

        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def _configure_stdio_encoding() -> None:
    """Avoid UnicodeEncodeError when stdout uses cp1252 (Task Scheduler / log redirect)."""
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            try:
                stream.reconfigure(errors="replace")
            except Exception:
                pass


_configure_windows_dpi()
_configure_stdio_encoding()

from PySide6.QtWidgets import QApplication

from echo.app import EchoApp
from echo.speech.audio_devices import log_audio_devices
from echo.ui.floating_widget import AssistantState, FloatingWidget
from echo.ui.icons import create_tray_icon
from echo.ui.settings_window import SettingsWindow
from echo.ui.tray import SystemTray

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main() -> int:
    print("[Echo] Iniciando asistente de voz...")
    log_audio_devices()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app_icon = create_tray_icon()
    app.setWindowIcon(app_icon)

    echo = EchoApp()
    widget = FloatingWidget()
    settings = SettingsWindow(echo.store)

    hotkey = echo.config.hotkey
    print(f"[Echo] Push-to-talk: {hotkey}  |  o mantén pulsado el círculo azul")
    if echo._whisper.is_available():
        print(f"[Echo] Whisper: OK ({echo._whisper.model_label})")
    else:
        print("[Echo] Whisper: NO (ejecuta setup.ps1; recomendado ggml-small.bin)")
    print("[Echo] Piper:", "OK" if echo._piper.is_available() else "NO (falta models/piper)")
    print("[Echo] La transcripcion sale aqui: [Echo] Texto entendido: \"...\"")
    print("[Echo] Lista de frases: COMANDOS.md")
    print()

    def sync_state(name: str) -> None:
        widget.set_state(AssistantState(name))

    echo.state_changed.connect(sync_state)

    widget.ptt_pressed.connect(echo.ptt_press)
    widget.ptt_released.connect(echo.ptt_release)

    def toggle_widget() -> None:
        if widget.isVisible():
            widget.hide()
        else:
            widget.place_bottom_right()
            widget.show()
            widget.raise_()

    def show_settings() -> None:
        echo.reload_config()
        settings._load_values()
        settings.show()

    def on_settings_saved(_cfg) -> None:
        echo.reload_config()
        if echo._hotkey:
            echo._hotkey.unregister()
        echo.setup_hotkey()
        echo.start_hotkey_listener()
        print(f"[Echo] Hotkey actualizado: {echo.config.hotkey}")
        print(
            f"[Echo] Whisper activo: {echo._whisper.model_label} "
            f"({'OK' if echo._whisper.is_available() else 'modelo pendiente'})"
        )

    settings.saved.connect(on_settings_saved)
    settings.whisper_ready.connect(on_settings_saved)

    tray = SystemTray(
        icon=app_icon,
        on_toggle=toggle_widget,
        on_settings=show_settings,
        on_exit=app.quit,
    )
    tray.show()
    widget.menu_requested.connect(tray.show_context_menu)

    if echo.setup_hotkey():
        echo.start_hotkey_listener()

    widget.place_bottom_right()
    widget.show()
    sync_state("idle")

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

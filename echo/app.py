"""Echo application orchestrator and state machine."""

from __future__ import annotations

import logging
import threading
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from echo.commands.chains import parse_chain
from echo.commands.handlers import HandlerResult, IntentHandlers
from echo.commands.normalizer import normalize
from echo.commands.router import CommandRouter
from echo.config.store import ConfigStore
from echo.logs.history import HistoryLog
from echo.speech.capture import AudioCapture
from echo.speech.hotkey import PushToTalkHotkey
from echo.speech.piper_engine import PiperEngine
from echo.speech.whisper_engine import WhisperEngine
from echo.ui.beep import play_soft_beep

logger = logging.getLogger(__name__)


class AppState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


class EchoApp(QObject):
    state_changed = Signal(str)
    message = Signal(str)

    def __init__(self, store: ConfigStore | None = None) -> None:
        super().__init__()
        self._store = store or ConfigStore()
        self._config = self._store.load()
        self._router = CommandRouter(self._config)
        self._handlers = IntentHandlers(self._config)
        self._handlers.set_dictation_callback(self._on_dictation_change)
        self._history = HistoryLog()
        self._capture = AudioCapture()
        self._whisper = WhisperEngine(config=self._config)
        self._piper = PiperEngine()
        self._hotkey: PushToTalkHotkey | None = None
        self._state = AppState.IDLE
        self._ptt_active = False
        self._ptt_lock = threading.Lock()
        self._worker: threading.Thread | None = None

    @property
    def config(self):
        return self._config

    @property
    def store(self) -> ConfigStore:
        return self._store

    @property
    def state(self) -> AppState:
        return self._state

    def reload_config(self) -> None:
        self._config = self._store.load()
        self._router.update_config(self._config)
        self._handlers.update_config(self._config)
        self._whisper.update_config(self._config)

    def _set_state(self, state: AppState) -> None:
        self._state = state
        self.state_changed.emit(state.value)

    def _notify(self, text: str) -> None:
        if text:
            print(f"[Echo] {text}")
            self.message.emit(text)

    def setup_hotkey(self) -> bool:
        self._hotkey = PushToTalkHotkey(
            hotkey=self._config.hotkey,
            on_press=self.ptt_press,
            on_release=self.ptt_release,
        )
        return self._hotkey.register()

    def start_hotkey_listener(self) -> None:
        if self._hotkey:
            self._hotkey.start_listener()

    def shutdown(self) -> None:
        if self._hotkey:
            self._hotkey.unregister()

    def ptt_press(self) -> None:
        """Start listening (hotkey or mouse hold on orb)."""
        with self._ptt_lock:
            if self._ptt_active:
                return
            self._ptt_active = True
            if not self._capture.start():
                self._ptt_active = False
                self._notify(
                    "No se pudo abrir el microfono. Revisa permisos y dispositivos arriba."
                )
                return
            self._set_state(AppState.LISTENING)
            print("[Echo] Escuchando... (mantén pulsado y habla)")

    def ptt_release(self) -> None:
        """Stop listening and process audio."""
        with self._ptt_lock:
            if not self._ptt_active:
                return
            self._ptt_active = False
            self._set_state(AppState.PROCESSING)
            print("[Echo] Procesando audio...")

        wav = self._capture.stop_and_save()
        if wav is None:
            self._notify(
                "Audio muy corto o vacio. Mantén Win+Espacio o el boton mas tiempo (min ~0.3 s)."
            )
            self._set_state(AppState.IDLE)
            return

        self._worker = threading.Thread(
            target=self._process_audio,
            args=(wav,),
            daemon=True,
        )
        self._worker.start()

    def _on_dictation_change(self, enabled: bool) -> None:
        self._config.dictation_active = enabled
        self._store.save(self._config)

    def process_text(self, text: str) -> HandlerResult:
        print(f'[Echo] Comando normalizado: "{normalize(text)}"')
        chain = parse_chain(text, self._router)
        intent = chain if chain else self._router.route(text)
        print(f"[Echo] Intent: {intent.name}", flush=True)
        if intent.name == "search_web" and getattr(intent, "route_label", ""):
            print(f"[Echo] Ruta: {intent.route_label} -> {getattr(intent, 'url', '')}", flush=True)
        result = self._handlers.handle(intent)
        self._history.append(
            raw_text=text,
            intent_name=intent.name,
            success=result.success,
            message=result.message,
        )
        if result.message:
            print(
                f"[Echo] Resultado: {result.message} ({'ok' if result.success else 'fallo'})",
                flush=True,
            )
        if intent.name == "unknown" and not result.success:
            play_soft_beep()
        if result.speak and result.message and self._config.voice_confirmations:
            if self._piper.is_available():
                self._set_state(AppState.SPEAKING)
                self._piper.speak(result.message)
        self._set_state(AppState.IDLE)
        self.message.emit(result.message)
        return result

    def _process_audio(self, wav: Path) -> None:
        try:
            if not self._whisper.is_available():
                self._notify(
                    "Whisper no instalado. En PowerShell: .\\setup.ps1 (desde la carpeta Echo)"
                )
                self._set_state(AppState.IDLE)
                return
            print(f"[Echo] Transcribiendo: {wav}")
            text = self._whisper.transcribe(wav)
            if not text:
                self._notify("No se entendio audio (transcripcion vacia).")
                self._set_state(AppState.IDLE)
                return
            print(f'[Echo] Texto entendido: "{text}"')
            self.process_text(text)
        except Exception as e:
            logger.exception("Processing failed: %s", e)
            self._notify(f"Error: {e}")
            self._history.append(
                raw_text="",
                intent_name="error",
                success=False,
                error=str(e),
            )
            self._set_state(AppState.IDLE)
        finally:
            try:
                wav.unlink(missing_ok=True)
            except OSError:
                pass

    def record_and_process(self, duration: float = 2.0) -> None:
        """Blocking record for tests and manual trigger."""
        self._set_state(AppState.LISTENING)
        wav = self._capture.record_blocking(duration)
        self._set_state(AppState.PROCESSING)
        if wav:
            self._process_audio(wav)
        else:
            self._set_state(AppState.IDLE)

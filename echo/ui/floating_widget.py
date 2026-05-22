"""Floating always-on-top assistant orb."""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QWidget

STATE_COLORS = {
    "idle": QColor(70, 130, 220),
    "listening": QColor(80, 200, 120),
    "processing": QColor(230, 180, 60),
    "speaking": QColor(180, 100, 220),
}


class AssistantState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


class FloatingWidget(QWidget):
    """Hold left-click on the orb to talk (same as Win+Space). Drag to move."""

    ptt_pressed = Signal()
    ptt_released = Signal()
    menu_requested = Signal()

    DIAMETER = 56
    SCREEN_MARGIN = 24

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._state = AssistantState.IDLE
        self._drag_pos: QPoint | None = None
        self._ptt_from_mouse = False
        self._init_ui()

    def _init_ui(self) -> None:
        self.setFixedSize(self.DIAMETER, self.DIAMETER)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Mantén pulsado para hablar · clic derecho: menú · Win+Espacio")

    def place_bottom_right(self, margin: int | None = None) -> None:
        """Dock orb in the bottom-right of the primary screen (with margin)."""
        margin = self.SCREEN_MARGIN if margin is None else margin
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        area = screen.availableGeometry()
        x = area.x() + area.width() - self.width() - margin
        y = area.y() + area.height() - self.height() - margin
        self.move(x, y)

    @property
    def state(self) -> AssistantState:
        return self._state

    def set_state(self, state: AssistantState | str) -> None:
        if isinstance(state, str):
            state = AssistantState(state)
        self._state = state
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = STATE_COLORS.get(self._state.value, STATE_COLORS["idle"])
        margin = 4
        painter.setBrush(color)
        painter.setPen(QPen(color.darker(120), 2))
        painter.drawEllipse(margin, margin, self.DIAMETER - 2 * margin, self.DIAMETER - 2 * margin)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            self.menu_requested.emit()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._ptt_from_mouse = True
            self.ptt_pressed.emit()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._ptt_from_mouse:
            self._ptt_from_mouse = False
            self.ptt_released.emit()
        self._drag_pos = None

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

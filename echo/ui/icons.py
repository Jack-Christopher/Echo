"""Application icons (generated at runtime — no asset files required)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap


def create_tray_icon(size: int = 32, color: QColor | None = None) -> QIcon:
    """Build a simple circular icon for the system tray and window."""
    if color is None:
        color = QColor(70, 130, 220)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(color)
    painter.setPen(Qt.PenStyle.NoPen)
    margin = max(2, size // 16)
    painter.drawEllipse(margin, margin, size - 2 * margin, size - 2 * margin)
    painter.end()
    icon = QIcon(pixmap)
    icon.addPixmap(pixmap)
    return icon

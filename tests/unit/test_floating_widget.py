import pytest
from PySide6.QtCore import Qt

from echo.ui.floating_widget import AssistantState, FloatingWidget


@pytest.mark.qt
@pytest.mark.unit
def test_states(qtbot):
    widget = FloatingWidget()
    qtbot.addWidget(widget)
    widget.set_state(AssistantState.LISTENING)
    assert widget.state == AssistantState.LISTENING
    widget.set_state("processing")
    assert widget.state.value == "processing"


@pytest.mark.qt
@pytest.mark.unit
def test_window_flags(qtbot):
    widget = FloatingWidget()
    qtbot.addWidget(widget)
    flags = widget.windowFlags()
    assert flags & widget.windowFlags()


@pytest.mark.qt
@pytest.mark.unit
def test_right_click_emits_menu_requested(qtbot):
    widget = FloatingWidget()
    qtbot.addWidget(widget)
    with qtbot.waitSignal(widget.menu_requested, timeout=1000):
        qtbot.mouseClick(widget, Qt.MouseButton.RightButton)

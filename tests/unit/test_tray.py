import pytest

from echo.ui.tray import SystemTray


@pytest.mark.qt
@pytest.mark.unit
def test_tray_menu_actions_exist(qapp):
    tray = SystemTray(on_exit=qapp.quit)
    assert tray._menu is not None
    assert tray._exit_action.text() == "Salir"
    assert tray.contextMenu() is tray._menu


@pytest.mark.qt
@pytest.mark.unit
def test_show_context_menu_does_not_raise(qapp, qtbot):
    tray = SystemTray()
    qtbot.addWidget(tray._menu)
    tray.show_context_menu()

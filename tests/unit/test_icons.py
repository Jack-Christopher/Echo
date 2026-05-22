import pytest

from echo.ui.icons import create_tray_icon


@pytest.mark.qt
@pytest.mark.unit
def test_create_tray_icon_not_null(qapp):
    icon = create_tray_icon()
    assert not icon.isNull()

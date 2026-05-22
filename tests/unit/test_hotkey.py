import pytest

from echo.speech.hotkey import PushToTalkHotkey


@pytest.mark.unit
def test_register_win_space():
    hk = PushToTalkHotkey("win+space")
    assert hk.register() is True


@pytest.mark.unit
def test_register_windows_alias():
    hk = PushToTalkHotkey("windows+space")
    assert hk.register() is True


@pytest.mark.unit
def test_register_unsupported():
    hk = PushToTalkHotkey("invalid+combo")
    assert hk.register() is False


@pytest.mark.unit
def test_simulate_press_release():
    events = []

    hk = PushToTalkHotkey(
        on_press=lambda: events.append("press"),
        on_release=lambda: events.append("release"),
    )
    hk.simulate_press()
    hk.simulate_release()
    assert events == ["press", "release"]

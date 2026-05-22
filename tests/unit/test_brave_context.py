import pytest

from echo.browser.brave import is_running


@pytest.mark.unit
def test_brave_context_fallback_is_running():
    """Without debug port, context detection falls back to process check."""
    result = is_running()
    assert isinstance(result, bool)

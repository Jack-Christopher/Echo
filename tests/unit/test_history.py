import pytest

from echo.logs.history import HistoryLog


@pytest.mark.unit
def test_append_and_read(tmp_path):
    log = HistoryLog(tmp_path / "history.jsonl")
    log.append("abre youtube", "open_website", True, message="ok")
    log.append("xyz", "unknown", False, error="fail")
    entries = log.read_recent()
    assert len(entries) == 2
    assert entries[0] == {"text": "abre youtube", "intent": "open_website", "result": "ok"}
    assert entries[1] == {"text": "xyz", "intent": "unknown", "result": "fail"}

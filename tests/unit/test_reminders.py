from datetime import datetime, timedelta

import pytest

from echo.reminders import ReminderScheduler


@pytest.mark.unit
def test_add_and_check_due(tmp_path):
    fired = []

    sched = ReminderScheduler(
        on_fire=lambda r: fired.append(r),
        store_path=tmp_path / "reminders.json",
    )
    due = (datetime.now() - timedelta(minutes=1)).isoformat()
    sched.add("tomar medicina", due)
    result = sched.check_due()
    assert len(result) == 1
    assert len(fired) == 1

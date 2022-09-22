from datetime import datetime, timezone

import pytest
from kpireport.report import Report


@pytest.fixture
def report():
    return Report(
        title="Fake report",
        interval_days=7,
        start_date=datetime(2020, 5, 1, 10, 11, 12, 0, timezone.utc),
        end_date=datetime(2020, 5, 7, 10, 11, 12, 0, timezone.utc),
        timezone=timezone.utc,
        theme=None,
    )

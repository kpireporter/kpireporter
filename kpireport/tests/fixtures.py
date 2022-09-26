import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Union

import pytest
import requests
from kpireport.output import OutputDriver
from kpireport.report import Report, Theme
from kpireport.utils import make_jinja_environment


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


@pytest.fixture
def jinja_env():
    return make_jinja_environment(Theme())


class FakePlugin:
    def __init__(self, report: "Report", id=None):
        pass


class FakeOutputDriver(OutputDriver):
    def init(self, **kwargs):
        pass

    def render_blob_inline(self, blob: "Blob", fmt=None):
        pass

    def render_output(self, content: "Content", blobs):
        pass


@dataclass
class FakeResponse:
    status_code: int
    content: "Union[str,Dict]"

    def raise_for_status(self):
        if self.status_code >= 300:
            raise requests.HTTPError()

    def json(self):
        if isinstance(self.content, str):
            return json.loads(self.content)
        return self.content

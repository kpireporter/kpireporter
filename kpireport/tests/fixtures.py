import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional, Union

import pytest
import requests
from kpireport.output import OutputDriver
from kpireport.report import Content, Report, Theme
from kpireport.utils import make_jinja_environment
from kpireport.view import Blob, Block


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
    j2 = make_jinja_environment(Theme())
    j2.globals["print_license"] = lambda: "(fake license)"
    return j2


@pytest.fixture
def content(report, jinja_env):
    c = Content(j2=jinja_env, report=report)
    blocks = [
        Block(
            id="first",
            title="First block",
            description="The first block in the rendered layout",
            cols=4,
            blobs=[],
            output="First block output",
            tags=["normal"],
        ),
        Block(
            id="second",
            title="Second block",
            description="The second block in the rendered layout",
            cols=2,
            blobs=[],
            output="Second block output",
            tags=[],
        ),
    ]
    c.add_format("html", blocks)
    c.add_format("md", blocks)
    c.add_format("slack", blocks)
    return c


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
    body: "Union[str,Dict]"
    headers: "Optional[Dict]" = field(default_factory=lambda: {})

    def raise_for_status(self):
        if self.status_code >= 300:
            raise requests.HTTPError()

    def json(self):
        if isinstance(self.body, str):
            return json.loads(self.body)
        return self.body

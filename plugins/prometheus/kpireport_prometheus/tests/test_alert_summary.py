import os
from datetime import datetime
from unittest.mock import Mock

import pandas as pd
import pytest
from kpireport.datasource import DatasourceManager
from kpireport.report import Report
from kpireport.tests.fixtures import FakeOutputDriver
from kpireport.tests.utils import make_datasource_manager
from kpireport.view import make_render_env
from kpireport_prometheus import PrometheusAlertSummary


def _mock_prometheus_response(ds_mgr: "DatasourceManager"):
    def _query(query_fn, *args, **kwargs):
        if query_fn == "ALERTS":
            return pd.DataFrame(
                [
                    {
                        "time": datetime.now(),
                        "value": 1,
                        "alertstate": "firing",
                        "alertname": "fake-alert1",
                        "host": "fake-host1",
                    }
                ]
            )
        raise ValueError(f"unmocked datasource query: {query_fn}")

    ds_mgr.get_instance("prometheus").query.side_effect = _query


def _assert_matches_fixture(output, fixture_name):
    fixture_path = os.path.join(os.path.dirname(__file__), fixture_name)
    with open(fixture_path, "r") as f:
        assert output == f.read()


@pytest.fixture
def ds_mgr():
    _ds_mgr = make_datasource_manager({"prometheus": Mock()})
    # Put an initial mock reply in w/ empty value
    _mock_prometheus_response(_ds_mgr)
    return _ds_mgr


@pytest.mark.parametrize("fmt", ["html", "md", "slack"])
def test_render(report: "Report", ds_mgr: "DatasourceManager", jinja_env, fmt: str):
    view = PrometheusAlertSummary(report, ds_mgr)
    j2 = make_render_env(jinja_env, view, FakeOutputDriver(report), fmt)
    _assert_matches_fixture(view.render(j2), f"expected_alert_summary.{fmt}")
    assert len(view.blobs) == 1

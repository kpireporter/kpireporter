from typing import Dict
from unittest import mock

import pytest
import requests
from kpireport.report import Report
from kpireport.tests.fixtures import FakeResponse
from kpireport_prometheus import PrometheusDatasource


def _mock_response(mocker: "mock", status_code: int, body: "Dict" = None):
    request = mocker.patch("requests.get")
    request.return_value = FakeResponse(status_code, body)
    return request


def test_query_simple(report: "Report", mocker: "mock"):
    _mock_response(
        mocker,
        200,
        {
            "status": "success",
            "data": {
                "resultType": "matrix",
                "result": [
                    {"metric": {"app": "fake-app1"}, "values": [[1.0, 1], [2.0, 1]]},
                    {"metric": {"app": "fake-app2"}, "values": [[1.0, 0], [2.0, 0]]},
                ],
            },
        },
    )
    ds = PrometheusDatasource(report, host="http://localhost:9090")
    df = ds.query("up")
    assert df.shape == (4, 3)
    assert list(df.columns) == ["time", "value", "app"]


def test_query_error_status(report: "Report", mocker: "mock"):
    _mock_response(mocker, 404)
    ds = PrometheusDatasource(report, host="http://localhost:9090")
    with pytest.raises(requests.HTTPError):
        ds.query("up")


def test_query_error_body(report: "Report", mocker: "mock"):
    _mock_response(mocker, 200, {"status": "error"})
    ds = PrometheusDatasource(report, host="http://localhost:9090")
    with pytest.raises(ValueError):
        ds.query("up")

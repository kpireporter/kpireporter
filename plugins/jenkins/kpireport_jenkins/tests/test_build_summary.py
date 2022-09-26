import os
from unittest.mock import Mock

import pandas as pd
import pytest
from kpireport.datasource import DatasourceManager
from kpireport.report import Report
from kpireport.tests.fixtures import FakeOutputDriver
from kpireport.tests.utils import make_datasource_manager
from kpireport.view import make_render_env
from kpireport_jenkins import JenkinsBuildSummary

FAKE_JOBS = [
    {
        "name": "job1",
        "fullname": "job1/main",
        "url": "https://jenkins.example.com/job1/main",
    },
    {
        "name": "job2",
        "fullname": "job2/main",
        "url": "https://jenkins.example.com/job2/main",
    },
]

FAKE_JOB_INFOS = {
    "job1/main": [
        {"result": "SUCCESS", "score": 50},
        {"result": "FAILURE", "score": 50},
    ],
    "job2/main": [
        {"result": "SUCCESS", "score": 100},
        {"result": "SUCCESS", "score": 100},
    ],
}


@pytest.fixture
def ds_mgr():
    _ds_mgr = make_datasource_manager({"jenkins": Mock()})
    # Put an initial mock reply in w/ empty value
    _mock_jenkins_response(_ds_mgr, FAKE_JOBS, FAKE_JOB_INFOS)
    return _ds_mgr


def _mock_jenkins_response(ds_mgr: "DatasourceManager", all_jobs=[], job_infos={}):
    def _query(query_fn, *args, **kwargs):
        if query_fn == "get_all_jobs":
            return pd.DataFrame(all_jobs)
        elif query_fn == "get_job_info":
            job_name = args[0]
            return pd.DataFrame(job_infos[job_name])
        raise ValueError(f"unmocked datasource query: {query_fn}")

    ds_mgr.get_instance("jenkins").query.side_effect = _query


def _assert_matches_fixture(output, fixture_name):
    fixture_path = os.path.join(os.path.dirname(__file__), fixture_name)
    with open(fixture_path, "r") as f:
        assert output == f.read()


def test_render_html(report: "Report", ds_mgr: "DatasourceManager", jinja_env):
    view = JenkinsBuildSummary(report, ds_mgr)
    j2 = make_render_env(jinja_env, view, FakeOutputDriver(report), "html")
    _assert_matches_fixture(view.render(j2), "expected_build_summary.html")


def test_render_md(report: "Report", ds_mgr: "DatasourceManager", jinja_env):
    view = JenkinsBuildSummary(report, ds_mgr)
    j2 = make_render_env(jinja_env, view, FakeOutputDriver(report), "md")
    _assert_matches_fixture(view.render(j2), "expected_build_summary.md")


def test_render_slack(report: "Report", ds_mgr: "DatasourceManager", jinja_env):
    view = JenkinsBuildSummary(report, ds_mgr)
    j2 = make_render_env(jinja_env, view, FakeOutputDriver(report), "slack")
    _assert_matches_fixture(view.render(j2), "expected_build_summary.slack")

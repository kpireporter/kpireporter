import os
from unittest.mock import Mock

import pandas as pd
import pytest
from kpireport.datasource import DatasourceManager
from kpireport.report import Report
from kpireport.tests.test_datasource import make_datasource_manager
from kpireport.view import make_view_jinja_env
from kpireport_jenkins import JenkinsBuildSummary

FAKE_JOBS = [
    {
        "name": "foo",
        "fullname": "foo/bar",
        "url": "https://jenkins.example.com/foo/bar",
    }
]

FAKE_JOB_INFOS = {
    "foo/bar": [{"result": "SUCCESS", "score": 80}, {"result": "FAILURE", "score": 80}]
}


@pytest.fixture
def ds_mgr():
    jenkins = Mock()
    _ds_mgr = make_datasource_manager(
        conf={"jenkins": {"plugin": "fake_jenkins"}},
        plugins=[("fake_jenkins", jenkins)],
    )
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
    with open(os.path.join(os.path.dirname(__file__), fixture_name), "r") as f:
        assert output == f.read()


def test_render_html(report: "Report", ds_mgr: "DatasourceManager", jinja_env):
    view = JenkinsBuildSummary(report, ds_mgr)
    j2 = make_view_jinja_env(jinja_env, view)
    _assert_matches_fixture(view.render_html(j2), "expected_build_summary.html")


def test_render_md(report: "Report", ds_mgr: "DatasourceManager", jinja_env):
    view = JenkinsBuildSummary(report, ds_mgr)
    j2 = make_view_jinja_env(jinja_env, view)
    _assert_matches_fixture(view.render_md(j2), "expected_build_summary.md")


def test_render_slack(report: "Report", ds_mgr: "DatasourceManager", jinja_env):
    view = JenkinsBuildSummary(report, ds_mgr)
    j2 = make_view_jinja_env(jinja_env, view)
    _assert_matches_fixture(view.render_slack(j2), "expected_build_summary.slack")

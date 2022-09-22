from unittest import mock

import pytest
from kpireport.report import Report
from kpireport_jenkins import JenkinsDatasource

JOBS_RESPONSE = [
    {
        "name": "v2-app/master",
        "color": "blue",
        "url": "https://jenkins.example.com/job/v2-app/job/master",
    },
    {
        "name": "v2-app/devel",
        "color": "red",
        "url": "https://jenkins.example.com/job/v2-app/job/devel",
    },
    {
        "name": "security-scan",
        "color": "blue",
        "url": "https://jenkins.example.com/job/security-scan",
    },
]

JOB_INFO_RESPONSE = {
    "builds": [
        {
            "id": "57",
            "url": "https://jenkins.example.com/job/v2-app/job/master/57",
            "result": "SUCCESS",
        },
        {
            "id": "56",
            "url": "https://jenkins.example.com/job/v2-app/job/master/56",
            "result": "SUCCESS",
        },
        {
            "id": "55",
            "url": "https://jenkins.example.com/job/v2-app/job/master/55",
            "result": "SUCCESS",
        },
        {
            "id": "54",
            "url": "https://jenkins.example.com/job/v2-app/job/master/54",
            "result": "SUCCESS",
        },
    ],
    "healthReport": [{"score": 100}],
}


def test_missing_host(report: "Report"):
    with pytest.raises(ValueError):
        ds = JenkinsDatasource(report)


def test_invalid_query(report: "Report"):
    ds = JenkinsDatasource(report, host="http://localhost")
    with pytest.raises(ValueError):
        ds.query("non_existent_query")


def test_get_all_jobs(report: "Report", mocker: "mock"):
    ds = JenkinsDatasource(report, host="http://localhost")
    mocker.patch.object(ds, "client").get_all_jobs.return_value = JOBS_RESPONSE
    df = ds.query("get_all_jobs")
    assert df.shape == (3, 3)
    assert list(df.columns) == ["name", "color", "url"]
    # Should be returned in order of response
    assert df.name[0] == "v2-app/master"


def test_get_job_info(report: "Report", mocker: "mock"):
    ds = JenkinsDatasource(report, host="http://localhost")
    mocker.patch.object(ds, "client").get_job_info.return_value = JOB_INFO_RESPONSE
    df = ds.query("get_job_info", "v2-app")
    assert df.shape == (4, 4)
    assert list(df.columns) == ["id", "url", "result", "score"]
    # Check that the healthReport.score value is in all rows
    assert all(x == 100 for x in df.score)

from kpireport.report import Report
from kpireport.tests import utils
from kpireport_googleanalytics import GoogleAnalyticsDatasource

"""Note: most of these tests will actually invoke the Google APIs!

This is to verify that the argument handling is working properly, rather than
attempting to mock out all the Google API backend behaviors ourselves and potentially
misrepresenting the API's actual behavior.
"""


def test_query_default(report: "Report", google_oauth2_keyfile):
    ds = GoogleAnalyticsDatasource(report, key_file=google_oauth2_keyfile)
    df = ds.query("report")
    assert len(df) == 7
    assert list(df.columns) == ["ga:users"]
    utils.assert_within_report_range(df.index[0].to_pydatetime(), report)
    utils.assert_within_report_range(df.index[-1].to_pydatetime(), report)


def test_query_with_dimensions(report: "Report", google_oauth2_keyfile):
    ds = GoogleAnalyticsDatasource(report, key_file=google_oauth2_keyfile)
    df = ds.query(
        "report",
        dimensions=["ga:date", "ga:pagepath"],
        filters_expression="ga:pagepath=~^/blog/",
    )
    assert len(df.columns) == 2
    assert list(df.columns) == ["ga:pagepath", "ga:users"]
    utils.assert_within_report_range(df.index[0].to_pydatetime(), report)
    utils.assert_within_report_range(df.index[-1].to_pydatetime(), report)


def test_query_with_metrics(report: "Report", google_oauth2_keyfile):
    ds = GoogleAnalyticsDatasource(report, key_file=google_oauth2_keyfile)
    df = ds.query("report", metrics=[{"expression": "ga:pageviews"}])
    assert list(df.columns) == ["ga:pageviews"]


def test_query_with_ordering(report: "Report", google_oauth2_keyfile):
    ds = GoogleAnalyticsDatasource(report, key_file=google_oauth2_keyfile)
    df = ds.query(
        "report", order_bys=[{"fieldName": "ga:users", "sortOrder": "DESCENDING"}]
    )
    assert list(df["ga:users"]) == sorted(df["ga:users"], reverse=True)

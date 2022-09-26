from unittest import mock

import pandas as pd
import pytest
from kpireport.report import Report
from kpireport_mysql import MySQLDatasource


@pytest.fixture
def cursor(mocker: "mock"):
    cur = mock.Mock()
    conn = mocker.patch("pymysql.connect")
    conn().cursor.return_value = cur
    cur.execute.return_value = cur
    return cur


def _mock_query_response(cursor, columns, rows):
    cursor.description = [[col] for col in columns]
    cursor.fetchall.return_value = rows


def _verify_dataframe(df, cols, rows):
    # Note: the first item in the row (first 'column') will be treated as an index,
    # not a column.
    assert df.shape == (len(rows), len(cols) - 1)
    assert df.equals(
        pd.DataFrame(
            [row[1:] for row in rows], columns=cols[1:], index=[row[0] for row in rows]
        )
    )


def test_query(report: "Report", cursor):
    cols, rows = ["id", "name"], [(1, "Anna"), (2, "Bob")]
    _mock_query_response(cursor, cols, rows)
    ds = MySQLDatasource(report)
    df = ds.query("select * from users")
    _verify_dataframe(df, cols, rows)


def test_query_param_replacement(report: "Report", cursor):
    _mock_query_response(cursor, ["id"], [])
    ds = MySQLDatasource(report)
    df = ds.query(
        "select * from users where join_date > date_sub({from}, {interval}) and "
        "join_date < {to}"
    )
    cursor.execute.assert_called_with(
        "select * from users where join_date > date_sub(%s, interval "
        f"{report.interval_days} day) and join_date < %s",
        [report.start_date, report.end_date],
    )


def test_query_param_invalid_replacement(report: "Report", cursor):
    _mock_query_response(cursor, [], [])
    report.interval_days = "; drop table users"
    ds = MySQLDatasource(report)
    with pytest.raises(ValueError):
        ds.query(
            "select * from users where join_date > date_sub(current_timestamp(), "
            "{interval})"
        )

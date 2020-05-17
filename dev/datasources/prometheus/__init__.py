from datetime import datetime, timedelta
import json
import os
import pandas as pd

from ..generate_timeseries import generate_sinusoidal

dirpath = os.path.dirname(os.path.realpath(__file__))


def open_file(name, mode):
    return open(os.path.join(dirpath, name), mode)


def to_prom_values(ts_df):
    ts_df['time'] = ts_df['time'].astype(int) / 10**9
    ts_df['value'] = ts_df['value'].astype(str)
    return ts_df.to_numpy().tolist()


def make_response():
    return dict(status="success", data={
        "resultType": "matrix",
        "result": []
    })


def add_result(response, labels, ts_df):
    response["data"]["result"].append(dict(
        metric=labels,
        values=to_prom_values(ts_df)
    ))


def add_sinusoidal_result(response, labels, **generate_kwargs):
    ts_df = generate_sinusoidal(**generate_kwargs)
    return add_result(response, labels, ts_df)


def add_window_result(response, labels, start, end):
    df = pd.DataFrame(pd.date_range(start, end, freq='min'), columns=['time'])
    df['value'] = 1
    return add_result(response, labels, df)


def add_alert_result(response, labels, start, end, alertname):
    labels = labels.copy()
    labels.update(dict(
        __name__="ALERTS",
        alertname=alertname,
        alertstate="firing"
    ))
    return add_window_result(response, labels, start, end)


def make():
    expectations = []

    res = make_response()
    add_alert_result(res, {"device": "/dev/sdb1", "severity": "critical"},
                     datetime.now() - timedelta(days=2, hours=3),
                     datetime.now() - timedelta(days=1, hours=2),
                     "NodeAlmostOutOfSpace")
    for service in ["prod-api", "batch-api", "analytics-api"]:
        add_alert_result(res, {"service": service, "severity": "critical"},
                         datetime.now() - timedelta(days=5, minutes=30),
                         datetime.now() - timedelta(days=5, minutes=15),
                         "ServiceDown")
    add_alert_result(res, {"cron": "some-cron-task", "severity": "warning"},
                     datetime.now() - timedelta(days=1, hours=7),
                     datetime.now(),
                     "CronJobFailed")
    add_alert_result(res, {"cron": "some-other-task", "severity": "warning"},
                     datetime.now() - timedelta(days=2, hours=12),
                     datetime.now() - timedelta(days=2),
                     "CronJobFailed")
    expectations.append({
        "httpRequest": {
            "path": "/api/v1/query_range",
            "queryStringParameters": {
                "query": ["ALERTS"]
            }
        },
        "httpResponse": {
            "body": res
        }
    })

    res = make_response()
    add_sinusoidal_result(res, {"hostname": "app01"}, base=2, amplitude=10)
    add_sinusoidal_result(res, {"hostname": "app02"}, base=1, amplitude=3)
    add_sinusoidal_result(res, {"hostname": "db01"}, base=4, amplitude=0.5)
    expectations.append({
        "httpRequest": {
            "path": "/api/v1/query_range",
            "queryStringParameters": {
                "query": [".*node_cpu_seconds_total.*"]
            }
        },
        "httpResponse": {
            "body": res
        }
    })

    with open_file("prometheus_api_mock.json", "w") as f:
        json.dump(expectations, f)

import json
import os

from ..generate_timeseries import generate_sinusoidal

dirpath = os.path.dirname(os.path.realpath(__file__))


def open_file(name, mode):
    return open(os.path.join(dirpath, name), mode)


def to_prom_values(ts_df):
    ts_df['time'] = ts_df['time'].astype(int) / 10**9
    ts_df['value'] = ts_df['value'].astype(str)
    return ts_df.to_numpy().tolist()


def make():
    expectations = []

    # with open_file("prometheus_alerts_mock.json", "r") as f:
    #     expectations.append({
    #         "httpRequest": {
    #             "path": "/api/v1/query_range",
    #             "queryStringParameters": {
    #                 "query": [".*ALERTS.*"]
    #             }
    #         },
    #         "httpResponse": {
    #             "body": json.load(f)
    #         }
    #     })

    def make_response():
        return dict(status="success", data={
            "resultType": "matrix",
            "result": []
        })

    def add_result(response, labels, values):
        response["data"]["result"].append(dict(
            metric=labels,
            values=values
        ))

    def add_sinusoid_result(res, hostname, **generate_kwargs):
        ts = generate_sinusoidal(**generate_kwargs)
        return add_result(res, {"hostname": hostname}, to_prom_values(ts))

    node_cpu_response = make_response()
    add_sinusoid_result(node_cpu_response, "app01", base=0, amplitude=12)
    add_sinusoid_result(node_cpu_response, "db01", base=4, amplitude=0.5)
    expectations.append({
        "httpRequest": {
            "path": "/api/v1/query_range",
            "queryStringParameters": {
                "query": [".*node_cpu_seconds_total.*"]
            }
        },
        "httpResponse": {
            "body": node_cpu_response
        }
    })

    with open_file("prometheus_api_mock.json", "w") as f:
        json.dump(expectations, f)

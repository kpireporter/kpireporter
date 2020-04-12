import json
import os

dirpath = os.path.dirname(os.path.realpath(__file__))

def open_file(name, mode):
    return open(os.path.join(dirpath, name), mode)

expectations = []

with open_file("prometheus_alerts_mock.json", "r") as f:
    expectations.append({
        "httpRequest": {
            "path": "/api/v1/query_range",
            "queryStringParameters": {
                "query": [""]
            }
        },
        "httpResponse": {
            "body": json.load(f)
        }
    })

with open_file("prometheus_node_cpu_seconds_mock.json", "r") as f:
    expectations.append({
        "httpRequest": {
            "path": "/api/v1/query_range",
            "queryStringParameters": {
                "query": [""]
            }
        },
        "httpResponse": {
            "body": json.load(f)
        }
    })

with open_file("prometheus_api_mock.json", "w") as f:
    json.dump(expectations, f)
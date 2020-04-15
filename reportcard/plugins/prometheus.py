import pandas as pd
import requests

from reportcard.datasource import Datasource


class PrometheusDatasource(Datasource):

    def init(self, host=None):
        if not host:
            raise ValueError("Missing required parameter: 'host'")
        if not host.startswith("http"):
            host = f"http://{host}"
        self.host = host

    def query(self, query: str, step="1h") -> pd.DataFrame:
        res = requests.get(f"{self.host}/api/v1/query_range", params=dict(
            start=self.report.start_date.timestamp(),
            end=self.report.end_date.timestamp(),
            step=step,
            query=query.strip()
        ))
        json = res.json()
        if json.get("status") != "success":
            raise ValueError("Got error response from Prometheus server")
        result = json.get("data", {}).get("result", [])
        df = pd.DataFrame()
        labels = set()
        for metric in result:
            mdf = pd.DataFrame(metric["values"], columns=["t", "value"])
            mdf["t"] = pd.to_datetime(mdf["t"], unit="s")
            mdf = mdf.set_index("t")
            mdf = mdf.assign(**metric["metric"])
            mdf = mdf.astype({"value": "float"})
            df = df.append(mdf)
            labels |= metric["metric"].keys()
        df = df.groupby(list(labels))
        return df

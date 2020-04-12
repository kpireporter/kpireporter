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
        for metric in result:
            mdf = pd.json_normalize(metric, "values")
            mdf = mdf.set_index(mdf.columns[0])
            mdf = mdf.rename(columns={1: "value"})
            mdf = mdf.assign(**metric["metric"])
            mdf = mdf.astype({"value": "float"})
            df = df.append(mdf)
        # TODO: make this generic!
        df = df.groupby(["hostname"])
        return df

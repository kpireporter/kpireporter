import pandas as pd
import requests

from kpireport.datasource import Datasource


class PrometheusDatasource(Datasource):
    """Datasource that executes PromQL queries against a Prometheus server.

    :type host: str
    :param host: the hostname of the Prometheus server (may include port),
                 e.g., :samp:`https://prometheus.example.com:9090`
    """

    def init(self, host=None):
        if not host:
            raise ValueError("Missing required parameter: 'host'")
        if not host.startswith("http"):
            host = f"http://{host}"
        self.host = host

    def query(self, query: str, step="1h") -> pd.DataFrame:
        """Execute a PromQL query against the Prometheus server.

        :type query: str
        :param query: the PromQL query
        :type step: str
        :param step: the step size for the range query. The Datasource will
                     execute a `range query <https://prometheus.io/docs/prometheus/latest/querying/api/#range-queries>`_
                     over the report window and capture all time series data
                     within the report boundaries. The step size indicates the
                     query resolution. A lower value provides more granularity
                     but at the cost of a more expensive query and more data
                     points to analyze. If your report window is significantly
                     short, it may make sense to reduce this.
        :rtype: pandas.DataFrame
        :returns: a table of time series results. The timeseries value will
                  be in a ``time`` column; any labels associated with the
                  metric will be added as additional columns.
        """
        res = requests.get(
            f"{self.host}/api/v1/query_range",
            params=dict(
                start=self.report.start_date.timestamp(),
                end=self.report.end_date.timestamp(),
                step=step,
                query=query.strip(),
            ),
        )
        res.raise_for_status()
        json = res.json()

        if json.get("status") != "success":
            raise ValueError("Got error response from Prometheus server")

        result = json.get("data", {}).get("result", [])

        df = pd.DataFrame()

        for metric in result:
            mdf = pd.DataFrame(metric["values"], columns=["time", "value"])
            mdf["time"] = pd.to_datetime(mdf["time"], unit="s")
            mdf = mdf.assign(**metric["metric"])
            mdf = mdf.astype({"value": "float"})
            df = df.append(mdf)

        return df

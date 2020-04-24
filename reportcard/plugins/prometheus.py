from datetime import timedelta
import numpy as np
import pandas as pd
import re
import requests

from reportcard.datasource import Datasource
from reportcard.view import View


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
            mdf = pd.DataFrame(metric["values"], columns=["time", "value"])
            mdf["time"] = pd.to_datetime(mdf["time"], unit="s")
            mdf = mdf.assign(**metric["metric"])
            mdf = mdf.astype({"value": "float"})
            df = df.append(mdf)

        return df


class PrometheusAlertSummary(View):
    RESOLUTION_REGEX = r"([0-9]+)([smhdwy])"

    def init(self, datasource="prometheus", resolution="15m",
             exclude_labels=["instance", "job"]):
        self.datasource = datasource
        self.resolution = self._parse_resolution(resolution)
        self.exclude_labels = exclude_labels

    def _parse_resolution(self, res):
        match = re.match(self.RESOLUTION_REGEX, res)

        if not match:
            raise ValueError("Invalid resolution format")

        mapping = {
            "s": "seconds",
            "m": "minutes",
            "h": "hours",
            "d": "days",
            "w": "weeks",
            "y": "years",
        }

        timedelta_kwargs = {mapping[match.group(2)]: int(match.group(1))}
        return timedelta(**timedelta_kwargs)

    def render(self, j2):
        df = self.datasources.query(
            self.datasource, "ALERTS", step=self.resolution.total_seconds())

        # Filter out pending alerts that never fired
        df = df[df["alertstate"] == "firing"]
        exclude_labels = ["__name__", "alertstate"] + self.exclude_labels
        df = df.drop(labels=exclude_labels, axis="columns")

        summary = {}
        for alertname in df["alertname"].unique():
            df_a = df[df["alertname"] == alertname]
            df_a = df_a.drop(labels="alertname", axis="columns")
            # Drop label columns that were not used for this alert
            df_a = df_a.dropna(how="all", axis="columns")
            # Round data points to resolution steps
            offset = pd.tseries.frequencies.to_offset(self.resolution)
            df_a["time"] = df_a["time"].dt.round(offset)
            # Find common label sets and which times those alerts fired
            df_ag = df_a.groupby(list(df_a.columns[2:]))["time"]
            alerts = {}
            for labelset, df_ts in df_ag:
                alerts[labelset] = windows = []
                curr_window = [None, None]
                list_ts = df_ts.tolist()
                for ts in list_ts:
                    if not curr_window[0]:
                        curr_window[0] = ts
                    elif (not curr_window[1] or
                        ts - curr_window[1] <= self.resolution):
                        curr_window[1] = ts
                    else:
                        windows.append(curr_window)
                        curr_window = [ts, None]
                # Close last window
                if not curr_window[1]:
                    curr_window[1] = list_ts[-1] + self.resolution
                windows.append(curr_window)
            summary[alertname] = alerts

        print(summary)

        template = j2.get_template("plugins/prometheus_alert_summary.html")
        return template.render(summary=summary)
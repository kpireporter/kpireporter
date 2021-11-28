import pandas as pd
from pdpyras import APISession

from kpireport.datasource import Datasource, DatasourceError

import logging

LOG = logging.getLogger(__name__)


def _dt_convert(df, columns, tz):
    for dt_col in columns:
        if dt_col not in df:
            continue
        df[dt_col] = pd.to_datetime(df[dt_col])
        df[dt_col] = df[dt_col].dt.tz_convert(tz)
    return df


class PagerDutyDatasource(Datasource):
    """A datasource that can fetch metrics from PagerDuty's API.

    Attributes:
        api_key (str): The PagerDuty API key.
    """

    def init(self, api_key=None):
        if not api_key:
            raise DatasourceError("'api_key' is required")
        self._session = APISession(api_key)

    def query(self, query: str, **kwargs) -> pd.DataFrame:
        query_fn = getattr(self, f"query_{query}", None)
        if query_fn and callable(query_fn):
            return query_fn(**kwargs)
        else:
            raise ValueError(f"Invalid query '{query}'")

    def query_incidents(self, **kwargs) -> pd.DataFrame:
        incidents = self._session.list_all("incidents", params=kwargs)
        df = pd.json_normalize(incidents)
        df = _dt_convert(
            df, ["created_at", "last_status_change_at"], self.report.timezone
        )
        return df

    def query_log_entries(self, **kwargs) -> pd.DataFrame:
        since = kwargs.pop("since", self.report.start_date)
        until = kwargs.pop("until", self.report.end_date)
        is_overview = kwargs.pop("is_overview", True)
        log_entries = self._session.list_all(
            "log_entries",
            params={
                "since": since,
                "until": until,
                "is_overview": is_overview,
            },
        )
        le_df = pd.json_normalize(log_entries)
        le_df = _dt_convert(le_df, ["created_at"], self.report.timezone)
        return le_df

    def query_incidents_by_day(self, **kwargs) -> pd.DataFrame:
        # Return a dataframe w/ daily rollups within the report window, which
        # returns how many incidents were active matching the input parameters.

        # Idea: create new columns, one for each day in the report window. Count the
        # number of rows that started BEFORE/DURING and had the last_status change
        # AFTER/DURING that day; those incidents were active that day.

        # 1. Get list of ALL active incidents (may include very old ones)
        # 2. Get list of ALL log entries BETWEEN report start and end date. This will
        #    provide info about any incidents that were resolved in the report window.
        # 3. For all resolved incidents in (2), look up incidents to see when they
        #    started. (may not be necessary since resolution MUST be the last event.)
        # 4. Incidents for a given day =
        #    (all incidents in (1) that had created_at < day) +
        #    (all incidents for events in (2) that had created_at < day)
        #    - drop duplicates
        since = kwargs.pop("since", self.report.start_date)
        until = kwargs.pop("until", self.report.end_date)
        days = pd.date_range(since, until, tz=self.report.timezone)

        incident_params = {
            "since": since,
            "until": until,
            "statuses[]": ["triggered", "acknowledged"],
        }
        i_df = self.query_incidents(**incident_params)

        le_df = self.query_log_entries(since=since, until=until)
        merged = self._correlate_log_entries(
            le_df, "trigger_log_entry", "resolve_log_entry"
        )

        def incidents_during_day(day):
            d = day.date()
            triggered_before = (merged["created_at_start"].dt.date <= d) | merged[
                "created_at_start"
            ].isna()
            ended_after = (merged["created_at_end"].dt.date >= d) | merged[
                "created_at_end"
            ].isna()
            active_during_period = merged[(triggered_before & ended_after)][
                "incident.id"
            ]
            ongoing = i_cf[i_cf["created_at"].dt.date <= d]["id"]
            return len(active_during_period.append(ongoing).unique())

        incidents_by_day_df = pd.DataFrame(index=days)
        incidents_by_day_df["num_incidents"] = days.to_series().apply(
            incidents_during_day
        )
        return incidents_by_day_df

    def query_mean_time_to_ack(self, **kwargs) -> pd.DataFrame:
        return self._mean_time_between_entries(
            "trigger_log_entry", "acknowledge_log_entry", **kwargs
        )

    def query_mean_time_to_resolve(self, **kwargs) -> pd.DataFrame:
        return self._mean_time_between_entries(
            "trigger_log_entry", "resolve_log_entry", **kwargs
        )

    def _mean_time_between_entries(
        self, from_entry: str, to_entry: str, **kwargs
    ) -> pd.DataFrame:
        le_df = self.query_log_entries(**kwargs)
        le_df = self._correlate_log_entries(le_df, from_entry, to_entry)
        deltas = le_df["created_at_end"] - le_df["created_at_start"]
        return pd.DataFrame([deltas.mean()], columns=["mean"])

    def _correlate_log_entries(
        self, le_df: pd.DataFrame, start_event: str, end_event: str
    ) -> pd.DataFrame:
        start_entries = le_df[le_df["type"] == start_event]
        end_entries = le_df[le_df["type"] == end_event]
        merged = start_entries.merge(
            end_entries, on="incident.id", how="outer", suffices=("_start", "_end")
        )
        return merged

from datetime import datetime, timezone

from apiclient.discovery import build
from kpireport.config import DEFAULT_CONF_DIR
from kpireport.datasource import Datasource
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import pytz

import logging

LOG = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
DATE_DIMENSION = "ga:date"


class GoogleAnalyticsDatasource(Datasource):
    def init(self, key_file=None, view_id=None):
        if not key_file:
            key_file = f"{DEFAULT_CONF_DIR}/google_oauth2_key.json"

        credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file, SCOPES)
        # Turn off cache discovery to suppress a noisy warning when using
        # oauth2client >= 4.0.0
        # https://github.com/googleapis/google-api-python-client/issues/427#issuecomment-737302835
        build_kwargs = {"credentials": credentials, "cache_discovery": False}

        self.reports = build("analyticsreporting", "v4", **build_kwargs).reports()
        self.mgmt = build("analytics", "v3", **build_kwargs).management()
        self._discover_view_info()

    def _discover_view_info(self):
        try:
            accounts = self.mgmt.accounts().list().execute().get("items", [])
            if not accounts:
                raise ValueError(
                    (
                        "Not authorized for any accounts. Please ensure your "
                        "service account is added to your Analytics account with "
                        "read/analyze permissions."
                    )
                )
            account_id = accounts[0]["id"]
            views = (
                self.mgmt.profiles()
                .list(accountId=account_id, webPropertyId="~all")
                .execute()
            ).get("items", [])
            LOG.debug(f"autodetect: all GA views={views}")
            if views:
                self.view_id = views[0]["id"]
                self.view_tz = pytz.timezone(views[0]["timezone"])
                LOG.info(
                    (
                        f"Auto-detected Google Analytics view {self.view_id}. "
                        "Please use the 'view_id' argument to use a different view."
                    )
                )
            else:
                raise ValueError("No views matched search arguments")
        except Exception as e:
            raise ValueError(
                "Failed to automatically detect a Google Analytics view."
            ) from e

    def query(
        self, input: str, view_id=None, dimensions=None, metrics=None
    ) -> pd.DataFrame:
        date_fmt = "%Y-%m-%d"

        def date_range_param(dt: datetime):
            """Convert UTC datetime to localized and properly formatted date string.

            Google Analytics views are timezone-aware and so are the APIs one uses
            to interact with them.
            """
            return datetime.strftime(dt.astimezone(self.view_tz), date_fmt)

        # Ensure date dimension is first; we use this later for the Dataframe index
        dimensions = [{"name": DATE_DIMENSION}] + (dimensions or [])
        if not metrics:
            # Default to just showing number of users
            metrics = [{"expression": "ga:users"}]
        res = self.reports.batchGet(
            body={
                "reportRequests": [
                    {
                        "viewId": view_id or self.view_id,
                        "dateRanges": [
                            {
                                "startDate": date_range_param(self.report.start_date),
                                "endDate": date_range_param(self.report.end_date),
                            }
                        ],
                        # Ensure rows with 0 values for metrics are still included
                        # (only works if ONLY date-derived dimensions are used, i.e.,
                        # dimensions with known low cardinality.)
                        # See: https://stackoverflow.com/a/44394541
                        "includeEmptyRows": True,
                        "metrics": metrics,
                        "dimensions": dimensions,
                        "orderBys": [
                            {"fieldName": DATE_DIMENSION, "sortOrder": "ASCENDING"}
                        ],
                    },
                ],
            }
        ).execute()

        report = res["reports"][0]
        report_hdr = report["columnHeader"]

        df_idx = []
        df_columns = [d for d in report_hdr["dimensions"] if d != DATE_DIMENSION] + [
            m["name"] for m in report_hdr["metricHeader"]["metricHeaderEntries"]
        ]
        df_rows = []

        for row in report["data"]["rows"]:
            date_dim = row["dimensions"][0]
            df_idx.append(self.view_tz.localize(datetime.strptime(date_dim, "%Y%m%d")))
            df_rows.append(
                [d for d in row["dimensions"][1:]]
                + [m["values"][0] for m in row["metrics"]]
            )

        df = pd.DataFrame(df_rows, index=df_idx, columns=df_columns)
        return df

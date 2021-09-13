from datetime import datetime, timezone
from functools import lru_cache

from apiclient.discovery import build
from kpireport.config import DEFAULT_CONF_DIR
from kpireport.datasource import Datasource
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import pytz

import logging

LOG = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
API_DATE_FMT = "%Y-%m-%d"
DATE_DIMENSIONS = {
    "ga:date": "%Y%m%d",
    "ga:dateHour": "%Y%m%d%H",
    "ga:dateHourMinute": "%Y%m%d%H%M",
}


class GoogleAnalyticsDatasource(Datasource):
    """A Datasource that provides data from the Google Analytics APIs.

    This Datasource supports a whitelist of query types:

        ``report``: Get a Report from the V4 Reporting API.
            See :func:`query_report` for additional options/arguments.

    To use in a View, the type of query is specified as the first argument.
    Any additional keyword arguments are interpreted as options specific to that
    query type.

    .. code-block:: python

       # From within a View member function...
       df = self.datasources.query("ga", "report", account_like="MyAccount")

    Attributes:
        key_file (str): The Google service account key file (must be in JSON format.)
            Refer to the `Google Cloud documentation
            <https://cloud.google.com/docs/authentication/production#manually>`_ for
            more information on how to set up this authentication credential.
            Default ``/etc/kpireporter/google_oauth2_key.json``.

    """

    def init(self, key_file=None):
        if not key_file:
            key_file = f"{DEFAULT_CONF_DIR}/google_oauth2_key.json"

        credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file, SCOPES)
        # Turn off cache discovery to suppress a noisy warning when using
        # oauth2client >= 4.0.0
        # https://github.com/googleapis/google-api-python-client/issues/427#issuecomment-737302835
        build_kwargs = {"credentials": credentials, "cache_discovery": False}

        self.reports = build("analyticsreporting", "v4", **build_kwargs).reports()
        self.mgmt = build("analytics", "v3", **build_kwargs).management()

    @lru_cache(maxsize=1)
    def _lookup_view(self, account_like=None, property_like=None, view_like=None):
        try:
            all_accounts = self.mgmt.accounts().list().execute().get("items", [])
            LOG.debug(f"autodetect: all GA accounts={all_accounts}")
            accounts = [
                a
                for a in all_accounts
                if (not account_like) or account_like in [a["name"], a["id"]]
            ]
            if not accounts:
                raise ValueError(
                    (
                        "Not authorized for requested account. Please ensure your "
                        "service account is added to your Analytics account with "
                        "read/analyze permissions."
                    )
                )
            elif len(accounts) > 1:
                LOG.warning("Multiple accounts matched, picking first from list.")
            account_id = accounts[0]["id"]

            all_properties = (
                self.mgmt.webproperties().list(accountId=account_id).execute()
            ).get("items", [])
            LOG.debug(f"autodetect: all GA properties={all_properties}")
            properties = [
                p
                for p in all_properties
                if (not property_like) or property_like in [p["id"], p["name"]]
            ]
            if not properties:
                raise ValueError("Could not find requested properties.")
            elif len(properties) > 1:
                LOG.warning("Multiple properties matched, picking first from list.")
            property_id = properties[0]["id"]

            all_views = (
                self.mgmt.profiles()
                .list(accountId=account_id, webPropertyId=property_id)
                .execute()
            ).get("items", [])
            LOG.debug(f"autodetect: all GA views={all_views}")
            views = [
                v
                for v in all_views
                if (not view_like) or view_like in [v["id"], v["name"]]
            ]
            if not views:
                raise ValueError("Could not find requested view.")
            elif len(views) > 1:
                LOG.warning("Multiple views matched, picking first from list.")
            view_id = views[0]["id"]
            view_tz = pytz.timezone(views[0]["timezone"])
            LOG.info(
                (
                    f"Auto-detected Google Analytics view {view_id}. "
                    "Please use the 'view_id' argument to use a different view."
                )
            )
            return view_id, view_tz
        except Exception as e:
            raise ValueError(
                "Failed to automatically detect a Google Analytics view."
            ) from e

    def query(self, input: str, **kwargs) -> pd.DataFrame:
        """Query the Google Analytics API.

        Args:
            input (str): The name of the query command to invoke.
                Currently supports only "report".

        Returns:
            A DataFrame with the query results.
        """
        if input == "report":
            return self.query_report(**kwargs)
        else:
            raise ValueError(f"Unsupported query '{input}'")

    def query_report(
        self,
        account_like=None,
        property_like=None,
        view_like=None,
        dimensions=None,
        metrics=None,
        filters_expression=None,
        order_bys=None,
    ) -> pd.DataFrame:
        """Request a report from the GA v4 Analytics API.

        Args:
            account_like (str): the GA account name or ID to search for the view. If
                not defined, the first account found is used.
            property_like (str): the GA property name or ID to search for the view. If
                not defined, the first property found is used.
            view_like (str): the GA view name or ID. If not defined, the first view
                found is used.

                .. note::
                   If you have multiple accounts or properties available from your
                   credentials, ensure you set ``account_like`` and ``property_like``
                   if you are using this field, as the default functionality for both
                   of those options is to naively take the first account/property found,
                   which may not have the view you're looking for.

            dimensions (List[str]): a list of `dimensions
                <https://developers.google.com/analytics/devguides/reporting/core/v4/basics#dimensions>`_.
                These can be just dimension names, or the full object syntax. If one
                of these dimensions is a "date-like" dimension (e.g., "ga:date.*"), the
                output DataFrame will have this dimension treated as a DateTimeIndex,
                making it effectively return something that looks like a time series.
            metrics (List[str]): a list of `metrics
                <https://developers.google.com/analytics/devguides/reporting/core/v4/basics#metrics>`_.
                These can be just metric expressions, or the full object syntax.
            filters_expression (str): an optional `filter expression
                <https://developers.google.com/analytics/devguides/reporting/core/v3/reference#filters>`_.
            order_bys (List[dict]): a list of `orderings
                <https://developers.google.com/analytics/devguides/reporting/core/v4/basics#ordering>`_.

        Returns:
            pd.DataFrame: a :class:`pd.DataFrame` with dimensions and metrics added.
                The dimensions will be the first columns in the resulting table, and
                each metric returned will be in a subsequent column.
        """
        view_id, view_tz = self._lookup_view(
            account_like=account_like, property_like=property_like, view_like=view_like
        )

        def date_range_param(dt: datetime):
            """Convert UTC datetime to localized and properly formatted date string.

            Google Analytics views are timezone-aware and so are the APIs one uses
            to interact with them.
            """
            return datetime.strftime(dt.astimezone(view_tz), API_DATE_FMT)

        if not dimensions:
            # Set a default single dimension of the metric date
            dimensions = ["ga:date"]

        # Check to see if user requested any date-like dimension
        date_dims = set(dimensions) & set(DATE_DIMENSIONS.keys())
        date_dim = next(iter(date_dims), None)
        if len(date_dims) > 1:
            LOG.warning(
                (
                    "There are multiple date dimensions on this query. Only the first "
                    "detected date dimension will be outputted."
                )
            )

        if all(isinstance(d, str) for d in dimensions):
            # Handle simple dimensions format
            dimensions = [{"name": d} for d in dimensions]

        if not metrics:
            # Default to just showing number of users
            metrics = [{"expression": "ga:users"}]

        req = {
            "viewId": view_id,
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
        }

        if filters_expression:
            req["filtersExpression"] = filters_expression

        if order_bys:
            req["orderBys"] = order_bys
        elif date_dim:
            # Add default sort order based on date dimension, if present
            req["orderBys"] = [{"fieldName": date_dim, "sortOrder": "ASCENDING"}]

        res = self.reports.batchGet(body={"reportRequests": [req]}).execute()
        report = res["reports"][0]
        hdr = report["columnHeader"]

        df_idx = []
        dim_columns = [d for d in hdr["dimensions"] if d not in date_dims]
        dim_column_idx = [hdr["dimensions"].index(d) for d in dim_columns]
        metric_columns = [m["name"] for m in hdr["metricHeader"]["metricHeaderEntries"]]
        df_columns = dim_columns + metric_columns
        df_rows = []

        for row in report["data"].get("rows", []):
            if date_dim:
                df_idx.append(
                    # GA data is in the View's local TZ; force-cast it to this TZ
                    view_tz.localize(
                        datetime.strptime(
                            row["dimensions"][hdr["dimensions"].index(date_dim)],
                            DATE_DIMENSIONS[date_dim],
                        )
                    )
                )
            row_dims = [row["dimensions"][idx] for idx in dim_column_idx]
            row_metrics = [float(m["values"][0]) for m in row["metrics"]]
            df_rows.append(row_dims + row_metrics)

        df = pd.DataFrame(df_rows, index=(df_idx or None), columns=df_columns)
        return df

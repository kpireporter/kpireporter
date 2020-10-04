import MySQLdb
import pandas as pd
import re

from kpireport.datasource import Datasource

import logging

LOG = logging.getLogger(__name__)


class MySQLDatasource(Datasource):
    """Provides an interface for running queries agains a MySQL database."""

    def init(self, **kwargs):
        """Initialize the Datasource and MySQL connector.

        :param **kwargs: keywoard arguments passed to :meth:`MySQLdb.Connect`
        """
        self.db = MySQLdb.connect(**kwargs)

    def query(self, sql: str, **kwargs) -> pd.DataFrame:
        """Execute a query SQL string.

        Some special tokens can be included in the SQL query. They will be
        replaced securely and escaped with the built-in parameter substition
        capabilities of the MySQL client.

        * ``{from}``: the start date of the Report
        * ``{to}``: the end date of the Report
        * ``{interval}``: an interval string set to the Report interval, i.e.,
          how many days is the Report window. This is useful when doing date
          substitution, e.g.

            .. code-block:: sql

               ; Also include previous interval
               WHERE time > DATE_SUB({from}, {interval})

        .. NOTE::

           By default, automatic date parsing will occur over the first column
           returned by the query. This can be disabled by passing in an empty
           list or dict to the ``parse_dates`` kwarg.


        :type sql: str
        :param sql: the SQL query to execute
        :param **kwargs**: keyword arguments passed to :meth:`pandas.read_sql`
        :rtype: pandas.DataFrame
        :returns: a table with any rows returned by the query. Columns
                  selected in the query will be columns in the output table.
        """
        sql, params = self._format_sql(sql)
        kwargs.setdefault("params", params)
        parse_dates = kwargs.setdefault("parse_dates", None)
        df = pd.read_sql(sql, self.db, **kwargs)

        if parse_dates is None:
            # Default to trying to parse the first column as some date format.
            try:
                df[df.columns[0]] = pd.to_datetime(
                    df[df.columns[0]], infer_datetime_format=True
                )
            except Exception:
                pass

        df = df.set_index(df.columns[0])
        LOG.debug(f"Query result: {df}")
        return df

    def _format_sql(self, sql: str) -> (str, list):
        """Replace special tokens in the SQL query.

        :type sql: str
        :param sql: the SQL query
        :rtype: Tuple[str, List[Any]]
        :returns: a tuple of the replaced SQL query and a list of parameters
                  to be passed to the MySQL client for secure substition.
        """
        params = []

        def collect_params(match):
            token = match.group(1)
            if token == "from":
                params.append(self.report.start_date)
            elif token == "to":
                params.append(self.report.end_date)
            elif token == "interval":
                return f"interval {int(self.report.interval_days)} day"
            else:
                raise ValueError(f"Unexpected token {token}")
            return "%s"

        replaced = re.sub(r"\{(interval|from|to)\}", collect_params, sql)

        return replaced, params

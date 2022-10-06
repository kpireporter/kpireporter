import logging
import re
import sqlite3
from typing import TYPE_CHECKING

import pandas as pd
import pymysql
from kpireport.datasource import Datasource

if TYPE_CHECKING:
    from typing import Any, List, Tuple

LOG = logging.getLogger(__name__)


class SQLDatasource(Datasource):
    """Provides an interface for running queries agains a SQL database.

    Attributes:
        driver (str): which DB driver to use. Possible values are "mysql" and "sqlite".
        kwargs: any keyword arguments are passed through to
            :meth:`pymysql.connect` (in the case of the MySQL driver) or
            :meth:`sqlite3.connect` (for the SQLite driver.)
    """

    def init(self, driver="mysql", **kwargs):
        if driver == "mysql":
            db = pymysql.connect(**kwargs)
        elif driver == "sqlite":
            db = sqlite3.connect(**kwargs)
        else:
            raise ValueError(f"unsupported DB driver: '{driver}'")
        self.db = db

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

           By default, no automatic date parsing will occur. To ensure that your
           timeseries data is properly parsed as a date, use the ``parse_dates``
           kwarg supported by :meth:`pandas.read_sql`, e.g.,

           .. code-block:: python

              self.datasources.query('my_db', 'select time, value from table',
                parse_dates=['time'])


        Args:
            sql (str): the SQL query to execute
            kwargs: keyword arguments passed to :meth:`pandas.read_sql`

        Returns:
            pandas.DataFrame: a table with any rows returned by the query.

                Columns selected in the query will be columns in the output
                table.
        """
        sql, params = self._format_sql(sql)
        kwargs.setdefault("params", params)
        LOG.debug(f"Query: {sql} {params}")
        df: "pd.DataFrame" = pd.read_sql(sql, self.db, **kwargs)
        df = df.set_index(df.columns[0])
        LOG.debug(f"Query result: {df}")
        return df

    def _format_sql(self, sql: str) -> "Tuple[str, List[Any]]":
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

import MySQLdb
import pandas as pd
import re

from reportcard.datasource import Datasource


class MySQLDatasource(Datasource):

    def init(self, **kwargs):
        self.db = MySQLdb.connect(**kwargs)

    def query(self, sql: str, **kwargs) -> pd.DataFrame:
        """
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_sql.html
        """
        sql, params = self.format_sql(sql)
        kwargs.setdefault("params", params)
        return pd.read_sql(sql, self.db, **kwargs)

    def format_sql(self, sql: str) -> (str, list):
        params = []

        def collect_params(match):
            token = match.group(1)
            if token == "from":
                params.append(self.report.start_date)
            elif token == "to":
                params.append(self.report.end_date)
            else:
                raise ValueError(f"Unexpected token {token}")
            return "%s"

        replaced = re.sub(r"\{(from|to)\}", collect_params, sql)

        return replaced, params

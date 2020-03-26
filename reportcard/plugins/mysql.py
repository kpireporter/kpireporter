import MySQLdb
import pandas as pd

from reportcard.datasource import Datasource


class MySQLDatasource(Datasource):

    def init(self, **kwargs):
        self.db = MySQLdb.connect(**kwargs)

    def query(self, sql: str, **kwargs) -> pd.DataFrame:
        """
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_sql.html
        """
        return pd.read_sql(sql, self.db, **kwargs)

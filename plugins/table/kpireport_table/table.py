from functools import lru_cache

from kpireport.view import View

class Table(View):
    """Render data fetched from a datasource as a table.

    Attributes:
        datasource (str): the datasource ID to fetch from.
        query (str): the query to execute against the datasource.
        query_args (dict): any additional keyword arguments to the datasource
            query operation.
    """
    def init(self, datasource=None, query=None, query_args=None, max_rows=None):
        self.datasource = datasource
        self.query = query
        self.query_args = query_args or {}
        self.max_rows = max_rows

        if not (self.datasource and self.query):
            raise ValueError(("Both a 'datasource' and 'query' parameter are required"))
        if not isinstance(self.query_args, dict):
            raise ValueError("Invalid format for 'query_args', expected dict")
        if self.max_rows and not isinstance(self.max_rows, int):
            raise ValueError("Invalid format for 'max_rows', expected int")

    @lru_cache(maxsize=1)
    def _query(self):
        df = self.datasources.query(self.datasource, self.query, **self.query_args)
        if self.max_rows:
            return df.head(self.max_rows)
        else:
            return df

    def render_html(self, j2):
        styles = f"""
        <style>
        .kpireport-table {{
            border-spacing: 0;
        }}
        .kpireport-table td,
        .kpireport-table th {{
            padding: .5rem;
        }}
        .kpireport-table tr:nth-child(2n) {{
            background: {self.report.theme.background_offset()};
        }}
        </style>
        """
        table = self._query().to_html(
            classes="kpireport-table", border=0, index_names=False)
        return f"{styles}\n{table}"

    def render_md(self, j2):
        return self._query().to_markdown()

    # def render_slack(self, j2):
        # Render as image?

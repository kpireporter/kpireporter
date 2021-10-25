from functools import lru_cache

from kpireport.view import View


def _summarize(df):
    if not df.columns.empty:
        return float(df[df.columns[0]].sum())
    else:
        return float(df.index.to_series().sum())


class SingleStat(View):
    """Display a single stat and optionally a delta.

    If the input query returns multiple rows, the rows are summed. If the query result
    is a DataFrame with multiple columns, only the first column is summed.

    Attributes:
        datasource (str): the ID of the Datasource to query.
        query (str): the query to execute agains the Datasource.
        query_args (dict): additional arguments to pass to the query function.
            Some Datasources may support additional parameters.
        label (str): a templated label that can be used to change how the stat is
            rendered. A ``{stat}`` template variable will be filled in with the stat
            value. (Default ``"{stat}"``)

            This can be used to create arbitrary other rendered output, e.g.:

              .. code-block::

                # Add a separate link element
                label: |
                  {stat} <a href="https://example.com">More</a>

        link_url (str): a hyperlink URL to open if the viewer clicks on the
            rendered output. The link wraps the entire display.
            (Default ``None``)
        comparison_query (str): an optional query to use as a comparison value.
            If defined, the current stat will be displayed,
            and the delta between the stat obtained via
            the comparison query will be shown next to it. (Default ``None``)
        comparison_query_args (dict): additional arguments to pass to the query
            function. Some Datasources may support additional parameters.
        comparison_type (str): how to show the delta; possible values are "raw",
            meaning the raw difference between the two values
            is displayed, or "percent", meaning the percentage
            increase/decrease is displayed. (Default ``"raw"``)
        precision (int): The floating point precision to use on the resulting stat.
            Set to the number of significant digits you want displayed. If 0, the stat
            is rounded to the nearest integer (Default ``0``)
    """

    def init(
        self,
        datasource=None,
        query=None,
        query_args={},
        label="{stat}",
        link_url=None,
        comparison_query=None,
        comparison_query_args={},
        comparison_type="raw",
        precision=0,
    ):
        self.datasource = datasource
        self.query = query
        self.query_args = query_args
        self.label = label
        self.link_url = link_url
        self.comparison_query = comparison_query
        self.comparison_query_args = comparison_query_args
        self.comparison_type = comparison_type
        self.precision = round(max(0, precision))

        if not (self.datasource and self.query):
            raise ValueError(("Both a 'datasource' and 'query' parameter are required"))

    @lru_cache(maxsize=1)
    def template_args(self):
        df = self.datasources.query(self.datasource, self.query, **self.query_args)
        stat_value = _summarize(df)
        stat_delta = None
        stat_delta_direction = None

        if self.comparison_query:
            df_cmp = self.datasources.query(
                self.datasource, self.comparison_query, **self.comparison_query_args
            )
            stat_cmp_value = _summarize(df_cmp)
            stat_delta = stat_value - stat_cmp_value
            stat_delta_direction = "up" if stat_delta >= 0 else "down"

            if self.comparison_type == "percent":
                if stat_cmp_value == 0:
                    # Avoid divide by zero
                    stat_delta = None
                else:
                    stat_delta = f"{(stat_delta / stat_cmp_value) * 100:.1f}%"

        label = self.label.format(stat=f"{stat_value:.{self.precision}f}")

        return dict(
            label=label,
            link_url=self.link_url,
            stat_delta=stat_delta,
            direction=stat_delta_direction,
            theme=self.report.theme,
        )

    def render_html(self, j2):
        template = j2.get_template("single_stat.html")
        return template.render(**self.template_args())

    def render_md(self, j2):
        template = j2.get_template("single_stat.md")
        return template.render(**self.template_args())

    def render_slack(self, j2):
        template = j2.get_template("single_stat.slack")
        return template.render(**self.template_args())

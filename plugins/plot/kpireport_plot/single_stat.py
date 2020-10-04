from functools import lru_cache

from kpireport.view import View


class SingleStat(View):
    """Display a single stat and optionally a delta.

    Attributes:
        datasource (str): the ID of the Datasource to query.
        query (str): the query to execute agains the Datasource.
        label (str): a templated label that can be used to change how the stat
            is rendered. A ``{stat}`` template variable will be filled
            in with the stat value. (Default ``"{stat}"``)
        comparison_query (str): an optional query to use as a comparison value.
            If defined, the current stat will be displayed,
            and the delta between the stat obtained via
            the comparison query will be shown next to it. (Default ``None``)
        comparison_type (str): how to show the delta; possible values are "raw",
            meaning the raw difference between the two values
            is displayed, or "percent", meaning the percentage
            increase/decrease is displayed. (Default ``"raw"``)
    """
    def init(
        self,
        datasource=None,
        query=None,
        label="{stat}",
        comparison_query=None,
        comparison_type="raw",
    ):
        self.datasource = datasource
        self.query = query
        self.label = label
        self.comparison_query = comparison_query
        self.comparison_type = comparison_type

        if not (self.datasource and self.query):
            raise ValueError(("Both a 'datasource' and 'query' parameter are required"))

    @lru_cache(maxsize=1)
    def template_args(self):
        df = self.datasources.query(self.datasource, self.query)
        stat_value = float(df.index.array[0])
        stat_delta = None
        stat_delta_direction = None

        if self.comparison_query:
            df_cmp = self.datasources.query(self.datasource, self.comparison_query)
            stat_cmp_value = float(df_cmp.index.array[0])
            stat_delta = stat_value - stat_cmp_value
            stat_delta_direction = "up" if stat_delta >= 0 else "down"

            if self.comparison_type == "percent":
                if stat_cmp_value == 0:
                    # Avoid divide by zero
                    stat_delta = None
                else:
                    stat_delta = f"{(stat_delta / stat_cmp_value) * 100:.1f}%"

        label = self.label.format(stat=stat_value)

        return dict(label=label, stat_delta=stat_delta, direction=stat_delta_direction)

    def render_html(self, j2):
        template = j2.get_template("single_stat.html")
        return template.render(theme=self.report.theme, **self.template_args())

    def render_md(self, j2):
        template = j2.get_template("single_stat.md")
        return template.render(**self.template_args())

    def render_slack(self, j2):
        template = j2.get_template("single_stat.slack")
        return template.render(**self.template_args())

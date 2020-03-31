import io
import matplotlib.pyplot as plt

from reportcard.view import View


class Plot(View):
    def init(self, datasource=None, query=None):
        self.datasource = datasource
        self.query = query

        if not (self.datasource and self.query):
            raise ValueError((
                "Both a 'datasource' and 'query' parameter are required"))

    @property
    def matplotlib_rc(self):
        text_color = "#222222"
        axis_color = "#cccccc"

        return {
            "lines.linewidth": 3,
            "text.color": text_color,
            "axes.edgecolor": axis_color,
            "axes.titlecolor": text_color,
            "axes.labelcolor": text_color,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.labelsize": 8,
            "xtick.color": text_color,
            "xtick.direction": "in",
            "ytick.labelsize": 8,
            "ytick.color": text_color,
            "ytick.direction": "in",
            "date.autoformatter.day": "%b %-d\n(%a)",
            "figure.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0,
        }

    def render(self, env):
        df = self.datasources.query(self.datasource, self.query)
        df = df.set_index(df.columns[0])

        with plt.rc_context(self.matplotlib_rc):
            ax = df.plot(figsize=[self.cols, 2], legend=None, title=None)
            ax.set_xlabel("")

            fig = ax.get_figure()
            figbytes = io.BytesIO()
            fig.savefig(figbytes)
            figname = "figure.png"
            self.add_blob(figname, figbytes)

            plt.close(fig)

        template = env.get_template("plugins/plot.html")

        return template.render(figure=figname)


class SingleStat(View):
    def init(self, datasource=None, query=None, comparison_query=None,
             comparison_type="raw"):
        self.datasource = datasource
        self.query = query
        self.comparison_query = comparison_query
        self.comparison_type = comparison_type

        if not (self.datasource and self.query):
            raise ValueError((
                "Both a 'datasource' and 'query' parameter are required"))

    def render(self, env):
        df = self.datasources.query(self.datasource, self.query)
        stat_value = df[df.columns[0]].iloc[0]
        stat_delta = None
        stat_delta_direction = None

        if self.comparison_query:
            df_cmp = self.datasources.query(self.datasource,
                                            self.comparison_query)
            stat_cmp_value = df_cmp[df_cmp.columns[0]].iloc[0]
            stat_delta = stat_value - stat_cmp_value
            stat_delta_direction = "up" if stat_delta >= 0 else "down"
            
            if self.comparison_type == "percent":
                if stat_cmp_value == 0:
                    # Avoid divide by zero
                    stat_delta = None
                else:
                    stat_delta = f"{stat_delta / stat_cmp_value:.2f}%"

        template = env.get_template("plugins/single_stat.html")

        return template.render(theme=self.report.theme, stat=stat_value,
                               stat_delta=stat_delta,
                               direction=stat_delta_direction)

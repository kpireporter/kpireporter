import io
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from reportcard.view import View

import logging
LOG = logging.getLogger(__name__)

DATE_FORMAT = "%b %-d\n(%a)"


class Plot(View):
    def init(self, datasource=None, query=None, query_args={},
             time_column="time", kind="line"):
        self.datasource = datasource
        self.query = query
        self.query_args = query_args
        self.time_column = time_column
        self.kind = kind

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
            "legend.loc": "upper left",
            "legend.frameon": False,
            "legend.fancybox": False,
            "legend.borderpad": 0,
            "legend.fontsize": "small",
            "date.autoformatter.day": DATE_FORMAT,
            "figure.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0,
        }

    def render_figure(self):
        df = self.datasources.query(self.datasource, self.query,
                                    **self.query_args)

        if self.time_column in df:
            df = df.set_index(self.time_column)

        if df.columns.size == 2:
            LOG.debug((
                "Automatically grouping data by "
                f"column='{df.columns[1]}'"))
            df = df.groupby(df.columns[1])
        elif df.columns.size > 2:
            LOG.warn((
                f"Dataframe has multiple columns: {list(df.columns)}. "
                "Two-dimensional plots will work best with only a value "
                "column and an optional grouping column."
            ))

        with plt.rc_context(self.matplotlib_rc):
            fig, ax = plt.subplots(figsize=[self.cols, 2])

            """
            Pandas is not great at handling custom date formats in a bar
            chart context; switch to using raw matplotlib for this type,
            if the index looks like it contains date/time data.
            """
            if self.kind == "bar" and isinstance(df.index, pd.DatetimeIndex):
                ax.xaxis.set_major_formatter(
                    mdates.DateFormatter(DATE_FORMAT))
                plt.xticks(rotation=30)
                plt.bar(pd.to_datetime(df.index), df[df.columns[0]])
            else:
                df.plot(ax=ax, kind=self.kind, legend=None, title=None)

            if getattr(df, "groups", None):
                ax.legend(df.groups, bbox_to_anchor=(1, 1))

            ax.set_xlabel("")

            fig = ax.get_figure()
            figbytes = io.BytesIO()
            fig.savefig(figbytes)
            figname = "figure.png"
            self.add_blob(figname, figbytes, mime_type="image/png")

            plt.close(fig)

            return figname

    def render_html(self, env):
        template = env.get_template("plugins/plot.html")
        return template.render(figure=self.render_figure())

    def render_md(self, env):
        self.render_figure()
        return ""

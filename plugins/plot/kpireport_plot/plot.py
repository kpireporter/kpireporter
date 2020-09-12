from cycler import cycler
import io
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from kpireport.view import View

import logging

LOG = logging.getLogger(__name__)

DATE_FORMAT = "%b %-d\n(%a)"


class Plot(View):
    """Render a line or bar graph as a PNG file inline.

    The :mod:`matplotlib` module handles rendering the plot. The Plot view
    sets a few default styles that make sense for plotting timeseries data,
    such as hiding the x-axis label and setting up date formatting for the
    x major labels.

    **Expected data formats**

    The Plot plugin can work for many different types of queries and
    Datasources, as long as a few properties hold for the response:

     * The returned table should ideally only have two columns: one for the
       time, and one for the value of the metric at that time.
     * The table can have three columns, in which case the data will be
       grouped by the last column. This can be useful if you want to display
       multiple series in one plot.

    Example of valid two-column result table:

    +------------+----------+
    | time       | value    |
    +============+==========+
    | 2020-01-01 | 1.0      |
    +------------+----------+
    | 2020-01-02 | 1.2      |
    +------------+----------+
    | 2020-01-03 | 2.1      |
    +------------+----------+

    Example of valid three-column result table:

    +------------+----------+---------+
    | time       | value    | country |
    +============+==========+=========+
    | 2020-01-01 | 1.0      | USA     |
    +------------+----------+---------+
    | 2020-01-01 | 3.2      | Germany |
    +------------+----------+---------+
    | 2020-01-02 | 1.2      | USA     |
    +------------+----------+---------+
    | 2020-01-02 | 2.7      | Germany |
    +------------+----------+---------+


    :type datasource: str
    :param datasource: ID of Datasource to fetch from
    :type query: str
    :param query: the query to execute against the Datasource
    :type query_args: dict
    :param query_args: additional arguments to pass to the query function.
                       Some Datasources may support additional parameters.
    :type time_column: str
    :param time_column: the name of the column in the query result table that
                        contains timeseries data. (Default="time")
    :type kind: str
    :param kind: the kind of plot to draw. Currently only "line" and "bar" are
                 officially supported, though other types supported by
                 matplotlib may be possible. (Default="line")
    :type stacked: bool
    :param stacked: whether to display the line/bar graph types as a stacked
                    plot, where each series is stacked atop the last.
    :type bar_labels: bool
    :param bar_labels: whether to label each bar with its value (only relevant
                       when kind is "bar".)
    :type xtick_rotation: Union[int, str]
    :param xtick_rotation: how much to rotate the X labels by when displaying.
    :type plot_rc: dict
    :param plot_rc: properties to set as :class:`matplotlib.RcParams`
    """

    def init(
        self,
        datasource=None,
        query=None,
        query_args={},
        time_column="time",
        kind="line",
        stacked=False,
        legend=None,
        bar_labels=False,
        xtick_rotation=0,
        plot_rc={},
    ):
        self.datasource = datasource
        self.query = query
        self.query_args = query_args
        self.time_column = time_column
        self.kind = kind
        self.stacked = stacked
        self.bar_labels = bar_labels
        self.xtick_rotation = xtick_rotation
        self.legend = legend
        self.plot_rc = plot_rc

        # TODO: make these configurable via the Theme
        self.text_color = "#222222"
        self.axis_color = "#cccccc"
        self.plot_colors = [
            "#0F5F0F",
            "#2D882D",
            "#94D794",
            "#DEA271",
            "#764013",
            "#B25B8C",
            "#5F0F3C",
        ]

        if not (self.datasource and self.query):
            raise ValueError(("Both a 'datasource' and 'query' parameter are required"))

    @property
    def matplotlib_rc(self):
        rc_params = self.plot_rc.copy()
        rc_defaults = {
            "lines.linewidth": 3,
            "text.color": self.text_color,
            "axes.edgecolor": self.axis_color,
            "axes.titlecolor": self.text_color,
            "axes.labelcolor": self.text_color,
            "axes.prop_cycle": cycler(color=self.plot_colors),
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.labelsize": 8,
            "xtick.color": self.text_color,
            "xtick.direction": "in",
            "ytick.labelsize": 8,
            "ytick.color": self.text_color,
            "ytick.direction": "in",
            "legend.loc": "lower left",
            "legend.frameon": False,
            "legend.fancybox": False,
            "legend.borderpad": 0,
            "legend.fontsize": "small",
            "date.autoformatter.day": DATE_FORMAT,
            "figure.dpi": 144,  # Retina display (ish)
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.083,
        }
        for k, v in rc_defaults.items():
            rc_params.setdefault(k, v)
        return rc_params

    def _plot_bar(self, df: "pandas.DataFrame", ax):
        """Render a bar chart with the current DataFrame."""

        def label_bars(rects):
            if not self.bar_labels:
                return
            for rect in rects:
                height = rect.get_height()
                ax.text(
                    rect.get_x() + rect.get_width() / 2.0,
                    1.05 * height,
                    "%d" % int(height),
                    ha="center",
                    va="bottom",
                    color=rect.get_facecolor(),
                    fontsize="small",
                    fontweight="bold",
                )

        if isinstance(df.index, pd.DatetimeIndex):
            ax.xaxis.set_major_formatter(mdates.DateFormatter(DATE_FORMAT))

        plot_fn = getattr(ax, self.kind, None)
        if not (plot_fn and callable(plot_fn)):
            raise ValueError(f"Plot function {self.kind} does not exist")

        rects = plot_fn(df.index, df[df.columns[0]])
        label_bars(rects)
        if self.stacked:
            bottom = df[df.columns[0]]
            for col in df.columns[1:]:
                rects = plot_fn(df.index, df[col], bottom=bottom)
                label_bars(rects)
                bottom += df[col]

    def _plot_default(self, df: "pandas.DataFrame", ax):
        df.plot(ax=ax, kind=self.kind, legend=None, title=None, stacked=self.stacked)

    def render_figure(self):
        df = self.datasources.query(self.datasource, self.query, **self.query_args)
        if self.time_column in df:
            df = df.set_index(self.time_column)

        if not self.stacked:
            # The auto-grouping behavior only makes sense if we're not told
            # to create a stacked graph.
            if df.columns.size == 2:
                LOG.debug((f"Automatically grouping data by column='{df.columns[1]}'"))
                df = df.groupby(df.columns[1])
            elif df.columns.size > 2:
                LOG.warn(
                    (
                        f"Dataframe has multiple columns: {list(df.columns)}. "
                        "Two-dimensional plots will work best with only a value "
                        "column and an optional grouping column."
                    )
                )

        # Ensure data is sorted along index; if it is not, matplotlib can
        # fail to properly graph it.
        df = df.sort_index()

        with plt.rc_context(self.matplotlib_rc):
            fig, ax = plt.subplots(figsize=[self.cols, 2], constrained_layout=True)

            if self.kind == "bar":
                self._plot_bar(df, ax)
            else:
                self._plot_default(df, ax)

            if self.legend is None and getattr(df, "groups", None):
                # Automatically generate legend by default if we're plotting
                # grouped data.
                ax.legend(df.groups, bbox_to_anchor=(0, -0.5))
            elif self.legend:
                l_kwargs = self.legend if isinstance(self.legend, dict) else {}
                ax.legend(df.columns, **l_kwargs)

            ax.set_xlabel("")
            plt.xticks(rotation=self.xtick_rotation)
            plt.tick_params(length=0)

            fig = ax.get_figure()
            figbytes = io.BytesIO()
            fig.savefig(figbytes)
            figname = "figure.png"
            self.add_blob(figname, figbytes, mime_type="image/png", title="Figure")

            plt.close(fig)

            return figname

    def render_html(self, j2):
        template = j2.get_template("plot.html")
        return template.render(figure=self.render_figure())

    def render_md(self, j2):
        template = j2.get_template("plot.md")
        return template.render(figure=self.render_figure())

    def render_slack(self, j2):
        self.render_figure()
        # Slack does not support rendering images inline from text--they
        # must be explicitly included as a Block element. This is a
        # "blob-only" View output.
        return ""
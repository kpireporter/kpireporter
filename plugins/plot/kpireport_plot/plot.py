from cycler import cycler
from functools import lru_cache
import io
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from kpireport.view import View

import logging

LOG = logging.getLogger(__name__)

DATE_FORMAT = "%b %-d\n(%a)"
FIGURE_PPI = 72  # Default PPI in matplotlib, not customizable
DEFAULT_FONT_SIZE = 10


class Plot(View):
    """Render a graph as a PNG file inline.

    The :mod:`matplotlib` module handles rendering the plot. The Plot view
    sets a few default styles that make sense for plotting timeseries data,
    such as hiding the x-axis label and setting up date formatting for the
    x major labels.

    **Expected data formats**

    The Plot plugin can work for many different types of queries and
    Datasources, as long as a few properties hold for the response:

     * The returned table should ideally only have two columns: one for the
       time, and one for the value of the metric at that time.
     * If the table has more than two columns, it is assumed that each column is
       a separate series and will be displayed as such, unless ``groupby`` is used.

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
    | time       | value_a  | value_b |
    +============+==========+=========+
    | 2020-01-01 | 1.0      | 0.4     |
    +------------+----------+---------+
    | 2020-01-01 | 3.2      | 0.2     |
    +------------+----------+---------+
    | 2020-01-02 | 1.2      | 0.2     |
    +------------+----------+---------+
    | 2020-01-02 | 2.7      | 0.7     |
    +------------+----------+---------+

    Example of valid three-column result table, where ``groupby: country`` would cause
    the data to be segmented according to the ``country`` column:

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

    Attributes:
        datasource (str): ID of Datasource to fetch from.
        query (str): the query to execute against the Datasource.
        query_args (dict): additional arguments to pass to the query function.
            Some Datasources may support additional parameters.
        time_column (str): the name of the column in the query result table that
            contains timeseries data. (Default ``"time"``)
        kind (str): the kind of plot to draw. Currently only "line", "bar", and
            "scatter" are supported. (Default ``"line"``)
        stacked (bool): whether to display the line/bar graph types as a stacked
            plot, where each series is stacked atop the last. This does not have any
            effect when rendering scatter plots. (Default ``False``)
        groupby (str): the name of the column in the query result table that should be
            used to group the data into separate series. (Default ``None``)
        bar_labels (bool): whether to label each bar with its value (only
            relevant when kind is "bar".) (Default ``False``)
        xtick_rotation (Union[int, str]): how much to rotate the X labels by
            when displaying.
        plot_rc (dict): properties to set as :class:`matplotlib.RcParams`. This
            can be used to customize the display of the output chart beyond
            the defaults provided by the Theme.
    """

    def init(
        self,
        datasource=None,
        query=None,
        query_args={},
        link_url=None,
        time_column="time",
        kind="line",
        groupby=None,
        stacked=False,
        legend=None,
        label_map=None,
        bar_labels=False,
        xtick_rotation=0,
        plot_rc={},
    ):
        self.datasource = datasource
        self.query = query
        self.query_args = query_args
        self.link_url = link_url
        self.time_column = time_column
        self.kind = kind
        self.groupby = groupby
        self.stacked = stacked
        self.label_map = label_map
        self.bar_labels = bar_labels
        self.xtick_rotation = xtick_rotation
        self.legend = legend
        self.plot_rc = plot_rc

        theme = self.report.theme
        self.text_color = theme.text_color
        self.axis_color = theme.text_offset()
        self.plot_colors = theme.series_colors

        if not (self.datasource and self.query):
            raise ValueError(("Both a 'datasource' and 'query' parameter are required"))

    @property
    def matplotlib_rc(self):
        rc_params = self.plot_rc.copy()
        rc_defaults = {
            "lines.linewidth": 3,
            "text.color": self.text_color,
            "font.size": DEFAULT_FONT_SIZE,
            "axes.edgecolor": self.axis_color,
            "axes.titlecolor": self.text_color,
            "axes.labelcolor": self.text_color,
            "axes.prop_cycle": cycler(color=self.plot_colors),
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.labelsize": DEFAULT_FONT_SIZE,
            "xtick.color": self.text_color,
            "xtick.direction": "in",
            "ytick.labelsize": DEFAULT_FONT_SIZE,
            "ytick.color": self.text_color,
            "ytick.direction": "in",
            "legend.loc": "lower left",
            "legend.frameon": False,
            "legend.fancybox": False,
            "legend.borderpad": 0,
            "date.autoformatter.day": DATE_FORMAT,
            "figure.dpi": FIGURE_PPI * 2,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 10 / FIGURE_PPI,
            "timezone": self.report.timezone,
        }
        for k, v in rc_defaults.items():
            rc_params.setdefault(k, v)
        return rc_params

    def _make_plot(self, ax, index_data, series_data):
        """Render a bar chart with the current DataFrame."""

        def with_labels(rects):
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

        if isinstance(index_data, pd.DatetimeIndex):
            ax.xaxis.set_major_formatter(mdates.DateFormatter(DATE_FORMAT))
            plt.xlim([self.report.start_date, self.report.end_date])

        if self.kind == "line":
            if self.stacked:
                ax.stackplot(index_data, *[s for s in series_data])
            else:
                for s in series_data:
                    ax.plot(index_data, s)
        elif self.kind == "scatter":
            for s in series_data:
                ax.plot(index_data, s, "o")
        elif self.kind == "bar":
            # FIXME: currently rendering multiple bar series will just render them
            # all on top of one another, which is not helpful. However, ensuring the
            # bars render side-by-side is complicated by the fact that the x-axis and
            # distribution of the data is highly variable, e.g., could be a date index
            # or a "regular" x-index depending on the query result. Should probably try
            # to do something reasonable and fall back to default behavior if it can't
            # be done.
            bar_kwargs = {}
            with_labels(ax.bar(index_data, series_data[0], **bar_kwargs))
            bottom = series_data[0]
            for _, s in enumerate(series_data[1:]):
                if self.stacked:
                    bar_kwargs["bottom"] = bottom
                with_labels(ax.bar(index_data, s, **bar_kwargs))
                bottom += s
        else:
            raise ValueError(f"Plot function {self.kind} does not exist")

    def _prune_nonnumeric_columns(self, df):
        orig_cols = set(df.columns)
        df = df.select_dtypes(include=["number"])
        pruned_cols = orig_cols - set(df.columns)
        if pruned_cols:
            LOG.warn(
                (
                    "Input DataFrame contained several non-numeric columns, which "
                    "have been pruned from the output, as they cannot be plotted: "
                    f"{pruned_cols}. Consider removing the extraneous columns or using "
                    "'groupby' to use the columns to denote multiple series instead."
                )
            )
        return df

    @lru_cache(maxsize=1)
    def render_figure(self):
        df = self.datasources.query(self.datasource, self.query, **self.query_args)
        if self.time_column in df:
            df = df.set_index(self.time_column)

        # Ensure data is sorted along index; if it is not, matplotlib can
        # fail to properly graph it.
        df = df.sort_index()

        if self.groupby:
            index_data = df.index.unique()
            df = df.groupby(self.groupby)
            series_labels = df.groups

            def _flatten_group(group_df):
                # When extracting a group as a Dataframe, the grouping column is once
                # again present. Remove it, as it is redundant (all rows will have the
                # same value)
                df = group_df.drop(self.groupby, axis=1)
                df = self._prune_nonnumeric_columns(df)
                # Ensure all groups are of the same size
                df = df.reindex(index_data, fill_value=0)
                if len(df.columns) > 1:
                    LOG.warn(
                        (
                            "After grouping data, there are still multiple columns. "
                            f"Taking just the first column '{df.columns[0]}'."
                        )
                    )
                return df[df.columns[0]]

            series_data = [_flatten_group(df.get_group(g)) for g in df.groups]
        else:
            index_data = df.index
            pruned_df = self._prune_nonnumeric_columns(df)
            series_labels = pruned_df.columns
            series_data = [pruned_df[col] for col in pruned_df.columns]

        if not series_data:
            raise ValueError("The query returned no plottable results.")

        if self.label_map:
            # Attempt to lookup name mapping from `label_map`
            series_labels = [self.label_map.get(lbl, lbl) for lbl in series_labels]

        with plt.rc_context(self.matplotlib_rc):
            figsize = [((self.cols * self.report.theme.column_width) / FIGURE_PPI), 2]
            fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)

            self._make_plot(ax, index_data, series_data)

            if self.legend is None and len(series_labels) > 1:
                # Automatically generate legend by default if we're plotting
                # multiple series or grouped data.
                ax.legend(series_labels, bbox_to_anchor=(0, -0.5), ncol=self.cols)
            elif self.legend:
                l_kwargs = self.legend if isinstance(self.legend, dict) else {}
                ax.legend(series_labels, **l_kwargs)

            ax.set_xlabel("")
            plt.xticks(rotation=self.xtick_rotation)
            plt.tick_params(length=0)

            self.post_plot(ax, df=df, index_data=index_data, series_data=series_data)

            fig = ax.get_figure()
            figbytes = io.BytesIO()
            fig.savefig(figbytes)
            figname = "figure.png"
            self.add_blob(figname, figbytes, mime_type="image/png", title="Figure")

            plt.close(fig)

            return figname

    def post_plot(self, ax, df=None, index_data=None, series_data=None):
        """A post-render hook that can be used to process the plot before outputting.

        Subclasses of the Plot class can override this to add, e.g., annotations or
        otherwise tweak the final plot output.
        """
        pass

    def render_html(self, j2):
        template = j2.get_template("plot.html")
        return template.render(figure=self.render_figure(), link_url=self.link_url)

    def render_md(self, j2):
        template = j2.get_template("plot.md")
        return template.render(figure=self.render_figure(), link_url=self.link_url)

    def render_slack(self, j2):
        self.render_figure()
        # Slack does not support rendering images inline from text--they
        # must be explicitly included as a Block element. This is a
        # "blob-only" View output.
        return ""

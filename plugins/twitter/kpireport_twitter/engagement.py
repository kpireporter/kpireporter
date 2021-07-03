from textwrap import wrap

from kpireport_plot import Plot
import matplotlib.dates as mdates

# How many characters to show in tweet text callout, per line
TWEET_LINE_LENGTH = 24
# How many lines of text to show in callout
TWEET_LINE_COUNT = 2


def human_format(num, pos):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "%d%s" % (num, ["", "K", "M", "B"][magnitude])


class TwitterEngagement(Plot):
    """Display a summary of engagement with an account's own Tweets.

    Attributes:
        **kwargs: keyword arguments passed to the parent :class:`~kpireport_plot.Plot`
            plugin.
    """

    def init(self, **kwargs):
        kwargs["query"] = "tweets"
        kwargs.setdefault("kind", "scatter")
        kwargs.setdefault(
            "legend",
            {
                "loc": "lower left",
                "ncol": 4,
                "bbox_to_anchor": [0, -0.5],
            },
        )
        kwargs.setdefault(
            "label_map",
            {
                "like_count": "Likes",
                "retweet_and_quote_count": "Shares",
                "reply_count": "Replies",
            },
        )
        return super().init(**kwargs)

    def post_plot(self, ax, df=None, index_data=None, series_data=None):
        # Humanize big numbers
        ax.yaxis.set_major_formatter(human_format)

        # Point out top tweets by like count
        top_tweets = df.sort_values(by=["like_count"], ascending=False).head(1)
        for row in top_tweets.itertuples():
            x = row.Index.to_pydatetime()
            y = row.like_count
            tweet_lines = wrap(row.text, TWEET_LINE_LENGTH)
            if len(tweet_lines) > TWEET_LINE_COUNT:
                tweet_lines = tweet_lines[:TWEET_LINE_COUNT]
                tweet_lines[1] += "..."
            ax.annotate(
                ('"' + "\n".join(tweet_lines) + '"'),
                xy=(x, y),
                xycoords="data",
                xytext=(20, 15),
                textcoords="offset points",
                horizontalalignment="left",
                verticalalignment="top",
                size="small",
                arrowprops={
                    "arrowstyle": "->",
                    "connectionstyle": "arc3,rad=.2",
                    "relpos": (0, 0.75),
                    "shrinkA": 3,
                    "shrinkB": 5,
                },
            )

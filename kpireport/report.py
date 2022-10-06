import logging
from datetime import datetime, timedelta
from functools import partial
from typing import TYPE_CHECKING

from dateutil.parser import parse as parse_date
from dateutil.tz import gettz, tzlocal
from jinja2 import TemplateNotFound
from slugify import slugify

from .datasource import DatasourceManager
from .license import License
from .output import OutputDriverManager
from .utils import make_jinja_environment
from .version import VERSION
from .view import ViewManager

if TYPE_CHECKING:
    from typing import List, Optional

    from jinja2 import Environment

    from .view import View

LOG = logging.getLogger(__name__)


class Theme:
    """The report theme options.

    Attributes:
        num_columns (int): the number of columns in the report grid. (Default 6)
        column_width (int): the width of each column, in pixels. (Default 86)
        padding_width (int): the width of the horizontal padding at the report edges
            (Default 20)
        theme_dir (str): a directory where additional templates can be found.
            These templates will override the default templates of the same
            name, and can be used to alter the overall report appearance.
        ui_colors (List[str]): a list of user interface colors. This is expected to
            be a 5-tuple of (text color, lighter text color, dark bg color, bg accent,
            bg color)
        error_colors (List[str]): a list of error colors used when views render an
            error vs. success state. This is expected to be a 2-tuple of
            (dark, light).
        success_colors (List[str]): a list of success colors used when views render
            an error vs. success state. This is expected to be a 2-tuple of
            (dark, light).
        series_colors (List[str]): a list of series colors. There can be as many or as
            few series colors in the theme; you just want to ensure you can handle
            whatever needs you have for plotting or displaying data in charts or graphs
            such that series can be identified clearly.
        heading_font (str): A CSS font-family declaration, which will define how the
            headings are styled. (Default "Helvetica, Arial, sans-serif"). Note that
            due to Jinja escaping rules, this does not like embedded quotes. Quotes
            are *not* required even when a typeface has a space in the name, so they
            are safe to simply omit.

    """

    def __init__(
        self,
        num_columns=6,
        column_width=86,
        padding_width=20,
        theme_dir=None,
        ui_colors=None,
        error_colors=None,
        success_colors=None,
        series_colors=None,
        heading_font=None,
    ):
        self.num_columns = num_columns
        self.column_width = column_width
        self.padding_width = padding_width
        self.theme_dir = theme_dir
        self.ui_colors = ui_colors or [
            "#222222",
            "#888888",
            "#cccccc",
            "#ededed",
            "#ffffff",
        ]
        self.error_colors = error_colors or [
            "#8b0000",
            "#ffcccb",
        ]
        self.success_colors = success_colors or [
            "#008000",
            "#d5ffd5",
        ]
        self.series_colors = series_colors or [
            "#0F5F0F",
            "#2D882D",
            "#94D794",
            "#DEA271",
            "#764013",
            "#B25B8C",
            "#5F0F3C",
        ]
        self.heading_font = heading_font or "Helvetica, Arial, sans-serif"
        self.text_font = "Helvetica, Arial, sans-serif"

    @property
    def text_color(self):
        return self.ui_colors[0]

    def text_offset(self, offset=1):
        return self.ui_colors[offset]

    @property
    def background_color(self):
        return self.ui_colors[-1]

    def background_offset(self, offset=1):
        return self.ui_colors[-(1 + offset)]

    @property
    def success_color(self):
        return self.success_colors[0]

    @property
    def success_background_color(self):
        return self.success_colors[-1]

    @property
    def error_color(self):
        return self.error_colors[0]

    @property
    def error_background_color(self):
        return self.error_colors[-1]


class Report:
    """The report object.

    .. note::

       This class is not meant to be instantiated directly; instead, use the
       :class:`ReportFactory` class to generate an instance.

    Attributes:
        title (str): the report title.
        interval_days (int): number of days.
        start_date (dateobj): the start date.
        end_date (dateobj): the end date.
        timezone (str): the timezone name. Defaults to the system timezone.
        theme (Theme): the report Theme.
    """

    version = VERSION

    def __init__(
        self,
        title=None,
        interval_days=None,
        start_date: "datetime" = None,
        end_date: "datetime" = None,
        timezone=None,
        theme=None,
    ):
        self.title = title
        self.interval_days = interval_days
        self.start_date = start_date
        self.end_date = end_date
        self.timezone = timezone
        self.title_slug = slugify(self.title)
        self.id = "_".join(
            [
                self.start_date.strftime("%Y-%m-%d"),
                self.end_date.strftime("%Y-%m-%d"),
                self.title_slug,
            ]
        )

        if theme:
            self.theme = theme
        else:
            self.theme = Theme()

    @property
    def timedelta(self):
        return self.end_date - self.start_date


class Content:
    """The rendered report, in a variety of formats.

    Attributes:
        j2 (Jinja2): a :mod:`Jinja2` context to use for loading and rendering
            templates.
        report (Report): the Report object for the current report.
        formats (List[str]): the list of all formats available for the report.
            Any formats added via :meth:`add_format` will be reflected here.
    """

    def __init__(self, j2: "Environment", report: "Report"):
        self.j2 = j2
        self.report = report
        self._formats = {}

    def add_format(self, fmt: str, views: "List[View]"):
        """Render the specified format and add to the output contents.

        If a layout file is found for this format, it will be used to render
        the raw output. If a layout file is not found, there will be no raw
        output, however, the list of Views will still be stored for the output
        format. This can be important for output drivers that may not be able
        to display/send a final rendered report in text, but could still render
        each view separately. The :ref:`Slack <slack-plugin>` output driver is
        a good example of this.

        The layout file is expected to exist at
        ``./templates/layout/default.{fmt}``, e.g.,
        ``./template/layout/default.html`` for the HTML format.

        Args:
            fmt (str): the output format, e.g., ``"md"`` or ``"html"``.
            views (List[View]): the list of Views to render
        """
        try:
            template = self.j2.get_template(f"layout/default.{fmt}")
        except TemplateNotFound:
            LOG.debug(
                (
                    f"No parent template found for format {fmt}, so no "
                    "final output text can be written. Views will still "
                    "be rendered individually."
                )
            )
            content = None
        else:
            content = template.render(views=views, report=self.report)

        # Also store a list of the raw views to allow the output
        # driver to render its own output structure
        self._formats[fmt] = dict(content=content, views=views)

    @property
    def formats(self):
        return self._formats.keys()

    def get_format(self, fmt: str) -> "Optional[str]":
        """Get the rendered string for the given format.

        Args:
            fmt (str): the desired output format.

        Returns:
            Optional[str]: the rendered content for the given format, if any.
        """
        return self._formats.get(fmt, {}).get("content")

    def get_views(self, fmt: str) -> "List[View]":
        """Get the rendered views for the given format.

        Args:
            fmt (str): the desired output format.

        Returns:
            List[View]: the list of Views rendered under that format.
        """
        return self._formats.get(fmt, {}).get("views", [])


class ReportFactory:
    """A factory class for building and executing an entire report.

    Once you have a report parsed from its YAML :ref:`configuration-file`, you
    can execute the report like so:

    .. code-block:: python

       ReportFactory(conf).create()

    Attributes:
        config (dict): the (parsed) configuration YAML file.
        supported_formats (List[str]): the output formats that any report can
            target.
    """

    supported_formats = ["html", "md", "slack"]

    def __init__(self, config):
        datasource_conf = config.get("datasources", {})
        view_conf = config.get("views", {})
        output_conf = config.get("outputs", {})

        interval_days = config.get("interval_days", 7)

        timezone = config.get("timezone", None)
        if timezone:
            timezone = gettz(timezone)
        else:
            timezone = tzlocal()

        end_date = config.get("end_date")
        if end_date:
            end_date = parse_date(end_date).replace(tzinfo=timezone)
        else:
            # Start of today
            end_date = datetime.now(tz=timezone).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

        start_date = config.get("start_date")
        if start_date:
            start_date = parse_date(start_date).replace(tzinfo=timezone)
        else:
            start_date = end_date - timedelta(days=interval_days)

        title = config.get("title", "Status report")
        theme = Theme(**config.get("theme", {}))

        self.report = Report(
            title=title,
            interval_days=interval_days,
            start_date=start_date,
            end_date=end_date,
            timezone=timezone,
            theme=theme,
        )
        self.dm = DatasourceManager(self.report, datasource_conf)
        self.vm = ViewManager(self.dm, self.report, view_conf)
        self.odm = OutputDriverManager(self.report, output_conf)
        self.env = make_jinja_environment(theme)

        self.license = License(config.get("license_key"))
        self.env.globals["print_license"] = self.license.render

    def create(self):
        """Render all Views in the report and output using the output driver.

        .. important::

           This will send the report using all configured output drivers!
           Disable any output drivers you don't wish to send to during testing.

        """
        for id, output_driver in self.odm.instances:
            LOG.info(f"Sending report via output driver {id}")
            content = Content(self.env, self.report)
            for fmt in self.supported_formats:
                self.env.globals["print_license"] = partial(self.license.render, fmt)
                views = self.vm.render(self.env, fmt, output_driver)
                content.add_format(fmt, views)
            if not self.license.rendered:
                raise ValueError("Template is missing `{{ print_license() }}` call")
            output_driver.render_output(content, self.vm.blobs)

from datetime import datetime, timedelta
from jinja2 import TemplateNotFound
from slugify import slugify

from kpireport.datasource import DatasourceManager
from kpireport.output import OutputDriverManager
from kpireport.view import ViewManager
from kpireport.utils import create_jinja_environment
from kpireport.version import VERSION

import logging

LOG = logging.getLogger(__name__)


class Theme:
    """The theme"""

    def __init__(self, num_columns=6):
        self.num_columns = num_columns


class Report:
    """The report object."""

    version = VERSION

    def __init__(
        self, title=None, interval_days=None, start_date=None, end_date=None, theme=None
    ):
        self.title = title
        self.interval_days = interval_days
        self.start_date = start_date
        self.end_date = end_date
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
    """Contents"""

    def __init__(self, j2: "Environment", report: "Report"):
        self.j2 = j2
        self.report = report
        self._formats = {}

    def add_format(self, fmt: str, views: "list[View]"):
        try:
            template = self.j2.get_template(f"layout/default.{fmt}")
        except TemplateNotFound:
            LOG.warning(
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

    def get_views(self, fmt: str) -> "list[kpireport.view.View]":
        """Get the rendered views for the given format.

        Args:
            fmt (str): the desired output format.

        Returns:
            List[View]: the list of Views rendered under that format.
        """
        return self._formats.get(fmt, {}).get("views", [])


class ReportFactory:
    supported_formats = ["html", "md", "slack"]

    def __init__(self, config):
        datasource_conf = config.get("datasources", {})
        view_conf = config.get("views", {})
        output_conf = config.get("outputs", {})

        interval_days = config.get("interval_days", 7)
        end_date = config.get("end_date", datetime.now())
        start_date = config.get("start_date", end_date - timedelta(days=interval_days))

        theme = Theme()
        title = config.get("title", "Status report")

        self.report = Report(
            title=title,
            interval_days=interval_days,
            start_date=start_date,
            end_date=end_date,
            theme=theme,
        )
        self.dm = DatasourceManager(self.report, datasource_conf)
        self.vm = ViewManager(self.dm, self.report, view_conf)
        self.odm = OutputDriverManager(self.report, output_conf)
        self.env = create_jinja_environment()

    def create(self):
        for id, output_driver in self.odm.instances:
            LOG.info(f"Sending report via output driver {id}")
            content = Content(self.env, self.report)
            for fmt in self.supported_formats:
                views = self.vm.render(self.env, fmt, output_driver)
                content.add_format(fmt, views)
            output_driver.render_output(content, self.vm.blobs)

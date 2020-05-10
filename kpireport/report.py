from datetime import datetime, timedelta
from slugify import slugify

from kpireport.datasource import DatasourceManager
from kpireport.output import OutputDriverManager
from kpireport.view import ViewManager
from kpireport.utils import create_jinja_environment
from kpireport.version import VERSION

import logging
LOG = logging.getLogger(__name__)


class Theme:
    """The theme
    """
    def __init__(self, num_columns=6):
        self.num_columns = num_columns


class Report:
    """The report object.
    """
    version = VERSION

    def __init__(self, title=None, interval_days=None,
                 start_date=None, end_date=None, theme=None):
        self.title = title
        self.interval_days = interval_days
        self.start_date = start_date
        self.end_date = end_date
        self.title_slug = slugify(self.title)
        self.id = "_".join([
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d'),
            self.title_slug
        ])

        if theme:
            self.theme = theme
        else:
            self.theme = Theme()

    @property
    def timedelta(self):
        return self.end_date - self.start_date


class ReportFactory:
    supported_formats = ["html", "md"]

    def __init__(self, config):
        datasource_conf = config.get("datasources", {})
        view_conf = config.get("views", {})
        output_conf = config.get("outputs", {})

        interval_days = config.get("interval_days", 7)
        end_date = config.get("end_date", datetime.now())
        start_date = config.get("start_date",
                                end_date - timedelta(days=interval_days))

        theme = Theme()
        title = config.get("title", "Status report")

        self.report = Report(title=title, interval_days=interval_days,
                             start_date=start_date, end_date=end_date,
                             theme=theme)
        self.dm = DatasourceManager(self.report, datasource_conf)
        self.vm = ViewManager(self.dm, self.report, view_conf)
        self.odm = OutputDriverManager(self.report, output_conf)
        self.env = create_jinja_environment()

    def create(self):
        for id, output_driver in self.odm.instances:
            LOG.info(f"Sending report via output driver {id}")
            content = {}
            for fmt in self.supported_formats:
                views = self.vm.render(self.env, fmt, output_driver)
                template = self.env.get_template(f"layout/default.{fmt}")
                content[fmt] = template.render(views=views,
                                               report=self.report)
                # Also store a list of the raw views to allow the output
                # driver to render its own output structure
                content[f"{fmt}_views"] = views
            output_driver.render_output(content, self.vm.blobs)
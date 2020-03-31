from datetime import datetime, timedelta

from reportcard.datasource import DatasourceManager
from reportcard.output import OutputDriverManager
from reportcard.view import ViewManager
from reportcard.utils import create_jinja_environment

import logging
LOG = logging.getLogger(__name__)


class Theme:
    def __init__(self, num_columns=6):
        self.num_columns = num_columns


class Report:
    def __init__(self, title=None, start_date=None, end_date=None,
                 theme=Theme()):
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        self.theme = theme


class ReportFactory:
    def __init__(self, config):
        datasource_conf = config.get("datasources", {})
        view_conf = config.get("views", {})
        output_conf = config.get("outputs", {})

        interval = config.get("interval_days", 7)
        end_date = config.get("end_date", datetime.now())
        start_date = config.get("start_date",
                                end_date - timedelta(days=interval))

        theme = Theme()
        title = config.get("title", "Status report")

        self.report = Report(title=title,
                             start_date=start_date, end_date=end_date,
                             theme=theme)
        self.dm = DatasourceManager(self.report, datasource_conf)
        self.vm = ViewManager(self.dm, self.report, view_conf)
        self.odm = OutputDriverManager(self.report, output_conf)
        self.env = create_jinja_environment()

    def create(self):
        for id, output_driver in self.odm.instances:
            LOG.info(f"Sending report via output driver {id}")
            views = self.vm.render(self.env, output_driver)
            template = self.env.get_template("layout/default.html")
            content = template.render(views=views, report=self.report)
            output_driver.render_output(content, self.vm.blobs)

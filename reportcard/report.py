from datetime import datetime, timedelta
from jinja2 import Environment, PackageLoader

from reportcard.datasource import DatasourceManager
from reportcard.output import OutputDriverManager
from reportcard.view import ViewManager
from reportcard.utils import module_root

import logging
LOG = logging.getLogger(__name__)


DEFAULT_OUTPUT_CONFIG = {}


class Report:
    def __init__(self, start_date=None, end_date=None, theme=None):
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

        report = Report(start_date=start_date, end_date=end_date)
        self.dm = DatasourceManager(report, datasource_conf)
        self.vm = ViewManager(self.dm, report, view_conf)
        self.odm = OutputDriverManager(report, output_conf)

        self.env = Environment(
            loader=PackageLoader(module_root(self.__module__)),
            autoescape=True
        )

    def create(self):
        for id, output_driver in self.odm.instances:
            LOG.info(f"Sending report via output driver {id}")
            views = self.vm.render(self.env, output_driver)
            template = self.env.get_template("layout/default.html")
            content = template.render(views=views)
            output_driver.render_output(content, self.vm.blobs)

from datetime import datetime, timedelta

from reportcard.datasource import DatasourceManager
from reportcard.view import ViewManager


class Report:
    def __init__(self, start_date=None, end_date=None, theme=None):
        self.start_date = start_date
        self.end_date = end_date
        self.theme = theme


class ReportFactory:
    def __init__(self, config):
        datasource_conf = config.get("datasources", {})
        view_conf = config.get("views", [])

        interval = config.get("interval_days", 7)
        end_date = config.get("end_date", datetime.now())
        start_date = config.get("start_date",
                                end_date - timedelta(days=interval))
        report = Report(start_date=start_date, end_date=end_date)

        self.dm = DatasourceManager(report, datasource_conf)
        self.vm = ViewManager(self.dm, report, view_conf)

    def create(self):
        return self.vm.render()
